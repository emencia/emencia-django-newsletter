"""Utils for newsletter"""
import urllib2

from BeautifulSoup import BeautifulSoup
from django.template import Context, Template

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
