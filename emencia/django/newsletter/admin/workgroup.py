"""ModelAdmin for WorkGroup"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class WorkGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'contacts_length',
                    'mailinglists_length', 'newsletters_length')
    fieldsets = ((None, {'fields': ('name', 'group')}),
                 (None, {'fields': ('contacts', 'mailinglists', 'newsletters')}),
                 )
    filter_horizontal = ['contacts', 'mailinglists', 'newsletters']
    actions_on_top = False
    actions_on_bottom = True

    def contacts_length(self, workgroup):
        return workgroup.contacts.count()
    contacts_length.short_description = _('Contacts length')

    def mailinglists_length(self, workgroup):
        return workgroup.mailinglists.count()
    mailinglists_length.short_description = _('Mailing List length')

    def newsletters_length(self, workgroup):
        return workgroup.newsletters.count()
    newsletters_length.short_description = _('Newsletter length')
