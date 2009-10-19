"""Admin for emencia.django.newsletter"""
from datetime import datetime

from django.contrib import admin
from django.conf.urls.defaults import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.db.models import Q

from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils import get_webpage_content

class SMTPServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'user', 'tls', 'mails_hour',)# 'check_connection')
    list_filter = ('tls',)
    search_fields = ('name', 'host', 'user',)
    fieldsets = ((None, {'fields': ('name',),}),
                 (_('Configuration'), {'fields': ('host', 'port',
                                                  'user', 'password', 'tls'),}),
                 (_('Miscellaneous'), {'fields': ('mails_hour',),}),
                 )
    actions = ['check_connections']
    actions_on_top = False
    actions_on_bottom = True

    def check_connections(self, request, queryset):
        message = '%s connection %s'
        for server in queryset:            
            status = server.connection_valid() and 'OK' or 'KO'
            self.message_user(request, message % (server.__unicode__(), status))
    
admin.site.register(SMTPServer, SMTPServerAdmin)

class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('email', 'first_name', 'last_name', 'tags', 'subscriber',
                    'valid', 'total_subscriptions', 'creation_date', 'related_object_admin')
    list_filter = ('subscriber', 'valid', 'creation_date', 'modification_date')
    search_fields = ('email', 'first_name', 'last_name', 'tags')
    fieldsets = ((None, {'fields': ('email', 'first_name', 'last_name')}),
                 (None, {'fields': ('tags',)}),
                 (_('Status'), {'fields': ('subscriber', 'valid')}),
                 (_('Advanced'), {'fields': ('object_id', 'content_type'),
                                  'classes': ('collapse',)}),
                 )
    actions = ['create_mailinglist',]
    actions_on_top = False
    actions_on_bottom = True

    def total_subscriptions(self, contact):
        subscriptions = contact.subscriptions().count()
        unsubscriptions = contact.unsubscriptions().count()
        return '%s / %s' % (subscriptions - unsubscriptions, subscriptions)
    total_subscriptions.short_description = _('Total subscriptions')

    def create_mailinglist(self, request, queryset):
        when = str(datetime.now()).split('.')[0]
        new_mailing = MailingList(name=_('New mailinglist at %s') % when, 
                                  description=_('New mailing list created in admin at %s') % when)
        new_mailing.save()
        new_mailing.subscribers = queryset.all()
        
        self.message_user(request, _('%s succesfully created.') % new_mailing)
        
    create_mailinglist.short_description = _('Create a mailinglist')
        

admin.site.register(Contact, ContactAdmin)

class MailingListAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('name', 'description',
                    'subscribers_count', 'unsubscribers_count',
                    'creation_date', 'modification_date')    
    list_filter = ('creation_date', 'modification_date')
    search_fields = ('name', 'description',)
    filter_horizontal = ['subscribers', 'unsubscribers']
    fieldsets = ((None, {'fields': ('name', 'description',)}),
                 (None, {'fields': ('subscribers',)}),
                 (None, {'fields': ('unsubscribers',)}),
                 )
    actions = ['merge_mailinglist',]
    actions_on_top = False
    actions_on_bottom = True

    def merge_mailinglist(self, request, queryset):
        if queryset.count() == 1:
            self.message_user(request, _('Please select a least 2 mailing list.'))
            return None
        
        contacts = {}
        for ml in queryset:
            for contact in ml.subscribers.all():
                contacts[contact] = ''

        when = str(datetime.now()).split('.')[0]
        new_mailing = MailingList(name=_('Merging list at %s') % when, 
                                  description=_('Mailing list created by merging at %s') % when)
        new_mailing.save()
        new_mailing.subscribers = contacts.keys()
        
        self.message_user(request, _('%s succesfully created by merging.') % new_mailing)
        
    merge_mailinglist.short_description = _('Merge selected mailinglists')
    

admin.site.register(MailingList, MailingListAdmin)


class NewsletterAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('title', 'mailing_list', 'server', 'status',
                    'sending_date', 'creation_date', 'modification_date', 'stats_link')
    list_filter = ('mailing_list', 'server', 'status', 'sending_date',
                   'creation_date', 'modification_date')
    search_fields = ('title', 'content', 'header_sender', 'header_reply')
    filter_horizontal = ['test_contacts']
    fieldsets = ((None, {'fields': ('title', 'content',)}),
                 (_('Receivers'), {'fields': ('mailing_list', 'test_contacts',)}),
                 (_('Sending'), {'fields': ('sending_date', 'status',)}),
                 (_('Miscellaneous'), {'fields': ('server', 'header_sender',
                                                  'header_reply', 'slug'),
                                       'classes': ('collapse',)}),                 
                 )
    prepopulated_fields = {'slug': ('title',)}
    actions = ['send_mail_test', 'make_ready_to_send', 'make_cancel_sending']
    actions_on_top = False
    actions_on_bottom = True

    def stats_link(self, newsletter):
        return '<a href="%s">%s</a>' % (newsletter.get_stats_url(), _('View stats'))
    stats_link.allow_tags = True
    stats_link.short_description = _('Statistics')

    def save_model(self, request, newsletter, form, change):
        if newsletter.content.startswith('http://'):
            newsletter.content = get_webpage_content(newsletter.content)
        
        newsletter.save()
        
    def send_mail_test(self, request, queryset):
        for newsletter in queryset:
            mailer = Mailer(newsletter, test=True)
            mailer.run()
            self.message_user(request, _('%s succesfully sent.') % newsletter)
    send_mail_test.short_description = _('Send test email')

    def make_ready_to_send(self, request, queryset):
        queryset = queryset.filter(status=Newsletter.DRAFT)
        for newsletter in queryset:
            newsletter.status = Newsletter.WAITING
            newsletter.save()
        self.message_user(request, _('%s newletters are ready to send') % queryset.count())
    make_ready_to_send.short_description = _('Make ready to send')

    def make_cancel_sending(self, request, queryset):
        queryset = queryset.filter(Q(status=Newsletter.WAITING) |
                                   Q(status=Newsletter.SENDING))
        for newsletter in queryset:
            newsletter.status = Newsletter.CANCELED
            newsletter.save()
        self.message_user(request, _('%s newletters are cancelled') % queryset.count())
    make_cancel_sending.short_description = _('Cancel the sending')

    def stats(self, request, slug):
        """Display stats of a newsletters"""
        opts = self.model._meta
        newsletter = get_object_or_404(Newsletter, slug=slug)
        
        context = {'title': _('Stats %s') % newsletter.__unicode__(),
                   'original': newsletter,
                   'opts': opts,
                   'object_id': newsletter.pk,
                   'root_path': self.admin_site.root_path,
                   'app_label': opts.app_label,}
        return render_to_response('newsletter/newsletter_stats.html',
                                  context,
                                  context_instance=RequestContext(request))

    def get_urls(self):
        urls = super(NewsletterAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^stats/(?P<slug>[-\w]+)/$', self.stats,
                               name='newsletter_newsletter_stats'),
                           )
        return my_urls + urls

admin.site.register(Newsletter, NewsletterAdmin)

#admin.site.register(ContactMailingStatus)

