r"""

    sparkles.models
    ~~~~~~~~~~~~~~~

    Database table definitions.

    Secure identifiers (sid) and usernames must be unique across all tables.

"""

import json
import logging
import functools

import redis
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)
redisc = redis.StrictRedis()
rng = open('/dev/urandom')


def is_used(sid):
    """Ensure this resource identifier isn't being used anywhere"""
    sid = sid.lower()
    return (User.objects.filter(username__iexact=sid).count() or
            Workgroup.objects.filter(username__iexact=sid).count() or
            Proposal.objects.filter(sid=sid).count())


def memoize(method):
    """Memoize decorator for methods taking no arguments
    """
    @functools.wraps(method)
    def _memoize(instance):
        key = method.__name__ + '__memoize'
        if not hasattr(instance, key):
            res = method(instance)
            setattr(instance, key, res)
        else:
            res = getattr(instance, key)
        return res
    return _memoize


def base36(amt=7):
    choices = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join([choices[ord(b) % 36] for b in rng.read(amt)])


def user_dict(user):
    return {
        'id': user.id,
        'email': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


class UserInfo(models.Model):
    """Extra DB information to associate with a Django auth user"""
    user = models.OneToOneField(User, editable=False, help_text="""
        Reference to Django auth user.""")
    content = models.TextField(blank=True, help_text="""
        Some profile or "about me" information.""")
    phone = models.CharField(max_length=255, blank=True, help_text="""
        Phone number for SMS alerts in +E.164 format""")
    xmpp = models.CharField(max_length=255, blank=True, help_text="""
        XMPP/Jabber instant messaging address""")

    class Meta:
        verbose_name = 'User Info'
        verbose_name_plural = 'User Infos'

    def __unicode__(self):
        return unicode(self.user)


@receiver(models.signals.post_save, sender=User)
def ensure_userinfo(sender, instance, **kwargs):
    """When a User object is saved, ensure associated UserInfo exists"""
    if not UserInfo.objects.filter(user=instance).count():
        instance.userinfo = UserInfo.objects.create(user=instance)


class Workgroup(models.Model):
    """Represents a group of users working towards a common goal

    Workgroups are a convenient way to get a temperature check from everyone
    in your affinity group without having to remember every person's name and
    inviting them one by one for each proposal.
    """
    username = models.CharField(max_length=255, unique=True, help_text="""
        A unique name with only letters and numbers""")
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    content = models.TextField(blank=True, help_text="""
        A description of this group""")
    members = models.ManyToManyField(User, through='WorkgroupMember')

    @models.permalink
    def get_absolute_url(self):
        return ('sparkles.views.workgroup', [self.username])


class WorkgroupMember(models.Model):
    """Associate users with a working group"""
    workgroup = models.ForeignKey(Workgroup)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When did they join?""")
    is_admin = models.BooleanField(help_text="""
        Facilitators have special powers like removing members""")

    class Meta:
        unique_together = ("workgroup", "user")
        ordering = ("user__username",)


class WorkgroupInvite(models.Model):
    """Ask someone to join your workgroup"""
    STATUSES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    )

    workgroup = models.ForeignKey(Workgroup)
    user = models.ForeignKey(User, related_name='workgroup_invites')
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STATUSES,
                              default='pending')
    is_viewed = models.BooleanField()
    content = models.TextField(blank=True, help_text="A personalized message")

    class Meta:
        unique_together = ("workgroup", "user")


class WorkgroupRequest(models.Model):
    """Ask facilitators if you can join workgroup"""
    STATUSES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    )

    workgroup = models.ForeignKey(Workgroup)
    user = models.ForeignKey(User, related_name='workgroup_requests')
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STATUSES,
                              default='pending')
    is_viewed = models.BooleanField()
    content = models.TextField(blank=True, help_text="A personalized message")

    class Meta:
        unique_together = ("workgroup", "user")


class Proposal(models.Model):
    """We need to make a decision"""
    sid = models.CharField(max_length=255, unique=True, help_text="""
        A randomly generated secure id for urls""")
    workgroup = models.ForeignKey(Workgroup)
    title = models.CharField(max_length=255, help_text="""
        A single line description""")
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")

    @models.permalink
    def get_absolute_url(self):
        return ('sparkles.views.proposal', [self.sid])

    def get_content(self):
        return self.texts.order_by('-created')[0]

    def set_content(self, user, content):
        p = ProposalText.objects.create(prop=self, user=user, content=content)
        p.publish()

    content = property(get_content, set_content)

    def log(self, user, content):
        p = ProposalLog.objects.create(prop=self, user=user, content=content)
        p.publish()


class ProposalText(models.Model):
    """Proposal texts with revisions"""
    prop = models.ForeignKey(Proposal, related_name='texts')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    content = models.TextField(blank=True, help_text="""
        The text of the proposal in markdown""")

    def publish(self):
        redisc.publish('sparkles-event', json.dumps({
            'channel': 'proposal-' + self.prop.sid,
            'type': 'text',
            'text': {
                'content': self.content,
                'created': self.created.strftime("%s"),
                'user': user_dict(self.user),
            }
        }))


class ProposalChat(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='chats')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this log entry emitted?""")
    content = models.TextField(help_text="""
        Arbitrary line of text in markdown""")

    def publish(self):
        redisc.publish('sparkles-event', json.dumps({
            'channel': 'proposal-' + self.prop.sid,
            'type': 'chat',
            'chat': {
                'content': self.content,
                'created': self.created.strftime("%s"),
                'user': user_dict(self.user),
            }
        }))


