"""Admin for emencia.django.newsletter"""
from datetime import datetime

from django.contrib import admin
from django.utils.translation import ugettext as _

from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils import get_webpage_body

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
        for server in queryset:            
            message = server.connection_valid() and '%s connection OK' or '%s connection KO'
            self.message_user(request, message % server.__unicode__())
    
admin.site.register(SMTPServer, SMTPServerAdmin)

class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('email', 'first_name', 'last_name', 'tags', 'subscriber',
                    'invalid', 'total_subscriptions', 'creation_date', 'related_object_admin')
    list_filter = ('subscriber', 'invalid', 'creation_date', 'modification_date')
    search_fields = ('email', 'first_name', 'last_name', 'tags')
    fieldsets = ((None, {'fields': ('email', 'first_name', 'last_name')}),
                 (None, {'fields': ('tags',)}),
                 (_('Status'), {'fields': ('subscriber', 'invalid')}),
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
                    'sending_date', 'creation_date', 'modification_date')
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
    actions_on_top = False
    actions_on_bottom = False

    def save_model(self, request, newsletter, form, change):
        if newsletter.content.startswith('http://'):
            newsletter.content = get_webpage_body(newsletter.content)
        
        newsletter.save()

admin.site.register(Newsletter, NewsletterAdmin)

#admin.site.register(ContactMailingStatus)

