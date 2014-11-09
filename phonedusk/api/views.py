# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app, request, Response, g, jsonify
from flask.ext.login import login_required

from functools import wraps
import twilio.twiml
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability

from phonedusk.user.models import User, WhitelistPhoneNumber, BlacklistPhoneNumber


blueprint = Blueprint("api", __name__, url_prefix='/api',
                        static_folder="../static")


def check_api_auth(username, password):
    user = User.query.filter_by(username=username).first()
    if not (user and user.check_password(password) and user.active):
        return False
    g.user = user
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
    user = g.user
    capability = TwilioCapability(current_app.config['TWILIO_ACCOUNT_SID'],
                                         current_app.config['TWILIO_AUTH_TOKEN'])
    capability.allow_client_incoming(user.username)
    capability.allow_client_outgoing(current_app.config['TWILIO_ACCOUNT_SID'])
    return capability.generate()


@blueprint.route("/call", methods=['GET', 'POST']) # GET added for debugging
@returns_xml
def twilio_route_incoming_call():
    # Called by twilio at start of incoming voice call
    to_num = request.form['To']
    user = User.query.filter(User.phone_numbers.contains(to_num)).first()

    resp = twilio.twiml.Response()
    if not user:
        resp.reject()
    else:
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
    print(to_num, from_num)
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        url="https://phonedusk.herokuapp.com/api/call",
        method="POST",
        )
    return Response(call.__repr__(), 200)


# Whitelist functions
@blueprint.route("/whitelist", methods=['GET'])
@requires_auth
def get_whitelist():
    user = g.user
    return jsonify(phone_numbers=[num.phone_number for num in user.whitelist_numbers])


@blueprint.route("/whitelist", methods=['DELETE'])
@requires_auth
def delete_whitelist_number():
    user = g.user
    data = request.get_json()
    number = data['phone_number']
    items = [num for num in user.whitelist_numbers
                   if num.phone_number == number]
    for item in items:
        item.delete()

    return Response('', 204)


@blueprint.route("/whitelist", methods=['POST', 'PUT'])
@requires_auth
def create_whitelist_number():
    user = g.user
    data = request.get_json()
    number = data['phone_number']
    WhitelistPhoneNumber.create(user=user, phone_number=number)


# Blacklist functions
@blueprint.route("/blacklist", methods=['GET'])
@requires_auth
def get_blacklist():
    user = g.user
    return jsonify(phone_numbers=[num.phone_number for num in user.blacklist_numbers])


@blueprint.route("/blacklist", methods=['DELETE'])
@requires_auth
def delete_blacklist_number():
    user = g.user
    data = request.get_json()
    number = data['phone_number']
    items = [num for num in user.blacklist_numbers
             if num.phone_number == number]
    for item in items:
        item.delete()

    return Response('', 204)


@blueprint.route("/blacklist", methods=['POST', 'PUT'])
@requires_auth
def create_blacklist_number():
    user = g.user
    data = request.get_json()
    number = data['phone_number']
    BlacklistPhoneNumber.create(user=user, phone_number=number)


# Turn them on and off

@blueprint.route("/message", methods=['POST'])
@returns_xml
def route_incoming_message():
    return 'unimplemented'
