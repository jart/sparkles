r"""

    sparkles.utils
    ~~~~~~~~~~~~~~

    Miscellaneous functions that help you.

"""

import json
import time
import logging
import traceback
from decimal import Decimal
from functools import wraps
from datetime import datetime, timedelta

import phonenumbers
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils.timezone import utc


logger = logging.getLogger(__name__)
day = timedelta(days=1)


class APIException(Exception):
    """Causes API wrapper to return an error result"""
    def __init__(self, message, results=[]):
        self.message = message
        self.results = results

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<APIException: %s>" % (self)


def api_view(function):
    """Decorator that turns a function into a Django JSON API view

    Your function must return a list of results which are expressed as
    normal Python data structures.  If something bad happens you
    should raise :py:class:`APIException`.

    This function also catches general exceptions to ensure the client
    always receives data in JSON format.

    API functions that have side-effects should be wrapped in a
    ``require_POST`` decorator in your ``url.py`` file to ensure CSRF
    protection, otherwise they should be wrapped in ``require_GET``.
    """
    @wraps(function)
    @transaction.commit_manually
    def _api_view(request):
        args = {}
        args.update(request.REQUEST)
        args['request'] = request
        args['user'] = request.user
        try:
            data = list(function(**args))
        except APIException, exc:
            res = {'status': 'ERROR',
                   'message': str(exc),
                   'results': list(getattr(exc, 'results', None))}
            transaction.rollback()
        except Exception, exc:
            traceback.print_exc()
            logger.exception('api request failed')
            res = {'status': 'ERROR',
                   'message': 'system malfunction',
                   'results': []}
            transaction.rollback()
            if getattr(settings, 'TEST_MODE', False):
                raise
        else:
            if data:
                res = {'status': 'OK',
                       'message': 'success',
                       'results': data}
            else:
                res = {'status': 'ZERO_RESULTS',
                       'message': 'no data returned',
                       'results': data}
            transaction.commit()
        logger.info("api %s returning %s: %s" %
                    (request.path, res['status'], res['message']))
        return _as_json(res)
    return _api_view


def _as_json(data):
    """Turns API result into JSON data"""
    data['results'] = sanitize_json(data['results'])
    if settings.DEBUG:
        content = json.dumps(data, indent=2) + '\n'
    else:
        content = json.dumps(data)
    response = HttpResponse(content, mimetype="application/json")
    return response


def jsonify(value, **argv):
    return json.dumps(sanitize_json(value), **argv)


def sanitize_json(value):
    if hasattr(value, 'as_dict'):
        return sanitize_json(value.as_dict())
    elif hasattr(value, 'timetuple'):
        return jstime(value)
    elif isinstance(value, Decimal):
        return str(value)
    elif isinstance(value, basestring):
        return value
    elif isinstance(value, dict):
        for k in value:
            value[k] = sanitize_json(value[k])
        return value
    elif hasattr(value, '__iter__'):
        return [sanitize_json(i) for i in value]
    else:
        return value


def jstime(dt):
    """Convert datetime object to javascript timestamp

    In javascript, timestamps are represented as milliseconds since the UNIX
    epoch in UTC. Therefore the datetime object you pass to this function must
    be in UTC.
    """
    ts = int(time.mktime(dt.timetuple())) * 1000
    if hasattr(dt, 'microsecond'):
        ts += dt.microsecond / 1000
    return ts


def now():
    """Shortcut function to get current timestamp with timezone set"""
    return datetime.utcnow().replace(tzinfo=utc)


def e164(phone):
    """Shortcut for turning phone object into E.164 string"""
    return phonenumbers.format_number(
        phone, phonenumbers.PhoneNumberFormat.E164)
