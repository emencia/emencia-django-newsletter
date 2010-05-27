from django import forms
from django.utils.translation import ugettext_lazy as _

from emencia.django.newsletter.models import Contact
from emencia.django.newsletter.models import MailingList


class SubscriptionForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mailing_lists = forms.ModelMultipleChoiceField(
        queryset=MailingList.objects.all(),
        initial=[obj.id for obj in MailingList.objects.all()],
        widget=forms.CheckboxSelectMultiple()
        )

    def clean_email(self):
        data = self.cleaned_data['email']
        email = Contact.objects.filter(email=data)

        if email:
            raise forms.ValidationError(_("This email address already exists in our database!"))

        return data
