"""Plugins for CMS"""
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from emencia.django.newsletter.cmsplugin_newsletter import settings
from emencia.django.newsletter.cmsplugin_newsletter.models import SubscriptionFormPlugin
from emencia.django.newsletter.forms import MailingListSubscriptionForm


class CMSSubscriptionFormPlugin(CMSPluginBase):
    module = _('newsletter')
    model = SubscriptionFormPlugin
    name = _('Subscription Form')
    render_template = 'newsletter/cms/subscription_form.html'
    text_enabled = False
    admin_preview = False

    def render(self, context, instance, placeholder):
        request = context['request']
        if request.method == "POST" and (settings.FORM_NAME in request.POST.keys()):
            form = MailingListSubscriptionForm(data=request.POST)
            if form.is_valid():
                form.save(instance.mailing_list)
                form.saved = True
        else:
            form = MailingListSubscriptionForm()
        context.update({
            'object': instance,
            'form': form,
            'form_name': settings.FORM_NAME,
            'placeholder': placeholder,
        })
        return context


plugin_pool.register_plugin(CMSSubscriptionFormPlugin)
