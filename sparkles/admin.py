r"""

    sparkles.admin
    ~~~~~~~~~~~~~~

    Django admin gui customization

"""

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

from sparkles import models as db


class AdminSite(admin.AdminSite):
    """Subclassed admin site (to avoid running code in global scope)"""

    def __init__(self, *args, **kwargs):
        admin.AdminSite.__init__(self, *args, **kwargs)
        self.register(User, UserAdmin)
        self.register(Group, GroupAdmin)
        self.register(db.Workgroup, WorkgroupAdmin)
        self.register(db.Proposal, ProposalAdmin)
        self.register(db.EmailBlacklist, EmailBlacklistAdmin)
        self.register(db.PhoneBlacklist, PhoneBlacklistAdmin)
        self.register(db.EmailVerify, EmailVerifyAdmin)
        self.register(db.PhoneVerify, PhoneVerifyAdmin)
        self.register(db.XmppVerify, XmppVerifyAdmin)
        self.register(db.SmsMessage, SmsMessageAdmin)
        self.register(db.XmppMessage, XmppMessageAdmin)


class ProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'user', 'workgroup')
    search_fields = ('title',)
    date_hierarchy = 'created'
    history_latest_first = True


class WorkgroupAdmin(admin.ModelAdmin):
    list_display = ('username', 'created')
    search_fields = ('username',)
    date_hierarchy = 'created'
    history_latest_first = True


class EmailBlacklistAdmin(admin.ModelAdmin):
    list_display = ('email', 'created', 'reason')
    search_fields = ('email', 'reason')
    date_hierarchy = 'created'
    history_latest_first = True


class PhoneBlacklistAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created', 'reason')
    search_fields = ('phone', 'reason')
    date_hierarchy = 'created'
    history_latest_first = True


class EmailVerifyAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created', 'ip')
    search_fields = ('email', 'code', 'ip')
    date_hierarchy = 'created'
    history_latest_first = True


class PhoneVerifyAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created', 'ip')
    search_fields = ('phone', 'code', 'ip')
    date_hierarchy = 'created'
    history_latest_first = True


class XmppVerifyAdmin(admin.ModelAdmin):
    list_display = ('xmpp', 'code', 'created', 'ip')
    search_fields = ('xmpp', 'code', 'ip')
    date_hierarchy = 'created'
    history_latest_first = True


class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'created', 'from_addr', 'to_addr', 'is_egress')
    list_filter = ('is_egress',)
    search_fields = ('content', 'from_addr', 'to_addr')
    date_hierarchy = 'created'
    history_latest_first = True


class XmppMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'created', 'from_addr', 'to_addr', 'is_egress')
    list_filter = ('is_egress',)
    search_fields = ('content', 'from_addr', 'to_addr')
    date_hierarchy = 'created'
    history_latest_first = True
