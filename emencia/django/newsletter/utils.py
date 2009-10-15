"""Utils for newsletter"""
import urllib2

from BeautifulSoup import BeautifulSoup

def get_webpage_body(url):

    request = urllib2.Request(url)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)
    
    return soup('body')[0].prettify()
