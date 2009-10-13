"""Models for emencia.django.newsletter"""
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from tagging.fields import TagField

class SMTPServer(models.Model):
    """Configuration of a SMTP server"""

    name = models.CharField(_('name'), max_length=30)
    host = models.CharField(_('server host'), max_length=255)
    user = models.CharField(_('server user'), max_length=128, blank=True,
                            help_text=_('Leave it empty if the host is public.'))
    password = models.CharField(_('server password'), max_length=128, blank=True,
                                help_text=_('Leave it empty if not necessary.'))
    port = models.IntegerField(_('server port'), default=25)
    tls = models.BooleanField(_('server use TLS'))

    mails_hour = models.IntegerField(_('mails per hour'), default=0)

    # Add a connection test method

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
    invalid = models.BooleanField(_('invalid'), default=False)
    tags = TagField(_('tags'))

    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def mail_format(self):
        if self.first_name and self.last_name:
            return '%s, %s <%s>' % (self.last_name, self.first_name, self.email)
        return self.email
    mail_format.short_description = _('mail format')

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
    contacts = models.ManyToManyField(Contact, verbose_name=_('contacts'))

    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def contacts_length(self):
        return self.contacts.all().count()
    contacts_length.short_description = _('contacts length')

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
    DEFAULT_HEADER = 'Emencia Newsletter<noreply@emencia.com>'

    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (WAITING, _('waiting sending')),
                      (SENDING, _('sending')),
                      (SENT, _('sent')),)

    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    
    mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'))
    test_contacts = models.ManyToManyField(Contact, verbose_name=_('test contacts'),
                                           blank=True, null=True)

    server = models.ForeignKey(SMTPServer, verbose_name=_('smtp server'),
                               default=1)
    header_sender = models.CharField(_('sender'), max_length=250,
                                     default=DEFAULT_HEADER)
    header_reply = models.CharField(_('reply to'), max_length=250,
                                    default=DEFAULT_HEADER)

    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=DRAFT)
    sending_date = models.DateTimeField(_('sending date'), default=datetime.now)
    
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)

    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('creation_date',)
        verbose_name = _('Newsletter')
        verbose_name_plural = _('Newsletters')


class ContactMailingStatus(models.Model):
    """Status of the reception"""
    SENT = 0
    ERROR = 1
    INVALID = 2
    OPENED = 4
    
    STATUS_CHOICES = ((SENT, _('sent')),
                      (ERROR, _('error')),
                      (INVALID, _('invalid email')),
                      (OPENED, _('opened')),)
    
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

        
