"""Mailer for emencia.django.newsletter"""
import re
import sys
import logging
import time
import mimetypes
from random import sample
from StringIO import StringIO
from smtplib import SMTPRecipientsRefused
from datetime import datetime
import time
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.Encoders import encode_base64
    from email.mime.MIMEAudio import MIMEAudio
    from email.mime.MIMEBase import MIMEBase
    from email.mime.MIMEImage import MIMEImage
except ImportError:  # Python 2.4 compatibility
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.Encoders import encode_base64
    from email.MIMEAudio import MIMEAudio
    from email.MIMEBase import MIMEBase
    from email.MIMEImage import MIMEImage
from email import message_from_file
from html2text import html2text as html2text_orig
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.encoding import smart_unicode

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils.tokens import tokenize
from emencia.django.newsletter.utils.newsletter import track_links
from emencia.django.newsletter.utils.newsletter import body_insertion
from emencia.django.newsletter.settings import TRACKING_LINKS
from emencia.django.newsletter.settings import TRACKING_IMAGE
from emencia.django.newsletter.settings import TRACKING_IMAGE_FORMAT
from emencia.django.newsletter.settings import UNIQUE_KEY_LENGTH
from emencia.django.newsletter.settings import UNIQUE_KEY_CHAR_SET
from emencia.django.newsletter.settings import INCLUDE_UNSUBSCRIPTION
from emencia.django.newsletter.settings import SLEEP_BETWEEN_SENDING
from emencia.django.newsletter.settings import \
     RESTART_CONNECTION_BETWEEN_SENDING


LINK_RE = re.compile(r"https?://([^ \n]+\n)+[^ \n]+", re.MULTILINE)
logger = logging.getLogger('emencia.django.newsletter')
def html2text(html):
    """Use html2text but repair newlines cutting urls.
    Need to use this hack until
    https://github.com/aaronsw/html2text/issues/#issue/7 is not fixed"""
    txt = html2text_orig(html)
    links = list(LINK_RE.finditer(txt))
    out = StringIO()
    pos = 0
    for l in links:
        out.write(txt[pos:l.start()])
        out.write(l.group().replace('\n', ''))
        pos = l.end()
    out.write(txt[pos:])
    return out.getvalue()


