from django import forms
from django.utils.translation import ugettext_lazy as _

class RemoteSubscribeForm(forms.Form):
    username = forms.CharField(max_length=64, label=_("username"))
    profile_url = forms.URLField(label=_("OMB compatible profile URL"))

AUTHORIZE_CHOICES = (
    (1, _('Accept')),
    (0, _('Reject'))
)

class AuthorizeForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)
    authorize_access = forms.ChoiceField(choices=AUTHORIZE_CHOICES,widget=forms.RadioSelect, required=False)
