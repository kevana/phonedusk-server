# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
import pytest
from flask import url_for


from phonedusk.user.models import WhitelistPhoneNumber, BlacklistPhoneNumber, UserPhoneNumber
from .factories import UserFactory


class TestWhitelist:

    def test_create(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_whitelist_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(WhitelistPhoneNumber.query.all()) is 1

    def test_get(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_whitelist_number'), {'phone_number': '+5555551212'}, status=204)
        r = testapp.get(url_for('api.get_whitelist'), status=200)
        assert len(r.json) is 1

    def test_delete(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        #TODO: Remove dependency on create
        r = testapp.post(url_for('api.create_whitelist_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(WhitelistPhoneNumber.query.all()) is 1
        r = testapp.delete(url_for('api.delete_whitelist_number') + '?phone_number=%2B5555551212', status=204)
        assert len(WhitelistPhoneNumber.query.all()) is 0


class TestBlacklist:

    def test_create(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_blacklist_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(BlacklistPhoneNumber.query.all()) is 1

    def test_get(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_blacklist_number'), {'phone_number': '+5555551212'}, status=204)
        r = testapp.get(url_for('api.get_whitelist'), status=200)
        assert len(r.json) is 1

    def test_delete(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        #TODO: Remove dependency on create
        r = testapp.post(url_for('api.create_blacklist_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(BlacklistPhoneNumber.query.all()) is 1
        r = testapp.delete(url_for('api.delete_blacklist_number') + '?phone_number=%2B5555551212', status=204)
        assert len(BlacklistPhoneNumber.query.all()) is 0


class TestUserPhoneNumber:

    def test_create(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_phone_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(UserPhoneNumber.query.all()) is 1

    def test_get(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        r = testapp.post(url_for('api.create_phone_number'), {'phone_number': '+5555551212'}, status=204)
        r = testapp.get(url_for('api.get_phone_numbers'), status=200)
        assert len(r.json) is 1

    def test_delete(self, user, testapp):
        testapp.authorization = ('Basic', (user.username, 'myprecious'))
        #TODO: Remove dependency on create
        r = testapp.post(url_for('api.create_phone_number'), {'phone_number': '+5555551212'}, status=204)
        assert len(UserPhoneNumber.query.all()) is 1
        r = testapp.delete(url_for('api.delete_phone_number') + '?phone_number=%2B5555551212', status=204)
        assert len(UserPhoneNumber.query.all()) is 0
