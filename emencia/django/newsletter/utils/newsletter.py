"""Utils for newsletter"""
import urllib2
from urlparse import urljoin
from urlparse import urlparse

from BeautifulSoup import BeautifulSoup
from django.core.urlresolvers import reverse

from emencia.django.newsletter.models import Link


def get_external_styles(soup, base_url):
    """Return a list of external styles"""
    styles = []

    for link in soup('link'):
        if link.get('rel', '').lower() == 'stylesheet' and link.get('href'):
            media = link.get('media', '')
            for media_type in ('all', 'screen', 'projection'):
                if media_type in media:
                    media_url = link['href']
                    media_url_components = urlparse(media_url)
                    if not media_url_components.netloc:
                        styles.append(urljoin(base_url, media_url))
                    else:
                        styles.append(media_url)
                    break
    return styles


def get_webpage_content(url):
    """Using premailer lib for rendering well the page,
    else fallback to BeautifulSoup"""
    request = urllib2.Request(url)
    page_content = '\n'.join(urllib2.urlopen(request).readlines())

    try:
        from premailer import Premailer
        pm = Premailer(page_content,
                       base_url=urljoin(url, '/'),
                       external_styles=get_external_styles(
                           BeautifulSoup(page_content), url))
        page_content = pm.transform()
    except (ImportError, AssertionError):
        pass

    soup = BeautifulSoup(page_content)
    return soup.body.prettify()


def body_insertion(content, insertion, end=False):
    """Insert an HTML content into the body HTML node"""
    if not content.startswith('<body'):
        content = '<body>%s</body>' % content
    soup = BeautifulSoup(content)

    if end:
        soup.body.append(insertion)
    else:
        soup.body.insert(0, insertion)
    return soup.prettify()


def track_links(content, context):
    """Convert all links in the template for the user
    to track his navigation"""
    if not context.get('uidb36'):
        return content

    soup = BeautifulSoup(content)
    for link_markup in soup('a'):
        if link_markup.get('href'):
            link_href = link_markup['href']
            link_title = link_markup.get('title', link_href)
            link, created = Link.objects.get_or_create(url=link_href,
                                                       defaults={'title': link_title})
            link_markup['href'] = 'http://%s%s' % (context['domain'], reverse('newsletter_newsletter_tracking_link',
                                                                              args=[context['newsletter'].slug,
                                                                                    context['uidb36'], context['token'],
                                                                                    link.pk]))
    return soup.prettify()
