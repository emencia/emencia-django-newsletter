"""Mailer for emencia.django.newsletter"""
from smtplib import SMTP
from smtplib import SMTPRecipientsRefused
from datetime import datetime
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
except ImportError :  # Python 2.4 compatibility
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText


from html2text import html2text
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils.tokens import tokenize
from emencia.django.newsletter.utils.newsletter import track_links
from emencia.django.newsletter.utils.newsletter import body_insertion
from emencia.django.newsletter.settings import TRACKING_LINKS
from emencia.django.newsletter.settings import TRACKING_IMAGE
from emencia.django.newsletter.settings import INCLUDE_UNSUBSCRIPTION


class Mailer(object):
    """Mailer for generating and sending newsletters
    In test mode the mailer always send mails but do not log it"""
    smtp = None

    def __init__(self, newsletter, test=False):
        self.test = test
        self.newsletter = newsletter
        self.expedition_list = self.get_expedition_list()
        self.newsletter_template = Template(self.newsletter.content)

    def run(self):
        """Send the mails"""
        if self.can_send:
            if not self.smtp:
                self.smtp_connect()

            for contact in self.expedition_list:
                message = self.build_message(contact)
                try:
                    self.smtp.sendmail(self.newsletter.header_sender,
                                                 contact.email,
                                                 message.as_string())
                    status = self.test and ContactMailingStatus.SENT_TEST or ContactMailingStatus.SENT
                except SMTPRecipientsRefused, e:
                    status = ContactMailingStatus.INVALID
                except:
                    status = ContactMailingStatus.ERROR

                ContactMailingStatus.objects.create(newsletter=self.newsletter,
                                                    contact=contact, status=status)
            self.smtp.quit()
            self.update_newsletter_status()

    def build_message(self, contact):
        """Build the email"""
        content_html = self.build_email_content(contact)
        content_text = html2text(content_html)

        message = MIMEMultipart('alternative')
        message['Subject'] = self.newsletter.title
        message['From'] = self.newsletter.header_sender
        message['Reply-to'] = self.newsletter.header_reply
        message['To'] = contact.mail_format()

        for header, value in self.newsletter.server.custom_headers.items():
            message[header] = value

        message.attach(MIMEText(content_text, 'plain', 'UTF-8'))
        message.attach(MIMEText(content_html, 'html', 'UTF-8'))

        return message

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

    def build_email_content(self, contact):
        """Generate the mail for a contact"""
        uidb36, token = tokenize(contact)
        context = Context({'contact': contact,
                           'domain': Site.objects.get_current().domain,
                           'newsletter': self.newsletter,
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
           self.newsletter.mails_sent() >= self.expedition_list.count():
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

