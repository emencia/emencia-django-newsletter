"""Models for emencia.django.newsletter"""
from smtplib import SMTP
from datetime import datetime
from datetime import timedelta

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from emencia.django.newsletter.settings import DEFAULT_HEADER_REPLY
from emencia.django.newsletter.settings import DEFAULT_HEADER_SENDER


class SMTPServer(models.Model):
    """Configuration of a SMTP server"""

    name = models.CharField(_('name'), max_length=30)
    host = models.CharField(_('server host'), max_length=255)
    user = models.CharField(_('server user'), max_length=128, blank=True,
                            help_text=_('Leave it empty if the host is public.'))
    password = models.CharField(_('server password'), max_length=128, blank=True,
                                help_text=_('Leave it empty if the host is public.'))
    port = models.IntegerField(_('server port'), default=25)
    tls = models.BooleanField(_('server use TLS'))

    mails_hour = models.IntegerField(_('mails per hour'), default=0)

    def connection_valid(self):
        """Check if the server can be connected"""
        try:            
            smtp = SMTP(self.host, self.port)
            if self.user or self.password:
                smtp.login(self.user, self.password)
            if self.tls:
                smtp.starttls()
            smtp.quit()
        except:
            return False
        return True
    connection_valid.short_description = _('Connection valid')

    def credits(self):
        """Return how many mails the server can send"""
        if not self.mails_hour:
            return 1000 # Arbitrary value

        last_hour = datetime.now() - timedelta(hours=1)
        sent_last_hour = ContactMailingStatus.objects.filter(
            models.Q(status=ContactMailingStatus.SENT) |
            models.Q(status=ContactMailingStatus.SENT_TEST),
            newsletter__server=self,
            creation_date__gte=last_hour).count()
        return self.mails_hour - sent_last_hour

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.host)

    class Meta:
        verbose_name = _('SMTP Server')
        verbose_name_plural = _('SMTP Servers')


class Contact(models.Model):
    """Contact for emailing"""
    
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    subscriber = models.BooleanField(_('subscriber'), default=True)
    valid = models.BooleanField(_('valid email'), default=True)
    tags = TagField(_('tags'))

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def related_object_admin(self):
        if self.content_type and self.object_id:
            admin_url = reverse('admin:%s_%s_change' % (self.content_type.app_label,
                                                        self.content_type.model),
                                args=(self.object_id,))
            return '%s: <a href="%s">%s</a>' % (self.content_type.model.capitalize(),
                                                admin_url,
                                                self.content_object.__unicode__())
        return _('No relative object')
    related_object_admin.allow_tags = True
    related_object_admin.short_description = _('Related object')

    def subscriptions(self):
        """Return the user subscriptions"""
        return MailingList.objects.filter(subscribers=self)

    def unsubscriptions(self):
        """Return the user unsubscriptions"""
        return MailingList.objects.filter(unsubscribers=self)

    def mail_format(self):
        if self.first_name and self.last_name:
            return '%s %s <%s>' % (self.last_name, self.first_name, self.email)
        return self.email
    mail_format.short_description = _('mail format')

    def get_absolute_url(self):
        if self.content_type and self.object_id:
            return self.content_object.get_absolute_url()
        return reverse('admin:newsletter_contact_change', args=(self.pk,))
    
    def __unicode__(self):
        if self.first_name and self.last_name:
            return '%s %s | %s' % (self.last_name, self.first_name, self.tags)
        return '%s | %s' % (self.email, self.tags)

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        
class MailingList(models.Model):
    """Mailing list"""
    
    name = models.CharField(_('name'), max_length=30)
    description = models.TextField(_('description'), blank=True)
    
    subscribers = models.ManyToManyField(Contact, verbose_name=_('subscribers'),
                                         related_name='mailinglist_subscriber')
    unsubscribers = models.ManyToManyField(Contact, verbose_name=_('unsubscribers'),
                                           related_name='mailinglist_unsubscriber',
                                           null=True, blank=True)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def subscribers_count(self):
        return self.subscribers.all().count()
    subscribers_count.short_description = _('subscribers')

    def unsubscribers_count(self):
        return self.unsubscribers.all().count()
    unsubscribers_count.short_description = _('unsubscribers')

    def expedition_set(self):
        unsubscribers_id = self.unsubscribers.values_list('id', flat=True)
        return self.subscribers.filter(subscriber=True, valid=True).exclude(
            id__in=unsubscribers_id)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('Mailing List')
        verbose_name_plural = _('Mailing Lists')


class Newsletter(models.Model):
    """Newsletter to be sended to contacts"""
    DRAFT  = 0
    WAITING  = 1
    SENDING = 2
    SENT = 4
    CANCELED = 5

    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (WAITING, _('waiting sending')),
                      (SENDING, _('sending')),
                      (SENT, _('sent')),
                      (CANCELED, _('canceled')),
                      )

    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'), help_text=_('Or paste an URL.'))
    
    mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'))
    test_contacts = models.ManyToManyField(Contact, verbose_name=_('test contacts'),
                                           blank=True, null=True)

    server = models.ForeignKey(SMTPServer, verbose_name=_('smtp server'),
                               default=1)
    header_sender = models.CharField(_('sender'), max_length=250,
                                     default=DEFAULT_HEADER_SENDER)
    header_reply = models.CharField(_('reply to'), max_length=250,
                                    default=DEFAULT_HEADER_REPLY)

    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT)
    sending_date = models.DateTimeField(_('sending date'), default=datetime.now)

    slug = models.SlugField(help_text=_('Used for displaying the newsletter on the site.'))
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def mails_sent(self):
        return self.contactmailingstatus_set.filter(status=ContactMailingStatus.SENT).count()

    @models.permalink
    def get_absolute_url(self):
        return ('newsletter_newsletter_preview', (self.slug,))

    @models.permalink
    def get_stats_url(self):
        return ('admin:newsletter_newsletter_stats', (self.slug,))

    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('Newsletter')
        verbose_name_plural = _('Newsletters')


class ContactMailingStatus(models.Model):
    """Status of the reception"""
    SENT_TEST = -1
    SENT = 0
    ERROR = 1
    INVALID = 2
    OPENED = 4
    OPENED_ON_SITE = 5
    
    STATUS_CHOICES = ((SENT_TEST, _('sent in test')),
                      (SENT, _('sent')),
                      (ERROR, _('error')),
                      (INVALID, _('invalid email')),
                      (OPENED, _('opened')),
                      (OPENED_ON_SITE, _('opened on site')),
                      )
    
    newsletter = models.ForeignKey(Newsletter, verbose_name=_('newsletter'))
    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES)

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)

    def __unicode__(self):
        return '%s : %s : %s' % (self.newsletter.__unicode__(),
                                 self.contact.__unicode__(),
                                 self.get_status_display())

    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('Contact Mailing Status')
        verbose_name_plural = _('Contact Mailing Status')

        
