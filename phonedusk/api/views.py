# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app, Response
from flask.ext.login import login_required

from functools import wraps
import twilio.twiml

#TODO: Probably don't want capability to be a global extension
from phonedusk.extensions import twilio_capability

blueprint = Blueprint("api", __name__, url_prefix='/api',
                        static_folder="../static")


def returns_xml(f):
    '''Decorator to return an XML response.'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/xml; charset=utf-8')
    return decorated_function


@blueprint.route("/capability_token", methods=['GET'])
#@login_required
def get_capability():
    # TOOD: Implement auth, tie user to client name
    # TODO: This is redundant after the first call
    twilio_capability.allow_client_incoming("tommy")
    twilio_capability.allow_client_outgoing(current_app.config['TWILIO_ACCOUNT_SID'])
    return twilio_capability.generate()


@blueprint.route("/call", methods=['GET', 'POST']) # GET added for debugging
@returns_xml
def route_incoming_call():
    # Called by twilio at start of incoming voice call
    # Use the 'To' post param to tie this to a user, create conference, add both parties to it.
    resp = twilio.twiml.Response()
    with resp.dial() as d:
        d.client('tommy')
    return str(resp)
    return 'teststring'


@blueprint.route("/message", methods=['POST'])
@returns_xml
def route_incoming_message():
    return 'unimplemented'
