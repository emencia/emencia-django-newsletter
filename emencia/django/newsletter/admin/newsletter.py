"""ModelAdmin for Newsletter"""
from HTMLParser import HTMLParseError

from django import forms
from django.db.models import Q
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import Attachment
from emencia.django.newsletter.models import MailingList
from emencia.django.newsletter.mailer import Mailer
from emencia.django.newsletter.settings import USE_TINYMCE
from emencia.django.newsletter.settings import USE_WORKGROUPS
try:
    CAN_USE_PREMAILER = True
    from emencia.django.newsletter.utils.premailer import Premailer
    from emencia.django.newsletter.utils.premailer import PremailerError
except ImportError:
    CAN_USE_PREMAILER = False
from emencia.django.newsletter.utils.workgroups import request_workgroups
from emencia.django.newsletter.utils.workgroups import request_workgroups_contacts_pk
from emencia.django.newsletter.utils.workgroups import request_workgroups_newsletters_pk
from emencia.django.newsletter.utils.workgroups import request_workgroups_mailinglists_pk

# --- templates --- start -----------------------------------------------------
from emencia.django.newsletter.settings import USE_TEMPLATE
# --- templates --- end -------------------------------------------------------

class AttachmentAdminInline(admin.TabularInline):
    model = Attachment
    extra = 1
    fieldsets = ((None, {'fields': (('title', 'file_attachment'))}),)


class BaseNewsletterAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('title', 'mailing_list', 'server', 'status',
                    'sending_date', 'creation_date', 'modification_date',
                    'historic_link', 'statistics_link')
    list_filter = ('status', 'sending_date', 'creation_date', 'modification_date')
    search_fields = ('title', 'content', 'header_sender', 'header_reply')
    filter_horizontal = ['test_contacts']
    fieldsets = ((None, {'fields': ['title', 'content',]}),
                 (_('Receivers'), {'fields': ('mailing_list', 'test_contacts',)}),
                 (_('Sending'), {'fields': ('sending_date', 'status',)}),
                 (_('Miscellaneous'), {'fields': ('server', 'header_sender',
                                                  'header_reply', 'slug'),
                                       'classes': ('collapse',)}),
                 )
    # --- templates --- start -------------------------------------------------
    if USE_TEMPLATE:
        fieldsets[0][1]['fields'].append('template')
    # --- templates --- end ---------------------------------------------------

    prepopulated_fields = {'slug': ('title',)}
    inlines = (AttachmentAdminInline,)
    actions = ['send_mail_test', 'make_ready_to_send', 'make_cancel_sending', 'duplicate']
    actions_on_top = False
    actions_on_bottom = True

    def get_actions(self, request):
        actions = super(BaseNewsletterAdmin, self).get_actions(request)
        if not request.user.has_perm('newsletter.can_change_status'):
            del actions['make_ready_to_send']
            del actions['make_cancel_sending']
        return actions

    def queryset(self, request):
        queryset = super(BaseNewsletterAdmin, self).queryset(request)
        if not request.user.is_superuser and USE_WORKGROUPS:
            newsletters_pk = request_workgroups_newsletters_pk(request)
            queryset = queryset.filter(pk__in=newsletters_pk)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mailing_list' and \
               not request.user.is_superuser and USE_WORKGROUPS:
            mailinglists_pk = request_workgroups_mailinglists_pk(request)
            kwargs['queryset'] = MailingList.objects.filter(pk__in=mailinglists_pk)
            return db_field.formfield(**kwargs)
        return super(BaseNewsletterAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'status' and \
               not request.user.has_perm('newsletter.can_change_status'):
            kwargs['choices'] = ((Newsletter.DRAFT, _('Default')),)
            return db_field.formfield(**kwargs)
        return super(BaseNewsletterAdmin, self).formfield_for_choice_field(
            db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'test_contacts':
            queryset = Contact.objects.filter(tester=True)
            if not request.user.is_superuser and USE_WORKGROUPS:
                contacts_pk = request_workgroups_contacts_pk(request)
                queryset = queryset.filter(pk__in=contacts_pk)
            kwargs['queryset'] = queryset
        return super(BaseNewsletterAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def save_model(self, request, newsletter, form, change):
        workgroups = []
        if not newsletter.pk and not request.user.is_superuser \
               and USE_WORKGROUPS:
            workgroups = request_workgroups(request)

        if newsletter.content.startswith('http://'):
            if CAN_USE_PREMAILER:
                try:
                    premailer = Premailer(newsletter.content.strip())
                    newsletter.content = premailer.transform()
                except PremailerError:
                    self.message_user(request, _('Unable to download HTML, due to errors within.'))
            else:
                self.message_user(request, _('Please install lxml for parsing an URL.'))
        if not request.user.has_perm('newsletter.can_change_status'):
            newsletter.status = form.initial.get('status', Newsletter.DRAFT)

        newsletter.save()

        for workgroup in workgroups:
            workgroup.newsletters.add(newsletter)

    def historic_link(self, newsletter):
        """Display link for historic"""
        if newsletter.contactmailingstatus_set.count():
            return u'<a href="%s">%s</a>' % (newsletter.get_historic_url(), _('View historic'))
        return _('Not available')
    historic_link.allow_tags = True
    historic_link.short_description = _('Historic')

    def statistics_link(self, newsletter):
        """Display link for statistics"""
        if newsletter.status == Newsletter.SENDING or \
           newsletter.status == Newsletter.SENT:
            return u'<a href="%s">%s</a>' % (newsletter.get_statistics_url(), _('View statistics'))
        return _('Not available')
    statistics_link.allow_tags = True
    statistics_link.short_description = _('Statistics')

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

    # --- duplicate newsletter --- start --------------------------------------
    def duplicate(self, request, queryset):
        """Duplicate selected newsletters"""
        for newsletter in queryset:
            newsletter.pk = None
            i = 1
            while Newsletter.objects.filter(slug=u'%s-%s' % (newsletter.slug, i)).count() > 0:
                i += 1
            newsletter.slug = u'%s-%s' % (newsletter.slug, i)
            newsletter.title = u'%s [%s]' % (newsletter.title, i)
            newsletter.save()
        
    # --- duplicate newsletter --- end ----------------------------------------


if USE_TINYMCE:
    from tinymce.widgets import TinyMCE

    class NewsletterTinyMCEForm(forms.ModelForm):
        content = forms.CharField(
            widget=TinyMCE(attrs={'cols': 150, 'rows': 80}))

        class Meta:
            model = Newsletter

    class NewsletterAdmin(BaseNewsletterAdmin):
        form = NewsletterTinyMCEForm
else:
    class NewsletterAdmin(BaseNewsletterAdmin):
        pass
