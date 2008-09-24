from django import forms

class RemoteSubscribeForm(forms.Form):
    username = forms.CharField(max_length=64, label="Username")
    profile_url = forms.CharField(label="OMB Compatable Profile URL")