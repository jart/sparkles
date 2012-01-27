r"""

    sparkles.views
    ~~~~~~~~~~~~~~

    Dynamic web page functions

"""

from django import forms
from django.contrib import auth
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from sparkles import models as db


def index(request):
    """I render the home page"""
    return render_to_response(
        "sparkles/index.html", {},
        context_instance=RequestContext(request))


class SignupForm(forms.Form):
    username = forms.RegexField(
        label="Username", max_length=12, regex=r'^[a-zA-Z0-9]{3,12}$',
        help_text="Required. Letters and digits only, 3-12 characters.",
        error_messages={'required': 'Please pick a username',
                        'invalid': ("Please enter only letters and digits in "
                                    "your username between 3 and 12 chars.")})
    password = forms.CharField(
        label="Passphrase", widget=forms.PasswordInput,
        min_length=6, max_length=128, help_text="At least 6 characters",
        error_messages={'required': 'Please choose a password',
                        'invalid': ("Please enter only letters and digits in "
                                    "your username between 3 and 12 chars.")})
    email = forms.EmailField(
        label='Email', help_text="Required. Email Alerts & Verification",
        widget=forms.TextInput(attrs={'placeholder': 'you@domain.com'}),
        error_messages={'required': 'Please enter your email address',
                        'invalid': 'Bad email address'})
    phone = forms.RegexField(
        label='Phone Number', required=False,
        regex=r'^[2-9]\d\d-?[2-9]\d\d-?\d\d\d\d$',
        widget=forms.TextInput(attrs={'placeholder': 'npa-nxx-xxxx'}),
        help_text='Optional. SMS notifications (US/CA Only)',
        error_messages={'required': 'Please enter your phone number',
                        'invalid': 'Bad telephone number, try xxx-yyy-zzzz'})

    def clean_username(self):
        username = self.data.get('username')
        if db.User.objects.filter(username__iexact=username).count():
            raise forms.ValidationError("Username is taken")
        return username

    def save(self):
        data = self.cleaned_data
        user = db.User.objects.create_user(
            data['username'], data['email'], data['password'])
        return user


def signup(request):
    """Create an account"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated():
                logout(request)
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()
    return render_to_response(
        "sparkles/signup.html", {'form': form},
        context_instance=RequestContext(request))


def error(request):
    """A view that's designed to fail"""
    assert False
