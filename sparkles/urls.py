r"""

    sparkles.urls
    ~~~~~~~~~~~~~

    HTTP request routing

"""

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.views.decorators.http import require_GET, require_POST

from sparkles.admin import AdminSite

adminsite = AdminSite(name="sparkles_admin")

urlpatterns = patterns("",
    url(r"^$", "sparkles.views.index", name="index"),
    # url(r"^article/(?P<slug>[-_\d\w]+)/$", "sparkles.views.article", name="article"),
    url(r"^error/$", "sparkles.views.error", name="error"),
    url(r"^admin/", include(adminsite.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^media/(?P<path>.*)$", "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT}),
    )
