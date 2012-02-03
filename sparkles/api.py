r"""

    sparkles.api
    ~~~~~~~~~~~~

    Core business logic, abstracted from http request/response stuff.

    API functions must do the following:

    - Return a list or iterator.
    - Include a ``**kwargs`` argument.
    - Be able to cope with string-only arguments.
    - Raise :py:class:`APIException` if anything goes wrong.

"""

import phonenumbers
from django.core import mail
from django.conf import settings
from django.core.validators import email_re
from django.template.loader import render_to_string

from sparkles import message, utils, models as db


def _try_to_get_ip(args):
    if 'request' in args:
        return args['request'].META.get('REMOTE_ADDR', '')
    else:
        return ''


def verify_email(email, **kwargs):
    ip = _try_to_get_ip(kwargs)
    yesterday = utils.now() - utils.day
    invalid = False
    invalid |= (not email_re.match(email))
    invalid |= (db.User.objects.filter(email=email).count() > 0)
    invalid |= (db.EmailBlacklist.objects.filter(email=email).count() > 0)
    invalid |= (db.EmailVerify.objects
                .filter(email=email, created__gt=yesterday)
                .count() > settings.SPARK_AUTH_MAX_EMAIL_DAY)
    if ip:
        invalid |= (db.EmailVerify.objects
                    .filter(ip=ip, created__gt=yesterday)
                    .count() > settings.SPARK_AUTH_MAX_EMAIL_DAY)
    if invalid:
        raise utils.APIException("invalid email address")
    code = db.base36(4)
    db.EmailVerify.objects.create(email=email, code=code, ip=ip)
    body = render_to_string('sparkles/email_verify.html', {'code': code})
    msg = mail.EmailMessage('Sparkles Email Verification Code', body,
                            'noreply@sparkles.org', [email])
    msg.content_subtype = "html"
    msg.send()
    return []


def verify_phone(phone, **kwargs):
    phone = phonenumbers.parse(phone, 'US')
    if not phonenumbers.is_valid_number(phone):
        raise utils.APIException("Invalid phone number")
    if phone.country_code != 1:
        raise utils.APIException('We only support US/CA numbers now :(')
    phone = utils.e164(phone)
    ip = _try_to_get_ip(kwargs)
    yesterday = utils.now() - utils.day
    invalid = False
    invalid |= (db.UserInfo.objects.filter(phone=phone).count() > 0)
    invalid |= (db.PhoneBlacklist.objects.filter(phone=phone).count() > 0)
    invalid |= (db.PhoneVerify.objects
                .filter(phone=phone, created__gt=yesterday)
                .count() > settings.SPARK_AUTH_MAX_PHONE_DAY)
    if ip:
        invalid |= (db.PhoneVerify.objects
                    .filter(ip=ip, created__gt=yesterday)
                    .count() > settings.SPARK_AUTH_MAX_PHONE_DAY)
    if invalid:
        raise utils.APIException("invalid phone number")
    code = db.base36(4)
    db.PhoneVerify.objects.create(phone=phone, code=code, ip=ip)
    message.sms_send(phone, 'sparkles phone auth code: ' + code)
    return []


def verify_xmpp(xmpp, **kwargs):
    ip = _try_to_get_ip(kwargs)
    yesterday = utils.now() - utils.day
    invalid = False
    invalid |= (not email_re.match(xmpp))
    invalid |= (db.UserInfo.objects.filter(xmpp=xmpp).count() > 0)
    invalid |= (db.XmppVerify.objects
                .filter(xmpp=xmpp, created__gt=yesterday)
                .count() > settings.SPARK_AUTH_MAX_XMPP_DAY)
    if ip:
        invalid |= (db.XmppVerify.objects
                    .filter(ip=ip, created__gt=yesterday)
                    .count() > settings.SPARK_AUTH_MAX_XMPP_DAY)
    if invalid:
        raise utils.APIException("invalid xmpp address")
    code = db.base36(4)
    db.XmppVerify.objects.create(xmpp=xmpp, code=code, ip=ip)
    message.xmpp_send(xmpp, 'sparkles xmpp auth code: ' + code)
    return []
