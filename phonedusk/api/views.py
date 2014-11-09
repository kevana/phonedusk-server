# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app, request, Response
from flask.ext.login import login_required

from functools import wraps
import twilio.twiml
from twilio.util import TwilioCapability

from phonedusk.user.models import User


blueprint = Blueprint("api", __name__, url_prefix='/api',
                        static_folder="../static")


def check_api_auth(username, password):
    user = User.query.filter_by(username=username).first()
    if not (user and user.check_password(password) and user.active):
        return False
    return True


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_api_auth(auth.username, auth.password):
            return Response('Unauthorized', 401)
        return f(*args, **kwargs)
    return decorated


def returns_xml(f):
    '''Decorator to return an XML response.'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/xml; charset=utf-8')
    return decorated_function


@blueprint.route("/capability_token", methods=['GET'])
@requires_auth
def get_capability():
    auth = request.authorization
    user = User.query.filter_by(username=auth.username).first()
    capability = TwilioCapability(current_app.config['TWILIO_ACCOUNT_SID'],
                                         current_app.config['TWILIO_AUTH_TOKEN'])
    capability.allow_client_incoming(user.username)
    capability.allow_client_outgoing(current_app.config['TWILIO_ACCOUNT_SID'])
    return capability.generate()


@blueprint.route("/call", methods=['GET', 'POST']) # GET added for debugging
@returns_xml
def twilio_route_incoming_call():
    # Called by twilio at start of incoming voice call
    # TODO: Use the 'To' post param to tie this to a user, create conference, add both parties to it.
    resp = twilio.twiml.Response()
    with resp.dial() as d:
        d.client('tommy')
    return str(resp)


@blueprint.route("/start_call", methods=['POST'])
@requires_auth
def user_route_outgoing_call():
    to_num = request.form['to']
    from_num = request.form['from']
    if not to_num or not from_num:
        return 'Request missing to or from numbers'

    client = TwilioRestClient(current_app.config['TWILIO_ACCOUNT_SID'],
                              current_app.config['TWILIO_AUTH_TOKEN'])
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        application_sid=current_app.config['TWILIO_ACCOUNT_SID'],
        method="POST",
        fallback_method="GET",
        status_callback_method="GET",
        record="false"
    )
    return Response(call.length, 200)

# Edit whitelist, blacklist
# Turn them on and off

@blueprint.route("/message", methods=['POST'])
@returns_xml
def route_incoming_message():
    return 'unimplemented'
