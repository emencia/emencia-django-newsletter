"""ModelAdmin for MailingList"""
from datetime import datetime

from django.contrib import admin
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.vcard import vcard_contacts_export_response

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
