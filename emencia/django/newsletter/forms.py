
"""Forms for emencia.django.newsletter"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from emencia.django.newsletter.models import Contact, MailingList

# --- subscriber verification --- start ---------------------------------------
from emencia.django.newsletter.settings import SUBSCRIBER_VERIFICATION

if SUBSCRIBER_VERIFICATION:
    from emencia.django.newsletter.models import SubscriberVerification
# --- subscriber verification --- end -----------------------------------------


class MailingListSubscriptionForm(forms.ModelForm):
    """Form for subscribing to a mailing list"""
    # Notes : This form will not check the uniquess of
    # the 'email' field, by defining it explictly and setting
    # it the Meta.exclude list, for allowing registration
    # to a mailing list even if the contact already exists.
    # Then the contact is always added to the subscribers field
    # of the mailing list because it will be cleaned with no
    # double.

    email = forms.EmailField(label=_('Email'), max_length=75)

    def save(self, mailing_list):
        data = self.cleaned_data
        contact, created = Contact.objects.get_or_create(
            email=data['email'],
            defaults={'first_name': data['first_name'],
                      'last_name': data['last_name']})

        mailing_list.subscribers.add(contact)
        mailing_list.unsubscribers.remove(contact)

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name')
        exclude = ('email',)


class AllMailingListSubscriptionForm(MailingListSubscriptionForm):
    """Form for subscribing to all mailing list"""

    mailing_lists = forms.ModelMultipleChoiceField(
        queryset=MailingList.objects.all(),
        initial=[obj.id for obj in MailingList.objects.all()],
        label=_('Mailing lists'),
        widget=forms.CheckboxSelectMultiple())

    def save(self, mailing_list):
        data = self.cleaned_data
        contact, created = Contact.objects.get_or_create(
            email=data['email'],
            defaults={'first_name': data['first_name'],
                      'last_name': data['last_name']})

        for mailing_list in data['mailing_lists']:
            mailing_list.subscribers.add(contact)
            mailing_list.unsubscribers.remove(contact)

# --- subscriber verification --- start ---------------------------------------
if SUBSCRIBER_VERIFICATION:
    class VerificationMailingListSubscriptionForm(forms.Form):
        """Form for subscribing to all mailing list after verification"""

        mailing_lists = forms.ModelMultipleChoiceField(
            queryset=MailingList.objects.all(),
            initial=[obj.id for obj in MailingList.objects.all()],
            label=_('Mailing lists'),
            widget=forms.CheckboxSelectMultiple(),
        )

        def save(self, contact_id):
            mailing_list = None
            data = self.cleaned_data

            for mailing_list in data['mailing_lists']:
                mailing_list.subscribers.add(
                    Contact.objects.get(id=contact_id)
                )
                mailing_list.unsubscribers.remove(
                    Contact.objects.get(id=contact_id)
                )

    class SubscriberVerificationForm(forms.ModelForm):
        """Form for verificate an contact"""

        class Meta:
            model = Contact
            exclude = (
                'verified',
                'subscriber',
                'valid',
                'tester',
                'tags',
                'content_type',
                'object_id'
            )

# --- subscriber verification --- end -----------------------------------------