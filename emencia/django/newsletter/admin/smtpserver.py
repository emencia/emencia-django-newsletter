"""ModelAdmin for SMTPServer"""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from emencia.django.newsletter.models import SMTPServer


class SMTPServerAdminForm(forms.ModelForm):
    """Form ofr SMTPServer with custom validation"""

    def clean_headers(self):
        """Check if the headers are well formated"""
        for line in self.cleaned_data['headers'].splitlines():
            elems = line.split(':')
            if len(elems) < 2:
                raise ValidationError(_('Invalid syntax, do not forget the ":".'))
            if len(elems) > 2:
                raise ValidationError(_('Invalid syntax, several assignments by line.'))

        return self.cleaned_data['headers']

    class Meta:
        model = SMTPServer


class SMTPServerAdmin(admin.ModelAdmin):
    form = SMTPServerAdminForm
    list_display = ('name', 'host', 'port', 'user', 'tls', 'mails_hour',)
    list_filter = ('tls',)
    search_fields = ('name', 'host', 'user')
    fieldsets = ((None, {'fields': ('name', )}),
                 (_('Configuration'), {'fields': ('host', 'port',
                                                  'user', 'password', 'tls')}),
                 (_('Miscellaneous'), {'fields': ('mails_hour', 'headers'),
                                       'classes': ('collapse', )}),
                 )
    actions = ['check_connections']
    actions_on_top = False
    actions_on_bottom = True

    def check_connections(self, request, queryset):
        """Check the SMTP connection"""
        message = '%s connection %s'
        for server in queryset:
            try:
                smtp = server.connect()
                if smtp:
                    status = 'OK'
                    smtp.quit()
                else:
                    status = 'KO'
            except:
                status = 'KO'
            self.message_user(request, message % (server.__unicode__(), status))
    check_connections.short_description = _('Check connection')