class ProposalLog(models.Model):
    """Proposal action log"""
    prop = models.ForeignKey(Proposal, related_name='logs')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this log entry emitted?""")
    content = models.TextField(help_text="""
        Arbitrary line of text in markdown""")

    def publish(self):
        redisc.publish('sparkles-event', json.dumps({
            'channel': 'proposal-' + self.prop.sid,
            'type': 'log',
            'log': {
                'content': self.content,
                'created': self.created.strftime("%s"),
                'user': user_dict(self.user),
            }
        }))


class ProposalVote(models.Model):
    """A person's vote and justification with revisions"""
    VOTES = (
        ('', 'Pending'),
        ('absgood', 'Absolute Support'),
        ('good', 'Support'),
        ('mid', 'Middling'),
        ('bad', 'Opposed'),
        ('absbad', 'Absolute Oppose'),
        ('abstain', 'Abstain'),
    )

    prop = models.ForeignKey(Proposal, related_name='votes')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When were they invited to collaborate?""")
    vote = models.CharField(max_length=255, choices=VOTES, help_text="""
        How do you feel?""")
    content = models.TextField(blank=True, help_text="""
        Why do you feel this way?""")

    def publish(self):
        redisc.publish('sparkles-event', json.dumps({
            'channel': 'proposal-' + self.prop.sid,
            'type': 'vote',
            'vote': {
                'vote': self.vote,
                'content': self.content,
                'created': self.created.strftime("%s"),
                'user': user_dict(self.user),
            }
        }))


class EmailBlacklist(models.Model):
    """Never email these people under any circumstances"""
    email = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    class Meta:
        verbose_name = 'Blacklisted Email'
        verbose_name_plural = 'Email Blacklist'


class PhoneBlacklist(models.Model):
    """Never call/text these people under any circumstances"""
    phone = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

    class Meta:
        verbose_name = 'Blacklisted Phone Number'
        verbose_name_plural = 'Phone Number Blacklist'


class EmailVerify(models.Model):
    """Record of each time we issue an email authorization code"""
    email = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("email", "code")
        verbose_name = 'Email Verification Entry'
        verbose_name_plural = 'Email Verification Log'


class PhoneVerify(models.Model):
    """Record of each time we issue an phone authorization code"""
    phone = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("phone", "code")
        verbose_name = 'Phone Verification Entry'
        verbose_name_plural = 'Phone Verification Log'


class XmppVerify(models.Model):
    """Record of each time we issue an xmpp authorization code"""
    xmpp = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=255)
    ip = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("xmpp", "code")
        verbose_name = 'XMPP Verification Entry'
        verbose_name_plural = 'XMPP Verification Log'


class SmsMessage(models.Model):
    """History of all sent/received sms messages"""
    created = models.DateTimeField(auto_now_add=True)
    to_addr = models.CharField(max_length=255, help_text="""
        Recipient's phone number in +E.164""")
    from_addr = models.CharField(max_length=255, help_text="""
        Sender's phone number in +E.164""")
    content = models.CharField(max_length=160)
    is_egress = models.BooleanField(help_text="""
        True if this message was sent by us""")

    class Meta:
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'


class XmppMessage(models.Model):
    """History of all sent/received xmpp messages"""
    created = models.DateTimeField(auto_now_add=True)
    to_addr = models.CharField(max_length=255, help_text="""
        Recipient's XMPP JID""")
    from_addr = models.CharField(max_length=255, help_text="""
        Sender's XMPP JID""")
    content = models.TextField()
    is_egress = models.BooleanField(help_text="""
        True if this message was sent by us""")

    class Meta:
        verbose_name = 'XMPP Message'
        verbose_name_plural = 'XMPP Messages'
