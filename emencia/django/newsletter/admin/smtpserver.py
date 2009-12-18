"""ModelAdmin for SMTPServer"""
from django.contrib import admin
from django.utils.translation import ugettext as _

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
