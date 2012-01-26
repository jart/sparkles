r"""

    sparkles.views
    ~~~~~~~~~~~~~~

    Dynamic web page functions

"""

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response

from sparkles import models as db


def index(request):
    """I render the home page"""
    return render_to_response(
        "sparkles/index.html", {},
        context_instance=RequestContext(request))


def error(request):
    """A view that's designed to fail"""
    assert False
