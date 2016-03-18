from django import forms

class NameForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.CharField(label='Your email address', widget=forms.EmailInput())
    email2 = forms.CharField(label='Re-enter email address', widget=forms.EmailInput())
    password = forms.CharField(label='Choose a password', widget=forms.PasswordInput(), min_length=8)
    password2 = forms.CharField(label='Re-enter password', widget=forms.PasswordInput(), min_length=8)

class LoginForm(forms.Form):
    email = forms.CharField(label='Your email address', widget=forms.EmailInput())
    password = forms.CharField(label='Choose a password', widget=forms.PasswordInput())
