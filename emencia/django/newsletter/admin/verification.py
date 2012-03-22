# --- subscriber verification --- start ---------------------------------------
from django.contrib import admin

from emencia.django.newsletter.models \
    import SubscriberVerification

class SubscriberVerificationAdmin(admin.ModelAdmin):
    fields = ['link_id', 'contact']

admin.site.register(SubscriberVerification, SubscriberVerificationAdmin)
# --- subscriber verification --- end -----------------------------------------