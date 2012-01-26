r"""

    sparkles.admin
    ~~~~~~~~~~~~~~

    Django admin gui customization

"""

import reversion
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
        # self.register(db.Article, ArticleAdmin)


# class ArticleAdmin(reversion.VersionAdmin):
#     """Version controlled blog entry manager for Django Admin"""
#     list_display = ('title', 'author', 'published', 'is_published')
#     list_filter = ('is_visible',)
#     search_fields = ('title', 'content', 'author__username')
#     prepopulated_fields = {"slug": ("title",)}
#     history_latest_first = True
