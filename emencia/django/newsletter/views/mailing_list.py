"""Views for emencia.django.newsletter Mailing List"""
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.models import Newsletter
from emencia.django.newsletter.models import ContactMailingStatus


def view_mailinglist_unsubscribe(request, slug, uidb36, token):
    """Unsubscribe a contact to a mailing list"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)
    
    already_unsubscribed = contact in newsletter.mailing_list.unsubscribers.all()

    if request.POST.get('email'):
        newsletter.mailing_list.unsubscribers.add(contact)
        newsletter.mailing_list.save()
        already_unsubcribed = True
        log = ContactMailingStatus.objects.create(newsletter=newsletter, contact=contact,
                                                  status=ContactMailingStatus.UNSUBSCRIPTION)

    return render_to_response('newsletter/mailing_list_unsubscribe.html',
                              {'email': contact.email,
                               'already_unsubscribed': already_unsubscribed},
                              context_instance=RequestContext(request))

