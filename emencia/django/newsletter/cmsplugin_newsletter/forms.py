import re

from django.conf import settings
from django import forms
from django.forms.widgets import Select, MultiWidget
from django.utils import translation

import cms.forms.fields

from emencia.django.newsletter.models import Newsletter

class PageSelectWidget(MultiWidget):
    """A widget that allows selecting a page by first selecting a site and then
    a page on that site in a two step process.
    """
    orig_url = re.compile(r"<!--CMS Origin URL: http://.*/\?site=(\d+)&page=(\d+)&lang=(\w+)-->", flags=re.MULTILINE)
    
    def __init__(self, attrs=None):

        widgets = (Select(choices=settings.LANGUAGES),
                   cms.forms.widgets.PageSelectWidget()
                   )

        super(PageSelectWidget, self).__init__(widgets, attrs)
        
    def decompress(self, value):
        '''parses the content of HTML and if finds origin URL, then decomposes it into the 
           dropdown settings. The format of HTML comment:
           <!--CMS Origin URL: http://<site_domain_name>/<page_absolute_url>/?site=<site_pk>&page=<page_pk>&lang=<lang>-->        
        '''
        
        res=[translation.get_language(), []]
        if value:
            m = self.orig_url.search(value)

            if m.groups():
                res = [m.group(3), [m.group(1),m.group(2),m.group(2)] ]
        
        return res
        
class CMSPageField(forms.fields.MultiValueField):
    widget = PageSelectWidget

    def __init__(self, required=True, widget=None, label=None, initial=None,
                 help_text=None):
        fields = (forms.fields.ChoiceField(choices=settings.LANGUAGES),
                 cms.forms.fields.PageSelectFormField(None)
                 )
        super(CMSPageField, self).__init__(fields=fields, widget=widget, 
              label=label, initial=initial, help_text=help_text)
        
    def compress(self, data_list):

        lang, page = data_list
        url = page.get_absolute_url(language=lang)
        url = "http://%s/%s%s?site=%s&page=%s&lang=%s" % (page.site.domain, lang, url, page.site.pk, page.pk, lang)

        return url

class NewsletterCMSForm(forms.ModelForm):
    content = CMSPageField()
    
    class Meta:
        model = Newsletter
