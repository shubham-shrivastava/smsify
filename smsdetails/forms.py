from django import forms
from .models import SmsDetail, ContactDetail
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


class SmsDetailForm(forms.Form):
    to = forms.CharField(max_length=15)
    message_body = forms.CharField(max_length=160, required="True")

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     return super(SmsDetailForm, self).__init__(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     kwargs['commit'] = False
    #     obj = super(SmsDetailForm, self).save(*args, **kwargs)
    #     if self.request:
    #         obj.user = self.request.user
    #     obj.save()
    #     return obj


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ContactDetailForm(forms.Form):
    first_name = forms.CharField(max_length=15)
    last_name = forms.CharField(max_length=160, required=True)
    phone_num = forms.CharField(max_length=15)
    email = forms.EmailField(max_length=100, required=False)
