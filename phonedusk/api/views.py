# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app, request, Response, g, jsonify
from flask.ext.login import login_required

from functools import wraps
import twilio.twiml
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from twilio.util import TwilioCapability

from phonedusk.user.models import User, WhitelistPhoneNumber, BlacklistPhoneNumber, UserPhoneNumber


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


def returns_plaintext(f):
    '''Decorator to return a plaintext response.'''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/plain; charset=utf-8')
    return decorated_function


@blueprint.route("/capability_token", methods=['GET'])
@requires_auth
@returns_plaintext
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
    from_num = request.form['From']

    # TODO: Fix this with SQLAlchemy
    users = User.query.all()
    users = filter(lambda user: to_num in [x.phone_number for x in user.phone_numbers], users)
    if len(users) > 0:
        user = users[0]
        blacklist = user.blacklist_numbers
        whitelist = user.whitelist_numbers
        blacklist_matches = [x for x in blacklist if x.phone_number == from_num]
        whitelist_matches = [x for x in whitelist if x.phone_number == from_num]
    else:
        user = None
    resp = twilio.twiml.Response()
    if not user:
        # User not found by To number, check to see if this is an outgoing call
        # TODO: Refactor spaghetti logic
        users = User.query.all()
        users = filter(lambda user: from_num in [x.phone_number for x in user.phone_numbers], users)
        if len(users) > 0:
            user = users[0]
            with resp.dial() as d:
                d.client(user.username)
        else:
            resp.reject('User not found')
    elif user.enable_blacklist and len(blacklist_matches) > 0:
        resp.reject('Blacklisted')
    else:
        with resp.dial() as d:
            d.client(user.username)
    return str(resp)


@blueprint.route("/start_call", methods=['POST'])
@requires_auth
def user_route_outgoing_call():
    to_num = request.form['to']
    from_num = request.form['from']
    if not to_num or not from_num:
        return 'Request missing "to" or "from" parameters'

    try:
        client = TwilioRestClient(current_app.config['TWILIO_ACCOUNT_SID'],
                                  current_app.config['TWILIO_AUTH_TOKEN'])
        call = client.calls.create(
            to=to_num,
            from_=from_num,
            url="https://phonedusk.herokuapp.com/api/call",
            method="POST",
            )
    except twilio.TwilioRestException as e:
        resp = jsonify(uri=e.uri,status=e.status,msg=e.msg,code=e.code,method=e.method)
        resp.status_code = 400
        return resp
    return '', 204


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
    data = request.form
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
    data = request.form
    number = data['phone_number']
    WhitelistPhoneNumber.create(user=user, phone_number=number)
    return Response('', 204)


@blueprint.route("/whitelist/enable", methods=['POST'])
@requires_auth
def enable_whitelist():
    user = g.user
    user.enable_whitelist = True
    user.save()
    return Response('', 204)


@blueprint.route("/whitelist/disable", methods=['POST'])
@requires_auth
def disable_whitelist():
    user = g.user
    user.enable_whitelist = False
    user.save()
    return Response('', 204)


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
    data = request.form
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
    data = request.form
    number = data['phone_number']
    BlacklistPhoneNumber.create(user=user, phone_number=number)
    return Response('', 204)


@blueprint.route("/blacklist/enable", methods=['POST'])
@requires_auth
def enable_blacklist():
    user = g.user
    user.enable_blacklist = True
    user.save()
    return Response('', 204)


@blueprint.route("/blacklist/disable", methods=['POST'])
@requires_auth
def disable_blacklist():
    user = g.user
    user.enable_blacklist = False
    user.save()
    return Response('', 204)


@blueprint.route("/phone_numbers", methods=['GET'])
@requires_auth
def get_phone_numbers():
    user = g.user
    return jsonify(phone_numbers=[num.phone_number for num in user.phone_numbers])


@blueprint.route("/phone_numbers", methods=['DELETE'])
@requires_auth
def delete_phone_number():
    user = g.user
    data = request.form
    number = data['phone_number']
    items = [num for num in user.phone_numbers
                   if num.phone_number == number]
    for item in items:
        item.delete()

    return Response('', 204)


@blueprint.route("/phone_numbers", methods=['POST', 'PUT'])
@requires_auth
def create_phone_number():
    # TODO: Register new numbers on Twilio?
    user = g.user
    data = request.form
    number = data['phone_number']
    UserPhoneNumber.create(user=user, phone_number=number)
    return Response('', 204)


@blueprint.route("/message", methods=['POST'])
@returns_xml
def route_incoming_message():
    return 'unimplemented'
