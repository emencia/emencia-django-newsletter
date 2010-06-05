"""Forms for emencia.django.newsletter"""
from django import forms
from django.utils.translation import ugettext_lazy as _

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList

class MailingListSubscriptionForm(forms.ModelForm):
    """Form for subscribing to a mailing list"""

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        data = self.cleaned_data['email']
        email = Contact.objects.filter(email=data)

        if email:
            raise forms.ValidationError(_("This email address already exists in our database!"))

        return data

class AllMailingListSubscriptionForm(MailingListSubscriptionForm):
    """Form for subscribing to all mailing list"""

    mailing_lists = forms.ModelMultipleChoiceField(
        queryset=MailingList.objects.all(),
        initial=[obj.id for obj in MailingList.objects.all()],
        widget=forms.CheckboxSelectMultiple())
    
