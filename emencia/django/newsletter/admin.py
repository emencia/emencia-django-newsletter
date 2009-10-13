"""Admin for emencia.django.newsletter"""
from django.contrib import admin

from emencia.django.newsletter.models import SMTPServer
from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus

admin.site.register(SMTPServer)
admin.site.register(Contact)
admin.site.register(MailingList)
admin.site.register(Newsletter)
admin.site.register(ContactMailingStatus)

