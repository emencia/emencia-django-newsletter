"""Models of Emencia CMS Plugins"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

from emencia.django.newsletter.models import MailingList


class SubscriptionFormPlugin(CMSPlugin):
    """CMS Plugin for susbcribing to a mailing list"""
    title = models.CharField(_('title'), max_length=100, blank=True)
    show_description = models.BooleanField(_('show description'), default=True,
                                           help_text=_('Show the mailing list\'s description.'))
    mailing_list = models.ForeignKey(MailingList, verbose_name=_('mailing list'),
                                     help_text=_('Mailing List to subscribe to.'))

    def __unicode__(self):
        return self.mailing_list.name
