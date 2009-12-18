"""Admin for emencia.django.newsletter"""
from datetime import datetime
from HTMLParser import HTMLParseError

from django.contrib import admin
from django.conf import settings
from django.conf.urls.defaults import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.db.models import Q

from emencia.django.newsletter.models import Link
from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils import get_webpage_content
from emencia.django.newsletter.vcard import vcard_contacts_export_response

class SMTPServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'user', 'tls', 'mails_hour',)# 'check_connection')
    list_filter = ('tls',)
    search_fields = ('name', 'host', 'user',)
    fieldsets = ((None, {'fields': ('name',),}),
                 (_('Configuration'), {'fields': ('host', 'port',
                                                  'user', 'password', 'tls'),}),
                 (_('Miscellaneous'), {'fields': ('mails_hour', 'headers'),
                                       'classes': ('collapse',)}),
                 )
    actions = ['check_connections']
    actions_on_top = False
    actions_on_bottom = True

    def check_connections(self, request, queryset):
        """Check the SMTP connection"""
        message = '%s connection %s'
        for server in queryset:
            status = server.connection_valid() and 'OK' or 'KO'
            self.message_user(request, message % (server.__unicode__(), status))

admin.site.register(SMTPServer, SMTPServerAdmin)

class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('email', 'first_name', 'last_name', 'tags', 'tester', 'subscriber',
                    'valid', 'total_subscriptions', 'creation_date', 'related_object_admin')
    list_filter = ('subscriber', 'valid', 'tester', 'creation_date', 'modification_date')
    search_fields = ('email', 'first_name', 'last_name', 'tags')
    fieldsets = ((None, {'fields': ('email', 'first_name', 'last_name')}),
                 (None, {'fields': ('tags',)}),
                 (_('Status'), {'fields': ('subscriber', 'valid', 'tester')}),
                 (_('Advanced'), {'fields': ('object_id', 'content_type'),
                                  'classes': ('collapse',)}),
                 )
    actions = ['create_mailinglist', 'export_vcard']
    actions_on_top = False
    actions_on_bottom = True

    def related_object_admin(self, contact):
        """Display link to related object's admin"""
        if contact.content_type and contact.object_id:
            admin_url = reverse('admin:%s_%s_change' % (contact.content_type.app_label,
                                                        contact.content_type.model),
                                args=(contact.object_id,))
            return '%s: <a href="%s">%s</a>' % (contact.content_type.model.capitalize(),
                                                admin_url,
                                                contact.content_object.__unicode__())
        return _('No relative object')
    related_object_admin.allow_tags = True
    related_object_admin.short_description = _('Related object')

    def total_subscriptions(self, contact):
        """Display user subscriptions to unsubscriptions"""
        subscriptions = contact.subscriptions().count()
        unsubscriptions = contact.unsubscriptions().count()
        return '%s / %s' % (subscriptions - unsubscriptions, subscriptions)
    total_subscriptions.short_description = _('Total subscriptions')

    def export_vcard(self, request, queryset, export_name=''):
        """Export selected contact in VCard"""
        return vcard_contacts_export_response(queryset)
    export_vcard.short_description = _('Export contacts as VCard')

    def create_mailinglist(self, request, queryset):
        """Create a mailing list from selected contact"""
        when = str(datetime.now()).split('.')[0]
        new_mailing = MailingList(name=_('New mailinglist at %s') % when,
                                  description=_('New mailing list created in admin at %s') % when)
        new_mailing.save()
        new_mailing.subscribers = queryset.all()

        self.message_user(request, _('%s succesfully created.') % new_mailing)
    create_mailinglist.short_description = _('Create a mailinglist')

    def importation(self, request):
        """Import contacts from a VCard"""
        #TODO
        pass

    def exportation(self, request):
        """Export all the contact in VCard"""
        return self.export_vcard(request, Contact.objects.all(),
                                 'all_contacts_edn_%s' % datetime.now().strftime('%d-%m-%Y'))

    def get_urls(self):
        urls = super(ContactAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^import/$', self.importation,
                               name='newsletter_contact_import'),
                           url(r'^export/$', self.exportation,
                               name='newsletter_contact_export'),)
        return my_urls + urls

admin.site.register(Contact, ContactAdmin)

class MailingListAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('name', 'description',
                    'subscribers_count', 'unsubscribers_count',
                    'creation_date', 'exportation_link')
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
        """Merge multiple mailing list"""
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

    def exportation_link(self, mailinglist):
        """Display link for exportation"""
        return '<a href="%s">%s</a>' % (reverse('admin:newsletter_mailinglist_export', args=[mailinglist.pk,]),
                                        _('Export Subscribers'))
    exportation_link.allow_tags = True
    exportation_link.short_description = _('Export')

    def export_subscribers(self, request, mailinglist_id):
        """Export subscribers in the mailing in VCard"""
        mailinglist = get_object_or_404(MailingList, pk=mailinglist_id)
        name = 'contacts_%s' % mailinglist.name
        return vcard_contacts_export_response(mailinglist.subscribers.all(), name)

    def get_urls(self):
        urls = super(MailingListAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^export/(?P<mailinglist_id>\d+)/$', self.export_subscribers,
                               name='newsletter_mailinglist_export'),)
        return my_urls + urls

admin.site.register(MailingList, MailingListAdmin)


class NewsletterAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('title', 'mailing_list', 'server', 'status',
                    'sending_date', 'creation_date', 'modification_date', 'historic_link')
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

    def get_actions(self, request):
        actions = super(NewsletterAdmin, self).get_actions(request)
        if not request.user.has_perm('newsletter.can_change_status'):
            del actions['make_ready_to_send']
            del actions['make_cancel_sending']
        return actions

    #def formfield_for_choice_field(self, db_field, request, **kwargs):
    #    if db_field.name == 'status' and \
    #           not request.user.has_perm('newsletter.can_change_status'):
    #        kwargs['editable'] = False
    #        # Marche po
    #        return db_field.formfield(**kwargs)
    #    return super(NewsletterAdmin, self).formfield_for_choice_field(
    #        db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'test_contacts':
            kwargs['queryset'] = Contact.objects.filter(tester=True)
        return super(NewsletterAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def save_model(self, request, newsletter, form, change):
        if newsletter.content.startswith('http://'):
            try:
                newsletter.content = get_webpage_content(newsletter.content)
            except HTMLParseError:
                self.message_user(request, _('Unable to download HTML, due to errors within.'))

        if not request.user.has_perm('newsletter.can_change_status'):
            newsletter.status = form.initial.get('status', Newsletter.DRAFT)

        newsletter.save()

    def historic_link(self, newsletter):
        """Display link for historic"""
        return '<a href="%s">%s</a>' % (newsletter.get_historic_url(), _('View historic'))
    historic_link.allow_tags = True
    historic_link.short_description = _('Historic')

    def send_mail_test(self, request, queryset):
        """Send newsletter in test"""
        for newsletter in queryset:
            if newsletter.test_contacts.count():
                mailer = Mailer(newsletter, test=True)
                try:
                    mailer.run()
                except HTMLParseError:
                    self.message_user(request, _('Unable send newsletter, due to errors within HTML.'))
                    continue
                self.message_user(request, _('%s succesfully sent.') % newsletter)
            else:
                self.message_user(request, _('No test contacts assigned for %s.') % newsletter)
    send_mail_test.short_description = _('Send test email')

    def make_ready_to_send(self, request, queryset):
        """Make newsletter ready to send"""
        queryset = queryset.filter(status=Newsletter.DRAFT)
        for newsletter in queryset:
            newsletter.status = Newsletter.WAITING
            newsletter.save()
        self.message_user(request, _('%s newletters are ready to send') % queryset.count())
    make_ready_to_send.short_description = _('Make ready to send')

    def make_cancel_sending(self, request, queryset):
        """Cancel the sending of newsletters"""
        queryset = queryset.filter(Q(status=Newsletter.WAITING) |
                                   Q(status=Newsletter.SENDING))
        for newsletter in queryset:
            newsletter.status = Newsletter.CANCELED
            newsletter.save()
        self.message_user(request, _('%s newletters are cancelled') % queryset.count())
    make_cancel_sending.short_description = _('Cancel the sending')

    def historic(self, request, slug):
        """Display the historic of a newsletters"""
        opts = self.model._meta
        newsletter = get_object_or_404(Newsletter, slug=slug)

        context = {'title': _('Stats %s') % newsletter.__unicode__(),
                   'original': newsletter,
                   'opts': opts,
                   'object_id': newsletter.pk,
                   'root_path': self.admin_site.root_path,
                   'app_label': opts.app_label,}
        return render_to_response('newsletter/newsletter_historic.html',
                                  context,
                                  context_instance=RequestContext(request))

    def get_urls(self):
        urls = super(NewsletterAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^historic/(?P<slug>[-\w]+)/$', self.historic,
                               name='newsletter_newsletter_historic'),)
        return my_urls + urls

admin.site.register(Newsletter, NewsletterAdmin)

class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'creation_date')

if settings.DEBUG:
    admin.site.register(Link, LinkAdmin)
    admin.site.register(ContactMailingStatus)

