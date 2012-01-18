from django.contrib import admin


class ContactMailingStatusAdmin(admin.ModelAdmin):
    """ Admin settings for ContactMailingStatus model """

    ### list_display callables
    # n/a

    ### additional admin actions for this model
    # n/a

    ### model admin options
    save_on_top = True
    # list display reasoning: 
    # 1. click-able fields to either edit or view on site or whatever 
    # 2. model information fields that effect rendering/system logic broad to narrow effecting
    # 3. lsit_editable fields that effect rendering/system logic broad to narrow effecting i.e. status, order, color
    list_display = ['id', 'status', 'newsletter', 'contact', 'link']
    list_display_links = ['id'] # other columns from list_display to turn into edits link; defaults to first column
    list_filter = ['status'] # from least specific to most specific
    search_fields = ['newsletter__title', 'contact__first_name', 'contact__last_name']
    readonly_fields = ['newsletter', 'contact', 'status', 'link']
    ordering = ['-id']


