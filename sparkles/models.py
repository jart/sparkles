r"""

    sparkles.models
    ~~~~~~~~~~~~~~~

    Database definition

"""

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User

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
