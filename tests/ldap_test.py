import unittest
from flask import Flask
from app.utils.connectors.authenticatorFactory import authenticatorFactory
from config import config
from app.utils.exceptions import FLASKLDAPMissingConfigurationError


class LDAPtest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(
            __name__
        )
        self.app.config.from_object(config)
        try:
            authenticatorFactory.initApp(self.app, 'ldap')
        except Exception:
            self.fail("Flask_LDAP rasied an unexpected exception")

    def testLoadConfigWithMissingSettings(self):
        del(self.app.config['DOMAIN'])
        del(self.app.authentication)
        with self.assertRaises(FLASKLDAPMissingConfigurationError):
            authenticatorFactory.initApp(self.app, 'ldap')

    def testAuthentication(self):
        shouldBeTrue = self.app.authentication.authenticateUser(
            'test_user',
            'qwerty123'
        )
        self.assertTrue(shouldBeTrue)

    def testAuthenticationWithErrors(self):
        shouldBeFalse = self.app.authentication.authenticateUser(
            'NoneExistingUser',
            'MissingPassword'
        )
        self.assertFalse(shouldBeFalse)

    def testAuthenticationWithoutAnyInput(self):
        with self.assertRaises(TypeError):
            self.app.authentication.authenticateUser()

    def testConnection(self):
        self.app.authentication.connection()

    def testGetUserGroups(self):
        groups = self.app.authentication.getUserGroups("test_user")
        self.assertTrue(type(groups) is list)

    def testGetUserGroupsNoneExistingUser(self):
        groups = self.app.authentication.getUserGroups("test_noneExistingUser")
        self.assertFalse(groups)

    def testCreateUser(self):

        sucessfull = self.app.authentication.createUser(
            'username',
            'password',
            'FirstName',
            'LastName',
            'Email@example.com',
            (
                'OU=Unpersonal Account,OU=AD-Users,'
                'OU=Users,OU=Xavizus,DC=xavizus,DC=com'
            )
        )

        self.assertTrue(sucessfull)

        self.app.authentication.deleteUser(
            (
                'CN=LastName FirstName,OU=Unpersonal Account,'
                'OU=AD-Users,OU=Users,OU=Xavizus,DC=xavizus,DC=com'
            )
        )
