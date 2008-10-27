from django import forms

class RemoteSubscribeForm(forms.Form):
    username = forms.CharField(max_length=64, label="Username")
    profile_url = forms.URLField(label="OMB Compatable Profile URL")

AUTHORIZE_CHOICES = (
    (1, 'Accept'),
    (0, 'Reject')
)

class AuthorizeForm(forms.Form):
    token = forms.CharField(widget=forms.HiddenInput)
    authorize_access = forms.ChoiceField(choices=AUTHORIZE_CHOICES,widget=forms.RadioSelect, required=False)
