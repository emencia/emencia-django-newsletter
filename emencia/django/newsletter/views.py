"""Views for emencia.django.newsletter"""
import base64

from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.utils.http import base36_to_int
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string as render_file

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.utils import render_string
from emencia.django.newsletter.tokens import untokenize
from emencia.django.newsletter.tokens import ContactTokenGenerator
from emencia.django.newsletter.settings import TRACKING_IMAGE

def render_newsletter(request, slug, context):
    """Return a newsletter in HTML format"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    context.update({'newsletter': newsletter,
                    'domain': Site.objects.get_current().domain})
    
    content = render_string(newsletter.content, context)
    footer = render_file('newsletter/newsletter_footer_unsubscribe.html', context)
    
    return render_to_response('newsletter/newsletter_detail.html',
                              {'content': content,
                               'footer': footer},
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
    log = ContactMailingStatus.objects.create(newsletter=newsletter,
                                              contact=contact,
                                              status=ContactMailingStatus.OPENED_ON_SITE)
    context = {'contact': contact,
               'uidb36': uidb36, 'token': token}
    
    return render_newsletter(request, slug, context)

def view_newsletter_tracking(request, slug, uidb36, token):
    """Track the opening of the newsletter by requesting a blank img"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    log = ContactMailingStatus.objects.create(newsletter=newsletter,
                                              contact=contact,
                                              status=ContactMailingStatus.OPENED)
    return HttpResponse(base64.b64decode(TRACKING_IMAGE), mimetype='image/png')

def view_mailinglist_unsubscribe(request, slug, uidb36, token):
    """Unsubscribe a contact to a mailing list"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    
    already_unsubscribed = contact in newsletter.mailing_list.unsubscribers.all()

    if request.POST.get('email'):
        newsletter.mailing_list.unsubscribers.add(contact)
        newsletter.mailing_list.save()
        already_unsubcribed = True

    return render_to_response('newsletter/newsletter_unsubscribe.html',
                              {'email': contact.email,
                               'already_unsubscribed': already_unsubscribed},
                              context_instance=RequestContext(request))

