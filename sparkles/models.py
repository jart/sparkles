r"""

    sparkles.models
    ~~~~~~~~~~~~~~~

    Tools for accessing data.

"""

import redis
# import datetime
import functools

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
# from django.utils.timezone import utc


redis = redis.StrictRedis()
rng = open('/dev/urandom')


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
    phone = models.CharField(max_length=32, blank=True, help_text="""
        Phone number for SMS alerts in +E.164 format""")

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
    """A model for fabulous ideas"""
    username = models.CharField(max_length=255, unique=True, help_text="""
        A unique name with only letters and numbers""")
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    content = models.TextField(blank=True, help_text="""
        A description of this group""")
    is_public = models.BooleanField(default=True, help_text="""
        Is this a secret shadow group?""")
    is_inviteonly = models.BooleanField(default=False, help_text="""
        Assuming it's public, can anyone just decide to join?""")

    @models.permalink
    def get_absolute_url(self):
        return ('sparkles.views.workgroup', [self.username])

    class Meta:
        ordering = ("-created",)


class WorkgroupMember(models.Model):
    """Associate users with a working group"""
    workgroup = models.ForeignKey(Workgroup, related_name='members')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When did they join?""")

    class Meta:
        unique_together = ("workgroup", "user")
        ordering = ("user__username",)


class Proposal(models.Model):
    """A model for fabulous ideas"""
    sid = models.CharField(max_length=255, unique=True, help_text="""
        A randomly generated secure id for URLs""")
    user = models.ForeignKey(User, help_text="""
        Who started this proposal?""")
    title = models.CharField(max_length=255, help_text="""
        A single line description""")
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    workgroup = models.ForeignKey(
        Workgroup, null=True, blank=True, related_name='proposals',
        help_text="Optionally associate proposal with a working group")

    @models.permalink
    def get_absolute_url(self):
        return ('sparkles.views.proposal', [self.sid])

    @property
    @memoize
    def content(self):
        return self.texts.all()[0]

    def set_content(self, content):
        ProposalText.objects.create(prop=self, content=content)

    def log(self, user, content):
        ProposalLog.objects.create(prop=self, user=user, content=content)

    def invite(self, name):
        try:
            self.invite_user(User.objects.get(username=name))
        except User.DoesNotExist:
            try:
                self.invite_workgroup(Workgroup.objects.get(username=name))
            except Workgroup.DoesNotExist:
                raise KeyError("'%s' not a user or workgroup" % (name))

    def invite_user(self, user):
        ProposalMember.objects.create(prop=self, user=user)
        # todo: email

    def invite_workgroup(self, workgroup):
        for member in workgroup.members.all():
            self.invite_user(member.user)

    class Meta:
        ordering = ("-created",)


class ProposalText(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='texts')
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this first created?""")
    content = models.TextField(blank=True, help_text="""
        The text of the proposal in markdown""")

    class Meta:
        ordering = ("-created",)


class ProposalLog(models.Model):
    """Proposal text revisions"""
    prop = models.ForeignKey(Proposal, related_name='logs')
    user = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When was this log entry emitted?""")
    content = models.TextField(help_text="""
        Arbitrary line of text in markdown""")

    class Meta:
        ordering = ("-created",)


class ProposalMember(models.Model):
    """Who is actually participating in a proposal?"""
    prop = models.ForeignKey(Proposal, related_name='members')
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When were they invited to collaborate?""")

    class Meta:
        unique_together = ("prop", "user")
        ordering = ("user__username",)


class ProposalMemberVote(models.Model):
    """How did they feel as the proposal evolved?"""
    VOTE_CHOICES = (
        ('', 'Unanswered'),
        ('up', 'Up Sparkle'),
        ('mid', 'Mid Sparkle'),
        ('down', 'Down Sparkle'),
        ('block', 'Block'),
        ('abstain', 'Abstain'),
    )

    prop = models.ForeignKey(Proposal, related_name='votes')
    member = models.ForeignKey(ProposalMember, related_name='votes')
    created = models.DateTimeField(auto_now_add=True, help_text="""
        When were they invited to collaborate?""")
    vote = models.CharField(max_length=255, choices=VOTE_CHOICES, help_text="""
        How do you feel?""")

    class Meta:
        unique_together = ("prop", "member")
        ordering = ("-created",)
