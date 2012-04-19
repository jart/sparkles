$ ->
  $("#resend_email").click (ev) ->
    ev.preventDefault()
    api "/api/verify_email/", email: g_email, (data) ->
      if data.status isnt "ERROR"
        $("#resend_email_sent").show()
  $("#resend_phone").click (ev) ->
    ev.preventDefault()
    api "/api/verify_phone/", phone: g_phone, (data) ->
      if data.status isnt "ERROR"
        $("#resend_phone_sent").show()
  $("#resend_xmpp").click (ev) ->
    ev.preventDefault()
    api "/api/verify_xmpp/", xmpp: g_xmpp, (data) ->
      if data.status isnt "ERROR"
        $("#resend_xmpp_sent").show()

# Use GET for data retrieval, POST for API calls that change stuff
api = (path, data, callback) ->
  if path.match /^\/api\/safe\//
    $.get path, data, callback, "json"
  else
    $.post path, data, callback, "json"

# Insert CSRF cookie in AJAX requests
$(document).ajaxSend (event, xhr, settings) ->
  getCookie = (name) ->
    if document.cookie
      for cookie in document.cookie.split ';'
        if cookie[0..name.length] is name + "="
          return decodeURIComponent cookie[name.length + 1...]
  sameOrigin = (url) ->
    host = document.location.host
    protocol = document.location.protocol
    sr_origin = '//' + host
    origin = protocol + sr_origin
    url is origin or url[..origin.length] is origin + '/' or
    url is sr_origin or url[..sr_origin.length] is sr_origin + '/' or
    not /^(\/\/|http:|https:).*/.test url
  safeMethod = (method) ->
    /^(GET|HEAD|OPTIONS|TRACE)$/.test method
  if not safeMethod settings.type and sameOrigin settings.url
    xhr.setRequestHeader "X-CSRFToken", getCookie 'csrftoken'
