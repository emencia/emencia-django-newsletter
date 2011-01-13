"""ModelAdmin for MailingList"""
from datetime import datetime

from django.contrib import admin
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.settings import USE_WORKGROUPS
from emencia.django.newsletter.utils.workgroups import request_workgroups
from emencia.django.newsletter.utils.workgroups import request_workgroups_contacts_pk
from emencia.django.newsletter.utils.workgroups import request_workgroups_mailinglists_pk
from emencia.django.newsletter.utils.vcard import vcard_contacts_export_response


class MailingListAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('creation_date', 'name', 'description',
                    'subscribers_count', 'unsubscribers_count',
                    'exportation_link')
    list_editable = ('name', 'description')
    list_filter = ('creation_date', 'modification_date')
    search_fields = ('name', 'description',)
    filter_horizontal = ['subscribers', 'unsubscribers']
    fieldsets = ((None, {'fields': ('name', 'description',)}),
                 (None, {'fields': ('subscribers',)}),
                 (None, {'fields': ('unsubscribers',)}),
                 )
    actions = ['merge_mailinglist']
    actions_on_top = False
    actions_on_bottom = True

    def queryset(self, request):
        queryset = super(MailingListAdmin, self).queryset(request)
        if not request.user.is_superuser and USE_WORKGROUPS:
            mailinglists_pk = request_workgroups_mailinglists_pk(request)
            queryset = queryset.filter(pk__in=mailinglists_pk)
        return queryset

    def save_model(self, request, mailinglist, form, change):
        workgroups = []
        if not mailinglist.pk and not request.user.is_superuser:
            workgroups = request_workgroups(request)
        mailinglist.save()
        for workgroup in workgroups:
            workgroup.mailinglists.add(mailinglist)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if 'subscribers' in db_field.name and not request.user.is_superuser:
            contacts_pk = request_workgroups_contacts_pk(request)
            kwargs['queryset'] = Contact.objects.filter(pk__in=contacts_pk)
        return super(MailingListAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def merge_mailinglist(self, request, queryset):
        """Merge multiple mailing list"""
        if queryset.count() == 1:
            self.message_user(request, _('Please select a least 2 mailing list.'))
            return None

        subscribers = {}
        unsubscribers = {}
        for ml in queryset:
            for contact in ml.subscribers.all():
                subscribers[contact] = ''
            for contact in ml.unsubscribers.all():
                unsubscribers[contact] = ''

        when = str(datetime.now()).split('.')[0]
        new_mailing = MailingList(name=_('Merging list at %s') % when,
                                  description=_('Mailing list created by merging at %s') % when)
        new_mailing.save()
        new_mailing.subscribers = subscribers.keys()
        new_mailing.unsubscribers = unsubscribers.keys()

        self.message_user(request, _('%s succesfully created by merging.') % new_mailing)
        return HttpResponseRedirect(reverse('admin:newsletter_mailinglist_change',
                                            args=[new_mailing.pk]))
    merge_mailinglist.short_description = _('Merge selected mailinglists')

    def exportation_link(self, mailinglist):
        """Display link for exportation"""
        return '<a href="%s">%s</a>' % (reverse('admin:newsletter_mailinglist_export',
                                                args=[mailinglist.pk]),
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
                           url(r'^export/(?P<mailinglist_id>\d+)/$',
                               self.admin_site.admin_view(self.export_subscribers),
                               name='newsletter_mailinglist_export'),)
        return my_urls + urls
