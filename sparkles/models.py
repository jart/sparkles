r"""

    sparkles.models
    ~~~~~~~~~~~~~~~

    Database definition

"""

from django.db import models
from django.contrib.auth.models import User


# class Article(models.Model):
#     """An example table for storing your blog entries"""
#     author = models.ForeignKey(User, help_text="""
#         The user who wrote this article.""")
#     title = models.CharField(max_length=255, help_text="""
#         A one-line title to describe article.""")
#     slug = models.SlugField(unique=True, help_text="""
#         A label for this article to appear in the url.  DO NOT change
#         this once the article has been published.""")
#     published = models.DateTimeField(help_text="""
#         When was article was published?""")
#     content = models.TextField(blank=True, help_text="""
#         The contents of the article""")
#     is_published = models.BooleanField(default=False, help_text="""
#         Should it be listed on the website and syndicated?""")
#
#     def __unicode__(self):
#         return "Article \"%s\" by %s" % (self.title, self.author)
#
#     @models.permalink
#     def get_absolute_url(self):
#         return ('article', [self.slug])

