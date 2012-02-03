r"""

    sparkles.models
    ~~~~~~~~~~~~~~~

    Database table definitions.

    Secure identifiers (sid) and usernames must be unique across all tables.

"""

import logging
import functools

import redis
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)
redis = redis.StrictRedis()
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


class Friend(models.Model):
    """Allow two users to be able to interract with one another

    Being friends with someone allows you to add them to proposals.  You'll
    also be able to follow what they're doing in the status feed.

    For each (user1, user2) entry there MUST BE a corresponding (user2, user1)
    entry.
    """
    user = models.ForeignKey(User, related_name='friend_user_set')
    friend = models.ForeignKey(User, related_name='friend_friend_set')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "friend")
        ordering = ("user__username", "friend__username")


class FriendRequest(models.Model):
    """Ask someone to be your friend

    Once you're friends with someone, that's it! Trust is established and they
    can add you to whatever goofy proposal they want, thereby bombarding your
    phone with text messages. So friend wisely my friends.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    )

    user = models.ForeignKey(User, related_name='friendrequest_user_set')
    friend = models.ForeignKey(User, related_name='friendrequest_friend_set')
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES,
                              default='pending')
    is_viewed = models.BooleanField()

    class Meta:
        unique_together = ("user", "friend")


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

    class Meta:
        ordering = ("-created",)


class WorkgroupMember(models.Model):
    """Associate users with a working group"""
    workgroup = models.ForeignKey(Workgroup)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When did they join?""")
    is_admin = models.BooleanField()

    class Meta:
        unique_together = ("workgroup", "user")
        ordering = ("user__username",)


class Proposal(models.Model):
    """A model for fabulous ideas"""
    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('semipub', 'Semi-Public'),
        ('private', 'Private'),
    )

    sid = models.CharField(max_length=255, unique=True, help_text="""
        A randomly generated secure id for urls""")
    user = models.ForeignKey(User, help_text="""
        Who started this proposal?""")
    title = models.CharField(max_length=255, help_text="""
        A single line description""")
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    privacy = models.CharField(max_length=255, choices=PRIVACY_CHOICES,
                               default='semipub', help_text="""
        Semi-public is the default which means anyone who's friends with a
        member can see this proposal. Public means anyone can see it. In
        public and semi-public mode, any member can add more members. Private
        means that only members can view the proposal and the only person
        who can add more members is the one who created the proposal.""")

    @models.permalink
    def get_absolute_url(self):
        return ('sparkles.views.proposal', [self.sid])

    @property
    @memoize
    def content(self):
        return self.texts.all()[0]

    def set_content(self, user, content):
        ProposalText.objects.create(prop=self, user=user, content=content)

    def log(self, user, content):
        ProposalLog.objects.create(prop=self, user=user, content=content)

    def invite(self, inviter, name):
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            try:
                workgroup = Workgroup.objects.get(username=name)
            except Workgroup.DoesNotExist:
                raise KeyError("'%s' not a user or workgroup" % (name))
            else:
                self.invite_workgroup(inviter, workgroup)
                self.log(inviter, 'invited #%s' % (workgroup.username))
        else:
            self.invite_user(inviter, user)
            self.log(inviter, 'invited @%s' % (user.username))

    def invite_workgroup(self, inviter, workgroup):
        for member in workgroup.members.all():
            self.invite_user(inviter, member.user)

    def invite_user(self, inviter, user):
        ProposalMember.objects.create(prop=self, inviter=inviter, user=user)
        # todo: email

    class Meta:
        ordering = ("-created",)


class ProposalMember(models.Model):
    """Who is actually participating in a proposal?"""
    prop = models.ForeignKey(Proposal, related_name='members')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When were they invited to collaborate?""")
    is_abstain = models.BooleanField()

    class Meta:
        unique_together = ("prop", "user")
        ordering = ("user__username",)


class ProposalText(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='texts')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    content = models.TextField(blank=True, help_text="""
        The text of the proposal in markdown""")

    class Meta:
        ordering = ("-created",)


class ProposalChat(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='chats')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this log entry emitted?""")
    content = models.TextField(help_text="""
        Arbitrary line of text in markdown""")

    class Meta:
        ordering = ("-created",)


class ProposalLog(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='logs')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this log entry emitted?""")
    content = models.TextField(help_text="""
        Arbitrary line of text in markdown""")

    class Meta:
        ordering = ("-created",)


class ProposalVote(models.Model):
    """How did they feel as the proposal evolved?"""
    VOTE_CHOICES = (
        ('', 'Unanswered'),
        ('up', 'Up Sparkle'),
        ('mid', 'Mid Sparkle'),
        ('down', 'Down Sparkle'),
        ('block', 'Block'),
    )

    prop = models.ForeignKey(Proposal, related_name='votes')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When were they invited to collaborate?""")
    vote = models.CharField(max_length=255, choices=VOTE_CHOICES, help_text="""
        How do you feel?""")

    class Meta:
        unique_together = ("prop", "user")
        ordering = ("-created",)


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
