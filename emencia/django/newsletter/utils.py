"""Utils for newsletter"""
import urllib2

from BeautifulSoup import BeautifulSoup

def get_webpage_content(url):
    """Return the content of the website
    located in the body markup"""
    request = urllib2.Request(url)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)
    
    return soup.body.findChild().prettify()
