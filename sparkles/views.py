r"""

    sparkles.views
    ~~~~~~~~~~~~~~

    Dynamic web page functions

"""

import phonenumbers
from django import forms
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from sparkles import utils, api, models as db


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
        help_text='Required. Verification & SMS Alerts (US/CA only)',
        widget=forms.TextInput(attrs={'placeholder': 'npa-nxx-xxxx'}),
        error_messages={'required': 'Please enter your phone number',
                        'invalid': 'Bad telephone number, try xxx-yyy-zzzz'})
    xmpp = forms.EmailField(
        label='XMPP', required=False,
        help_text="Optional. XMPP/Jabber Instant Message Alerts",
        widget=forms.TextInput(attrs={'placeholder': 'you@jabber.org'}),
        error_messages={'invalid': 'Bad xmpp address'})

    def clean_username(self):
        username = self.data.get('username')
        if db.is_used(username):
            raise forms.ValidationError("Username is taken")
        return username

    def clean_email(self):
        email = self.data.get('email')
        invalid = False
        invalid |= (db.User.objects.filter(email=email).count() > 0)
        invalid |= (db.EmailBlacklist.objects.filter(email=email).count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect email verify code")
        return email

    def clean_phone(self):
        phone = phonenumbers.parse(self.data.get('phone'), 'US')
        if not phonenumbers.is_valid_number(phone):
            raise forms.ValidationError("Invalid phone number")
        if phone.country_code != '1':
            raise forms.ValidationError('We only support US/CA numbers now')
        phone = utils.e164(phone)
        invalid = False
        invalid |= (db.UserInfo.objects.filter(phone=phone).count() > 0)
        invalid |= (db.PhoneBlacklist.objects.filter(phone=phone).count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect phone verify code")
        return phone

    def clean_xmpp(self):
        xmpp = self.data.get('xmpp')
        if not xmpp:
            return ''
        invalid = False
        invalid |= (db.UserInfo.objects.filter(xmpp=xmpp).count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect xmpp verify code")
        return xmpp


class SignupVerifyForm(forms.Form):
    email_code = forms.CharField(
        label="Email Verification Code",
        help_text="Please check your email inbox for the code we sent you",
        error_messages={'required': 'Please enter email address verify code'})
    phone_code = forms.CharField(
        label="Phone Verification Code",
        help_text="Please check your text messages for the code we sent you",
        error_messages={'required': 'Please enter phone number verify code'})
    xmpp_code = forms.CharField(
        label="XMPP Verification Code", required=False)

    def clean_email(self):
        email = self.data.get('email')
        code = self.data.get('email_code')
        invalid = False
        invalid |= (db.User.objects.filter(email=email).count() > 0)
        invalid |= (db.EmailBlacklist.objects.filter(email=email).count() > 0)
        invalid |= (db.EmailVerify.objects
                    .filter(email=email, code__iexact=code)
                    .count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect email verify code")

    def clean_phone(self):
        phone = self.data.get('phone')
        code = self.data.get('phone_code')
        invalid = False
        invalid |= (db.UserInfo.objects.filter(phone=phone).count() > 0)
        invalid |= (db.PhoneBlacklist.objects.filter(phone=phone).count() > 0)
        invalid |= (db.PhoneVerify.objects
                    .filter(phone=phone, code__iexact=code)
                    .count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect phone verify code")

    def clean_xmpp(self):
        xmpp = self.data.get('xmpp')
        code = self.data.get('xmpp_code')
        if not xmpp:
            return
        if not code:
            raise forms.ValidationError("Please enter XMPP verify code")
        invalid = False
        invalid |= (db.UserInfo.objects.filter(xmpp=xmpp).count() > 0)
        invalid |= (db.XmppVerify.objects
                    .filter(xmpp=xmpp, code__iexact=code)
                    .count() > 0)
        if invalid:
            raise forms.ValidationError("Incorrect XMPP verify code")


def signup(request):
    """Create an account (Step 1)"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            api.verify_email(form.cleaned_data['email'])
            api.verify_phone(form.cleaned_data['phone'])
            if form.cleaned_data['xmpp']:
                api.verify_xmpp(form.cleaned_data['xmpp'])
            request.session['signup'] = form.cleaned_data
            return HttpResponseRedirect('/')
    else:
        form = SignupForm(initial=request.session.get('signup', {}))
    return render_to_response(
        "sparkles/signup.html", {'form': form},
        context_instance=RequestContext(request))


def signup_verify(request):
    """Create an account (Step 2)"""
    if 'signup' not in request.session:
        HttpResponseRedirect('..')
    if request.method == 'POST':
        data = request.POST.copy()
        data.update(request.session['signup'])
        form = SignupVerifyForm(data)
        if form.is_valid():
            data = form.cleaned_data
            user = db.User.objects.create_user(
                data['username'], data['email'], data['password'])
            user.userinfo.phone = data['phone']
            user.userinfo.xmpp = data['xmpp']
            user.userinfo.save()
            if not request.user.is_authenticated():
                user = auth.authenticate(username=data['username'],
                                         password=data['password'])
                auth.login(request, user)
            del request.session['signup']
            return HttpResponseRedirect('/')
    else:
        form = SignupVerifyForm(initial=request.session['signup'])
    return render_to_response(
        "sparkles/signup_verify.html", {'form': form,
                                        'data': request.session['signup']},
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


@login_required
def proposal(request, sid):
    """A view that's designed to fail"""
    try:
        prop = db.Proposal.objects.get(sid=sid)
    except db.Proposal.DoesNotExist:
        raise Http404()
    return render_to_response(
        "sparkles/proposal.html", {'prop': prop},
        context_instance=RequestContext(request))


@login_required
def proposal_new(request):
    """Create an account"""
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            prop = form.save(request.user)
            return HttpResponseRedirect(prop.get_absolute_url())
    else:
        form = ProposalForm()
    return render_to_response(
        "sparkles/proposal_new.html", {'form': form},
        context_instance=RequestContext(request))


@login_required
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


@login_required
def workgroup(request, username):
    """View a workgroup profile"""
    try:
        workgroup = db.Workgroup.objects.get(username=username)
    except db.Workgroup.DoesNotExist:
        raise Http404()
    return render_to_response(
        "sparkles/workgroup.html", {'workgroup': workgroup},
        context_instance=RequestContext(request))


@login_required
def user(request, username):
    """View a user profile"""
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
