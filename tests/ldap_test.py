import unittest
from flask import Flask
from app.utils.ldap import Flask_LDAP
from config import config
from app.utils.exceptions import FLASKLDAPMissingConfigurationError


class LDAPtest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(
            __name__
        )
        self.app.config.from_object(config)
        try:
            Flask_LDAP(self.app)
        except Exception:
            self.fail("Flask_LDAP rasied an unexpected exception")

    def testLoadConfigWithMissingSettings(self):
        del(self.app.config['DOMAIN'])
        del(self.app.ldap)
        with self.assertRaises(FLASKLDAPMissingConfigurationError):
            Flask_LDAP(self.app)

    def testAuthentication(self):
        shouldBeTrue = self.app.ldap.authenticateUser('test_user', 'qwerty123')
        self.assertTrue(shouldBeTrue)

    def testAuthenticationWithErrors(self):
        shouldBeFalse = self.app.ldap.authenticateUser('NoneExistingUser', 'MissingPassword')
        self.assertFalse(shouldBeFalse)

    def testAuthenticationWithoutAnyInput(self):
        with self.assertRaises(TypeError):
            self.app.ldap.authenticateUser()

    def testConnection(self):
        self.app.ldap.connection()

    def testGetUserGroups(self):
        groups = self.app.ldap.getUserGroups("test_user")
        self.assertTrue(type(groups) is list)

    def testGetUserGroupsNoneExistingUser(self):
        groups = self.app.ldap.getUserGroups("test_noneExistingUser")
        self.assertFalse(groups)

    def testCreateUser(self):

        sucessfull = self.app.ldap.createUser('username', 'password', options)

        self.assertTrue(sucessfull)