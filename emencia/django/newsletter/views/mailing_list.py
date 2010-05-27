"""Views for emencia.django.newsletter Mailing List"""
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from emencia.django.newsletter.utils.tokens import untokenize
from emencia.django.newsletter.models import Newsletter, Contact
from emencia.django.newsletter.models import ContactMailingStatus
from emencia.django.newsletter.forms import SubscriptionForm


def view_mailinglist_unsubscribe(request, slug, uidb36, token):
    """Unsubscribe a contact to a mailing list"""
    newsletter = get_object_or_404(Newsletter, slug=slug)
    contact = untokenize(uidb36, token)

    already_unsubscribed = contact in newsletter.mailing_list.unsubscribers.all()

    if request.POST.get('email') and not already_unsubscribed:
        newsletter.mailing_list.unsubscribers.add(contact)
        newsletter.mailing_list.save()
        already_unsubscribed = True
        log = ContactMailingStatus.objects.create(newsletter=newsletter, contact=contact,
                                                  status=ContactMailingStatus.UNSUBSCRIPTION)

    return render_to_response('newsletter/mailing_list_unsubscribe.html',
                              {'email': contact.email,
                               'already_unsubscribed': already_unsubscribed},
                              context_instance=RequestContext(request))

def view_mailinglist_subscribe(request, template="newsletter/mailing_list_subscribe.html"):
    """
    A simple view that shows a form for subscription
    on one or more mailing-lists at the same time.
    """

    subscribed = False

    if request.method == 'POST' and not subscribed:
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            contact, generated = Contact.objects.get_or_create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'])

            for mailing_list in form.cleaned_data['mailing_lists']:
                mailing_list.subscribers.add(contact)

            subscribed = True
    else:
        form = SubscriptionForm()

    return render_to_response(
        template,
        {'subscribed': subscribed,
         'form': form },
        context_instance=RequestContext(request)
    )


