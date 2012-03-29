from django.conf import settings
from django import forms
from django.forms.widgets import Select, MultiWidget

import cms.forms


from emencia.django.newsletter.models import Newsletter

class PageSelectWidget(MultiWidget):
    """A widget that allows selecting a page by first selecting a site and then
    a page on that site in a two step process.
    """
    def __init__(self, attrs=None):

        widgets = (Select(choices=settings.LANGUAGES),
                   cms.forms.widgets.PageSelectWidget()
                   )

        super(PageSelectWidget, self).__init__(widgets, attrs)
        
    def decompress(self, value):
        print 'value to decompress: %s' % value
        return ['fr', []]
        
class CMSPageField(forms.Field):

    def __init__(self, *args, **kwargs):
        self.widget = PageSelectWidget()
        super(CMSPageField, self).__init__(*args, **kwargs)

    def clean(self, value):
        print 'field clean: %s' % value
        lang = value[0]
        site = value[1][0]
        page = value[1][1]

        print 'CMS page: lang=%s site=%s page=%s' % (lang, site, page)
        
        return value

class NewsletterCMSForm(forms.ModelForm):
    content = CMSPageField()
    
    class Meta:
        model = Newsletter
