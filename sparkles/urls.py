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
    url(r'^$', TemplateView.as_view(template_name="sparkles/index.html"), name="index"),
    url(r'^about/$', TemplateView.as_view(template_name="sparkles/about.html"), name="about"),
    url(r"^signup/$", "sparkles.views.signup", name="signup"),
    url(r"^error/$", "sparkles.views.error", name="error"),
    url(r"^p/new/$", "sparkles.views.proposal_new", name="proposal_new"),
    url(r"^p/(?P<sid>[a-z0-9]+)/$", "sparkles.views.proposal", name="proposal"),
    url(r"^p/(?P<sid>[a-z0-9]+)/edit/$", "sparkles.views.proposal_edit", name="proposal_edit"),
    url(r"^w/(?P<username>[a-z0-9]+)/$", "sparkles.views.workgroup", name="workgroup"),
    url(r"^u/(?P<username>[a-z0-9]+)/$", "sparkles.views.user", name="user"),
    url(r"^login/$", 'django.contrib.auth.views.login', {'template_name': 'sparkles/index.html'}, name="login"),
    url(r"^logout/$", 'django.contrib.auth.views.logout', name="logout"),
    url(r"^admin/", include(adminsite.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^media/(?P<path>.*)$", "django.views.static.serve",
            {"document_root": settings.MEDIA_ROOT}),
    )
