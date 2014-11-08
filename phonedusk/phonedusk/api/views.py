# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, current_app
from flask.ext.login import login_required

#TODO: Probably don't want capability to be a global extension
from phonedusk.extensions import twilio_capability

blueprint = Blueprint("api", __name__, url_prefix='/api',
                        static_folder="../static")


@blueprint.route("/capability_token", methods=['GET'])
#@login_required
def get_capability():
    # TODO: This is redundant after the first call
    twilio_capability.allow_client_incoming("tommy")
    twilio_capability.allow_client_outgoing(current_app.config['TWILIO_ACCOUNT_SID'])
    return twilio_capability.generate()
