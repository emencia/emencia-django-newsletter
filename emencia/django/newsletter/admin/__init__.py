"""Admin for emencia.django.newsletter"""
from django.contrib import admin
from django.conf import settings

from emencia.django.newsletter.models import Link
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import WorkGroup
from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import ContactMailingStatus

from emencia.django.newsletter.settings import USE_WORKGROUPS
from emencia.django.newsletter.admin.contact import ContactAdmin
from emencia.django.newsletter.admin.workgroup import WorkGroupAdmin
from emencia.django.newsletter.admin.newsletter import NewsletterAdmin
from emencia.django.newsletter.admin.smtpserver import SMTPServerAdmin
from emencia.django.newsletter.admin.mailinglist import MailingListAdmin


admin.site.register(Contact, ContactAdmin)
admin.site.register(SMTPServer, SMTPServerAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(MailingList, MailingListAdmin)

if USE_WORKGROUPS:
    admin.site.register(WorkGroup, WorkGroupAdmin)


class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'creation_date')

if settings.DEBUG:
    admin.site.register(Link, LinkAdmin)
    admin.site.register(ContactMailingStatus)
