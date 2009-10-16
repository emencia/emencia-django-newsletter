"""Views for emencia.django.newsletter"""
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.utils.http import base36_to_int
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string as render_file

from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.utils import render_string
from emencia.django.newsletter.tokens import untokenize
from emencia.django.newsletter.tokens import ContactTokenGenerator
from emencia.django.newsletter.settings import INCLUDE_UNSUBSCRIPTION

def render_newsletter(request, slug, context):
    """Return a newsletter in HTML format"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    context.update({'newsletter': newsletter})
    
    content = render_string(newsletter.content, context)
    footer = INCLUDE_UNSUBSCRIPTION and \
             render_file('newsletter/newsletter_footer.html', context) or ''
    
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
    context = {'contact': untokenize(uidb36, token),
               'uidb36': uidb36, 'token': token}
    return render_newsletter(request, slug, context)

def view_mailinglist_unsubscribe(request, slug, uidb36, token):
    """Unsubscribe a contact to a mailing list"""
    pass
