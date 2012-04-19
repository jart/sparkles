r"""

    sparkles.urls
    ~~~~~~~~~~~~~

    HTTP request routing

"""

from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.defaults import patterns, url, include
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.urls import urlpatterns as auth_urlpatterns

from sparkles import admin, utils, api

adminsite = admin.AdminSite(name="sparkles_admin")

urlpatterns = auth_urlpatterns + patterns("",
    url(r'^$', TemplateView.as_view(template_name="sparkles/index.html"), name="index"),
    url(r'^about/$', TemplateView.as_view(template_name="sparkles/about.html"), name="about"),
    url(r"^signup/$", "sparkles.views.signup", name="signup"),
    url(r"^signup/verify/$", "sparkles.views.signup_verify", name="signup_verify"),
    url(r"^error/$", "sparkles.views.error", name="error"),
    url(r"^p/new/$", "sparkles.views.proposal_new", name="proposal_new"),
    url(r"^p/(?P<sid>[a-z0-9]+)/$", "sparkles.views.proposal", name="proposal"),
    url(r"^p/(?P<sid>[a-z0-9]+)/edit/$", "sparkles.views.proposal_edit", name="proposal_edit"),
    url(r"^w/(?P<username>[a-z0-9]+)/$", "sparkles.views.workgroup", name="workgroup"),
    url(r"^u/(?P<username>[a-z0-9]+)/$", "sparkles.views.user", name="user"),
    url(r"^admin/", include(adminsite.urls)),
    url(r'^api/verify_email/$', require_POST(utils.api_view(api.verify_email))),
    url(r'^api/verify_phone/$', require_POST(utils.api_view(api.verify_phone))),
    url(r'^api/verify_xmpp/$', require_POST(utils.api_view(api.verify_xmpp))),
)
