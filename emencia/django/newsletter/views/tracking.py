"""Views for emencia.django.newsletter Tracking"""
import base64

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from emencia.django.newsletter.models import Link
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.settings import TRACKING_IMAGE


def view_newsletter_tracking(request, slug, uidb36, token):
    """Track the opening of the newsletter by requesting a blank img"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    ContactMailingStatus.objects.create(newsletter=newsletter,
                                        contact=contact,
                                        status=ContactMailingStatus.OPENED)
    return HttpResponse(base64.b64decode(TRACKING_IMAGE), mimetype='image/png')


def view_newsletter_tracking_link(request, slug, uidb36, token, link_id):
    """Track the opening of a link on the website"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    link = get_object_or_404(Link, pk=link_id)
    ContactMailingStatus.objects.create(newsletter=newsletter,
                                        contact=contact,
                                        status=ContactMailingStatus.LINK_OPENED,
                                        link=link)
    return HttpResponseRedirect(link.url)


@login_required
def view_newsletter_historic(request, slug):
    """Display the historic of a newsletter"""
    opts = Newsletter._meta
    newsletter = get_object_or_404(Newsletter, slug=slug)

    context = {'title': _('Historic of %s') % newsletter.__unicode__(),
               'original': newsletter,
               'opts': opts,
               'object_id': newsletter.pk,
               'app_label': opts.app_label}
    return render_to_response('newsletter/newsletter_historic.html',
                              context, context_instance=RequestContext(request))
