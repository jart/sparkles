"""

    sparkles.message
    ~~~~~~~~~~~~~~~~

    Message service integration.

    http://web.sarathlakshman.com/Articles/XMPP.pdf

"""

import logging

import xmpp
from django.conf import settings
from twilio.rest import TwilioRestClient

from sparkles import models as db


_client = None
logger = logging.getLogger(__name__)


def xmpp_client():
    """Lazily connect/auth XMPP client"""
    global _client
    if _client and _client.isConnected():
        return _client
    jid = xmpp.JID(settings.XMPP_JID)
    client = xmpp.Client(jid.domain)
    client.connect(server=settings.XMPP_SERVER)
    client.auth(jid.node, settings.XMPP_PASSWORD, jid.resource)
    client.RegisterHandler('message', xmpp_on_message)
    client.sendInitPresence(requestRoster=0)
    _client = client
    client.jid = jid
    return client


def xmpp_send(to, content):
    from_ = settings.XMPP_JID
    logger.info("xmpp %s -> %s: %s", from_, to, content)
    if not settings.DEBUG and not getattr(settings, 'TEST_MODE', False):
        xmpp_client().send(xmpp.Message(to, content))
    db.XmppMessage.objects.create(to_addr=to,
                                  from_addr=from_,
                                  content=content,
                                  is_egress=True)


def xmpp_on_message(client, message):
    to = message.getTo()
    from_ = message.getFrom()
    content = message.getBody()
    db.XmppMessage.objects.create(to_addr=to,
                                  from_addr=from_,
                                  content=content,
                                  is_egress=False)


def sms_send(to, content):
    """Send an sms text message"""
    assert len(content) <= 160
    from_ = settings.TWILIO_PHONE
    logger.info("sms %s -> %s: %s", from_, to, content)
    if not settings.DEBUG and not getattr(settings, 'TEST_MODE', False):
        twil = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        twil.sms.messages.create(to=to, from_=from_, body=content)
    db.SmsMessage.objects.create(to_addr=to,
                                 from_addr=from_,
                                 content=content,
                                 is_egress=True)