class Mailer(object):
    """Mailer for generating and sending newsletters
    In test mode the mailer always send mails but do not log it"""
    smtp = None

    def __init__(self, newsletter, test=False, verbose=0):
        self.test = test
        self.verbose = verbose
        self.newsletter = newsletter
        self.expedition_list = self.get_expedition_list()
        self.newsletter_template = Template(self.newsletter.content)
        self.title_template = Template(self.newsletter.title)

    def run(self):
        """Send the mails"""
        if not self.can_send:
            return

        if not self.smtp:
            self.smtp_connect()

        self.attachments = self.build_attachments()
        per_hour = self.newsletter.server.mails_hour
        sleep_time = 60.0 * 60 / per_hour

        number_of_recipients = len(self.expedition_list)
        if self.verbose:
            print '%i emails will be sent up to %s/hour at one every %s seconds.' % (number_of_recipients, per_hour, round(sleep_time, 2))

        i = 1
        critical_errors = 0
        for contact in self.expedition_list:
            if self.verbose:
                print '- Processing %s/%s (%s - %s)' % (
                    i, number_of_recipients, contact.pk, contact)

            try:
                message = self.build_message(contact)
                self.smtp.sendmail(smart_str(self.newsletter.header_sender),
                                   contact.email,
                                   message.as_string())
                status = self.test and ContactMailingStatus.SENT_TEST \
                         or ContactMailingStatus.SENT
            except (UnicodeError, SMTPRecipientsRefused):
                status = ContactMailingStatus.INVALID
                contact.valid = False
                contact.save()
            except:
                e = sys.exc_info()[1]
                logger.error('Sending to %s failed: \n%s' % (contact, e))
                status = ContactMailingStatus.ERROR
                critical_errors += 1

            ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                                contact=contact, status=status)

            # exit if to many critical erros
            if critical_errors >= 3:
                logger.error('Max 3 critical errors reached, aborting this batch and will attempt again on next cron call (if it was setup)')
                break

            if SLEEP_BETWEEN_SENDING:
                time.sleep(SLEEP_BETWEEN_SENDING)
            else:
                time.sleep(sleep_time)
            if RESTART_CONNECTION_BETWEEN_SENDING:
                self.smtp.quit()
                self.smtp_connect()
            i += 1

        self.smtp.quit()
        self.update_newsletter_status()

    def build_message(self, contact):
        """
        Build the email as a multipart message containing
        a multipart alternative for text (plain, HTML) plus
        all the attached files.
        """
        content_html = self.build_email_content(contact)
        content_text = html2text(content_html)

        message = MIMEMultipart()

        message['Subject'] = self.build_title_content(contact)
        message['From'] = smart_str(self.newsletter.header_sender)
        message['Reply-to'] = smart_str(self.newsletter.header_reply)
        message['To'] = contact.mail_format()

        message_alt = MIMEMultipart('alternative')
        message_alt.attach(MIMEText(smart_str(content_text), 'plain', 'UTF-8'))
        message_alt.attach(MIMEText(smart_str(content_html), 'html', 'UTF-8'))
        message.attach(message_alt)

        for attachment in self.attachments:
            message.attach(attachment)

        for header, value in self.newsletter.server.custom_headers.items():
            message[header] = value

        return message

    def build_attachments(self):
        """Build email's attachment messages"""
        attachments = []

        for attachment in self.newsletter.attachment_set.all():
            ctype, encoding = mimetypes.guess_type(attachment.file_attachment.path)

            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)

            fd = open(attachment.file_attachment.path, 'rb')
            if maintype == 'text':
                message_attachment = MIMEText(fd.read(), _subtype=subtype)
            elif maintype == 'message':
                message_attachment = message_from_file(fd)
            elif maintype == 'image':
                message_attachment = MIMEImage(fd.read(), _subtype=subtype)
            elif maintype == 'audio':
                message_attachment = MIMEAudio(fd.read(), _subtype=subtype)
            else:
                message_attachment = MIMEBase(maintype, subtype)
                message_attachment.set_payload(fd.read())
                encode_base64(message_attachment)
            fd.close()
            message_attachment.add_header('Content-Disposition', 'attachment',
                                          filename=attachment.title)
            attachments.append(message_attachment)

        return attachments

    def smtp_connect(self):
        """Make a connection to the SMTP"""
        self.smtp = self.newsletter.server.connect()

    def get_expedition_list(self):
        """Build the expedition list"""
        credits = self.newsletter.server.credits()
        if self.test:
            return self.newsletter.test_contacts.all()[:credits]

        already_sent = ContactMailingStatus.objects.filter(status=ContactMailingStatus.SENT,
                                                           newsletter=self.newsletter).values_list('contact__id', flat=True)
        expedition_list = self.newsletter.mailing_list.expedition_set().exclude(id__in=already_sent)
        return expedition_list[:credits]

    def build_title_content(self, contact):
        """Generate the email title for a contact"""
        context = Context({'contact': contact,
                           'UNIQUE_KEY': ''.join(sample(UNIQUE_KEY_CHAR_SET,
                                                        UNIQUE_KEY_LENGTH))})
        title = self.title_template.render(context)
        return title

    def build_email_content(self, contact):
        """Generate the mail for a contact"""
        uidb36, token = tokenize(contact)
        context = Context({'contact': contact,
                           'domain': Site.objects.get_current().domain,
                           'newsletter': self.newsletter,
                           'tracking_image_format': TRACKING_IMAGE_FORMAT,
                           'uidb36': uidb36, 'token': token})
        content = self.newsletter_template.render(context)
        if TRACKING_LINKS:
            content = track_links(content, context)
        link_site = render_to_string('newsletter/newsletter_link_site.html', context)
        content = body_insertion(content, link_site)

        if INCLUDE_UNSUBSCRIPTION:
            unsubscription = render_to_string('newsletter/newsletter_link_unsubscribe.html', context)
            content = body_insertion(content, unsubscription, end=True)
        if TRACKING_IMAGE:
            image_tracking = render_to_string('newsletter/newsletter_image_tracking.html', context)
            content = body_insertion(content, image_tracking, end=True)
        return smart_unicode(content)

    def update_newsletter_status(self):
        """Update the status of the newsletter"""
        if self.test:
            return

        if self.newsletter.status == Newsletter.WAITING:
            self.newsletter.status = Newsletter.SENDING
        if self.newsletter.status == Newsletter.SENDING and \
               self.newsletter.mails_sent() >= \
               self.newsletter.mailing_list.expedition_set().count():
            self.newsletter.status = Newsletter.SENT
        self.newsletter.save()

    @property
    def can_send(self):
        """Check if the newsletter can be sent"""
        if self.newsletter.server.credits() <= 0:
            return False

        if self.test:
            return True

        if self.newsletter.sending_date <= datetime.now() and \
               (self.newsletter.status == Newsletter.WAITING or \
                self.newsletter.status == Newsletter.SENDING):
            return True

        return False
