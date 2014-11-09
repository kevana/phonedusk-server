# -*- coding: utf-8 -*-
'''
The admin module, containing Flask-Admin.
'''

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user

from phonedusk.extensions import db
from phonedusk.user.models import Role, User, UserPhoneNumber, BlacklistPhoneNumber, WhitelistPhoneNumber


class MyView(ModelView):
    '''Authenticated-required view for database models.'''
    column_exclude_list = ('password')

    def is_accessible(self):
        return (current_user.is_authenticated()
                and current_user.is_admin)


admin = Admin()
admin.add_view(MyView(Role, db.session))
admin.add_view(MyView(User, db.session))
admin.add_view(MyView(UserPhoneNumber, db.session))
admin.add_view(MyView(BlacklistPhoneNumber, db.session))
admin.add_view(MyView(WhitelistPhoneNumber, db.session))
