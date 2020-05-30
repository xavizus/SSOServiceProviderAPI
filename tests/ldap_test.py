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

    def testLoadConfig(self):
        self.app.config.from_object(config)
        try:
            Flask_LDAP(self.app)
        except Exception:
            self.fail("Flask_LDAP rasied an unexpected exception")

    def testLoadConfigWithMissingSettings(self):
        from tests import config_missing_variables
        self.app.config.from_object(config_missing_variables)
        with self.assertRaises(FLASKLDAPMissingConfigurationError):
            Flask_LDAP(self.app)

    def testAuthentication(self):
        self.app.config.from_object(config)
        Flask_LDAP(self.app)
        self.app.ldap.authenticateUser()

    def testConnection(self):
        self.app.config.from_object(config)
        Flask_LDAP(self.app)
        self.app.ldap.connection()
