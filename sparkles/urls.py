r"""

    sparkles.urls
    ~~~~~~~~~~~~~

    HTTP request routing

"""

from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.defaults import patterns, url, include
from django.views.decorators.http import require_GET, require_POST

from sparkles.admin import AdminSite

adminsite = AdminSite(name="sparkles_admin")

urlpatterns = patterns("",
    url(r"^$", "sparkles.views.index", name="index"),
    url(r"^signup/$", "sparkles.views.signup", name="signup"),
    url(r'^about/$', TemplateView.as_view(template_name="sparkles/about.html"), name="about"),
    url(r"^error/$", "sparkles.views.error", name="error"),
    url(r"^admin/", include(adminsite.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^media/(?P<path>.*)$", "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT}),
    )
