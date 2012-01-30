r"""

    sparkles.views
    ~~~~~~~~~~~~~~

    Dynamic web page functions

"""

from django import forms
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect

from sparkles import models as db


class SignupForm(forms.Form):
    username = forms.RegexField(
        label="My Name", max_length=12, regex=r'^[a-zA-Z][a-zA-Z0-9]{3,12}$',
        help_text=("Letters and digits only, 3-12 characters. "
                   "PLEASE PICK A USERNAME PEOPLE WILL UNDERSTAND. For "
                   "example if your friends know you as Tyler Durden, then "
                   "your username should be TylerDurden."),
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
    phone = forms.CharField(
        label='Mobile Phone',
        widget=forms.TextInput(attrs={'placeholder': '+1 (npa) nxx-xxxx'}),
        help_text='Required. Verification & SMS Alerts',
        error_messages={'required': 'Please enter your phone number',
                        'invalid': 'Bad telephone number, try xxx-yyy-zzzz'})
    xmpp = forms.EmailField(
        label='XMPP', help_text="Optional. Instant Message Alerts",
        widget=forms.TextInput(attrs={'placeholder': 'you@jabber.no'}),
        error_messages={'invalid': 'Bad xmpp address'})
    aim = forms.CharField(
        label='AIM', help_text="Optional. AOL Instant Messenger Alerts",
        widget=forms.TextInput(attrs={'placeholder': 'gothchick420'}),
        error_messages={'invalid': 'Bad AIM screen name'})

    def clean_username(self):
        username = self.data.get('username')
        if db.User.objects.filter(username__iexact=username).count():
            raise forms.ValidationError("Username is taken")
        if db.Workgroup.objects.filter(username__iexact=username).count():
            raise forms.ValidationError("Username is taken")
        if db.Proposal.objects.filter(sid=username.lower()).count():
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
            user = form.save()
            if request.user.is_authenticated():
                auth.logout(request)
            user = auth.authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password'])
            auth.login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignupForm()
    return render_to_response(
        "sparkles/signup.html", {'form': form},
        context_instance=RequestContext(request))


class ProposalForm(forms.Form):
    title = forms.CharField(
        label="Title", max_length=64,
        widget=forms.TextInput(attrs={'class': 'xxlarge'}),
        help_text="One line synopsis of proposal",
        error_messages={'required': 'Please enter a title for your proposal'})
    content = forms.EmailField(
        label='Description', required=False,
        widget=forms.Textarea(attrs={'class': 'xxlarge'}),
        help_text=("Describe the proposal in as much detail as possible here. "
                   "You can use markdown formatting"))
    invite = forms.CharField(
        label="Invitations", required=False,
        help_text="Enter usernames and workgroups to invite")
    email_blast = forms.BooleanField(
        label="Email Blast?", required=False, initial=True,
        help_text=("Should we email everyone you invited right now to get "
                   "a temperature check?"))
    sms_blast = forms.BooleanField(
        label="SMS Blast?", required=False, initial=True,
        help_text=("Should we send everyone you invited text messages?"))

    def clean_invite(self):
        invites = self.data['invites']
        return invites

    def save(self, user, prop=None):
        data = self.cleaned_data
        prop = prop or db.Prop()
        prop.sid = prop.sid or db.base36()
        prop.user = prop.user or user
        prop.title = data['title']
        prop.save()
        prop.set_content(data['content'])
        prop.log(user, 'Edited')
        for name in data['invite'].replace(',', ' ').split():
            try:
                prop.invite(name)
            except KeyError:
                pass
        return prop


def proposal(request, sid):
    """A view that's designed to fail"""
    try:
        prop = db.Proposal.objects.get(sid=sid)
    except db.Proposal.DoesNotExist:
        raise Http404()
    return render_to_response(
        "sparkles/proposal.html", {'prop': prop},
        context_instance=RequestContext(request))


def proposal_new(request):
    """Create an account"""
    signup_form = None
    if request.method == 'POST':
        if not request.user.is_authenticated():
            signup_form = SignupForm(request.POST)
        form = ProposalForm(request.POST)
        if signup_form.is_valid() and form.is_valid():
            if not request.user.is_authenticated():
                signup_form.save()
                user = auth.authenticate(
                    username=signup_form.cleaned_data['username'],
                    password=signup_form.cleaned_data['password'])
                auth.login(request, user)
            else:
                user = request.user
            prop = form.save(user)
            return HttpResponseRedirect(prop.get_absolute_url())
    else:
        if not request.user.is_authenticated():
            signup_form = SignupForm()
        form = ProposalForm()
    return render_to_response(
        "sparkles/proposal_new.html", {'form': form,
                                       'signup_form': signup_form},
        context_instance=RequestContext(request))


def proposal_edit(request, sid):
    """Create an account"""
    try:
        prop = db.Proposal.objects.get(sid=sid)
    except db.Proposal.DoesNotExist:
        raise Http404()
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            prop = form.save(user)
            return HttpResponseRedirect(prop.get_absolute_url())
    else:
        form = ProposalForm(initial={
            'title': prop.title,
            'content': prop.content,
            'is_public': prop.is_public,
            'is_inviteonly': prop.is_inviteonly,
        })
    return render_to_response(
        "sparkles/proposal_edit.html", {'prop': prop, 'form': form},
        context_instance=RequestContext(request))


def workgroup(request, username):
    """A view that's designed to fail"""
    try:
        workgroup = db.Workgroup.objects.get(username=username)
    except db.Workgroup.DoesNotExist:
        raise Http404()
    return render_to_response(
        "sparkles/workgroup.html", {'workgroup': workgroup},
        context_instance=RequestContext(request))


def user(request, username):
    """A view that's designed to fail"""
    try:
        user = db.User.objects.get(username=username)
    except db.User.DoesNotExist:
        raise Http404()
    return render_to_response(
        "sparkles/user.html", {'user': user},
        context_instance=RequestContext(request))


def error(request):
    """A view that's designed to fail"""
    assert False
