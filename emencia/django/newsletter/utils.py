"""Utils for newsletter"""
import urllib2

from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse
from django.template import Context, Template

from emencia.django.newsletter.models import Link

def get_webpage_content(url):
    """Return the content of the website
    located in the body markup"""
    request = urllib2.Request(url)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)
        
    return soup.body.renderContents()

def render_string(template_string, context={}):
    """Shortcut for render a template string with a context"""
    t = Template(template_string)
    c = Context(context)
    return t.render(c)

def track_links(content, context):
    """Convert all links in the template for the user
    to track his navigation"""
    if not context.get('uidb36'):
        return content
    
    soup = BeautifulSoup(content)
    for link_markup in soup('a'):
        if link_markup.get('href'):
            link_href = link_markup['href']
            if '?' not in link_href and '@' not in link_href and \
                   not link_href.endswith('/'):
                link_href = '%s/' % link_href
            link_title = link_markup.get('title', link_href)
            link, created = Link.objects.get_or_create(url=link_href,
                                                       defaults={'title': link_title})
            link_markup['href'] = reverse('newsletter_newsletter_tracking_link',
                                          args=[context['newsletter'].slug,
                                                context['uidb36'], context['token'],
                                                link.pk])
    return soup
