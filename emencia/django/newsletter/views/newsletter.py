"""Views for emencia.django.newsletter Newsletter"""
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string as render_file

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils import render_string
from emencia.django.newsletter.utils.newsletter import body_insertion
from emencia.django.newsletter.utils.newsletter import track_links
from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.settings import TRACKING_LINKS

# --- template --- start ------------------------------------------------------
from django.template.loader import render_to_string
from emencia.django.newsletter.settings import USE_TEMPLATE
# --- template --- end --------------------------------------------------------

def render_newsletter(request, slug, context):
    """Return a newsletter in HTML format"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    context.update({'newsletter': newsletter,
                    'domain': Site.objects.get_current().domain})

    content = render_string(newsletter.content, context)
    title = render_string(newsletter.title, context)
    if TRACKING_LINKS:
        content = track_links(content, context)
    unsubscription = render_file('newsletter/newsletter_link_unsubscribe.html', context)
    # --- template --- start --------------------------------------------------
    if USE_TEMPLATE:
        content =  render_to_string(
            'mailtemplates/{0}/{1}'.format(newsletter.template,'index.html'),
            {
                'content': content,
                'link_site': '',
                'unsubscription': unsubscription
            }
        )
        #insert image_tracking
    else:
        content = body_insertion(content, unsubscription, end=True)
    # --- template --- end ----------------------------------------------------

    return render_to_response('newsletter/newsletter_detail.html',
                              {'content': content,
                               'title': title,
                               'object': newsletter},
                              context_instance=RequestContext(request))


@login_required
def view_newsletter_preview(request, slug):
    """View of the newsletter preview"""
    context = {'contact': request.user}
    return render_newsletter(request, slug, context)


def view_newsletter_contact(request, slug, uidb36, token):
    """Visualization of a newsletter by an user"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    ContactMailingStatus.objects.create(newsletter=newsletter,
                                        contact=contact,
                                        status=ContactMailingStatus.OPENED_ON_SITE)
    context = {'contact': contact,
               'uidb36': uidb36, 'token': token}

    return render_newsletter(request, slug, context)