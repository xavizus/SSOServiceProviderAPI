from app.utils.abstractConnector import abstractConnector
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPUnknownAuthenticationMethodError,\
    LDAPSocketOpenError, LDAPSSLConfigurationError
from ldap3.utils import conv
from app.utils.exceptions import FLASKLDAPMissingConfigurationError


class Flask_LDAP(abstractConnector):
    ldapProviderUrl = None
    ldapDomain = None
    ldapOU = None
    ldapSSL = None

    server = None
    port = None

    tls_configuration = None

    def __init__(self, app=None):
        if app is not None:
            self.initApp(app)

    def initApp(self, app):
        requiredConfigs = {
            'ldapProviderUrl': 'LDAP_PROVIDER_URL',
            'ldapDomain': 'DOMAIN',
            'ldapOU': 'DOMAIN_OU',
            'ldapSSL': 'LDAP_SSL',
            'port': 'LDAP_PORT',
            'username': 'LDAP_USER',
            'password': 'LDAP_PASSWORD'
        }

        missingProperties = []
        for ldapProperty, configVariable in requiredConfigs.items():
            setattr(self, ldapProperty, app.config.get(configVariable))
            if getattr(self, ldapProperty) is None:
                missingProperties.append(configVariable)

        if len(missingProperties) != 0:
            stringMissingProperties = ', '.join(missingProperties)
            raise FLASKLDAPMissingConfigurationError(
                f"LDAP missing following properties: {stringMissingProperties}"
            )

        if(self.ldapSSL):
            import ssl
            from ldap3 import Tls
            self.tls_configuration = Tls(
                validate=ssl.CERT_REQUIRED,
                ca_certs_file=app.config.get('LDAP_CA_CERT_PATH'),
                version=ssl.PROTOCOL_TLSv1
            )

        try:
            self.server = Server(
                self.ldapProviderUrl,
                port=self.port,
                use_ssl=self.ldapSSL,
                get_info=ALL,
                tls=self.tls_configuration
            )

            connection = self.connection(self.username, self.password, True)
            connection.unbind()
        except LDAPSocketOpenError as error:
            raise Exception(error)
        except LDAPSSLConfigurationError as error:
            raise Exception(error)

        app.__setattr__("ldap", self)

    def connection(self, username=None, password=None, auto_bind=False):
        if any(element is None for element in [username, password]):
            username = self.username
            password = self.password
        return Connection(
            self.server,
            user=f"{self.ldapDomain}\\{username}",
            password=password,
            authentication=NTLM,
            auto_bind=auto_bind
        )

    def authenticateUser(self, username, password):
        authenticated = False
        try:
            connection = self.connection(username, password)
            connection.bind()
            if connection.extend.standard.who_am_i():
                authenticated = True
        except LDAPUnknownAuthenticationMethodError:
            pass
        except LDAPSocketOpenError:
            pass
        finally:
            connection.unbind()
            return authenticated

    def getUserGroups(self, username):
        escapedUsername = conv.escape_filter_chars(username, encoding=None)
        connection = self.connection(auto_bind=True)
        connection.search(
            self.ldapOU,
            f'(&(sAMAccountName={escapedUsername}))',
            attributes=['distinguishedName']
        )
        entry = connection.entries

        if not entry:
            return False

        groups = []
        connection.search(
            self.ldapOU, f'(member:1.2.840.113556.1.4.1941:={entry[0]["distinguishedName"]})',
            attributes=[ALL_ATTRIBUTES]
        )
        for entry in connection.entries:
            groups.append(entry['sAMAccountName'].value)
        connection.unbind()
        return groups if groups else False

    def createUser(
        self,
        username,
        password,
        firstname,
        lastname,
        email,
        distinguishedNameOfOU,
        description="Created by SSO"
    ):
        options = {
            "objectClass": 'User',
            'sn': lastname,
            'description': description,
            'displayName': f"{lastname} {firstname}",
            'givenName': firstname,
            'sAMAccountName': username,
            'mail': email,
            'distinguishedName': f"CN={lastname} {firstname},{distinguishedNameOfOU}",
            'userAccountControl': 512  # https://support.microsoft.com/sv-se/help/305144/how-to-use-useraccountcontrol-to-manipulate-user-account-properties
        }

        result, error = self._createObject(options)
        if error:
            return False
        connection = self.connection(auto_bind=True)
        unlockResult = connection.extend.microsoft.unlock_account(options['distinguishedName'])
        if unlockResult['result'] != 0:
            raise Exception(
                f"Could not unlock user. Reason: { unlockResult['description']}"
            )

        passwordResult = connection.extend.microsoft.modify_password(options['distinguishedName'], new_password=password)
        if passwordResult['result'] != 0:
            raise Exception(
                f"Could not reset password. Reason: { passwordResult['description']}"
            )
        connection.unbind()

    def _createObject(self, dObject):
        objectCreated = True
        connection = self.connection(auto_bind=True)
        connection.add(dObject['distinguishedName'], attributes=dObject)

        creationResult = connection.result
        if creationResult['result'] != 0:
            loggmessage = f"Could not create object. Reason: { creationResult['description'] }"
            objectCreated = False
        connection.unbind()
        return objectCreated, loggmessage if loggmessage else None

    def deleteUser(self, username):
        raise NotImplementedError('Subclass must override deleteUser method')

    def addUserToGroups(self, username, groups):
        raise NotImplementedError(
            'Subclass must override addUserToGroups method'
        )

    def removeUserFromGroups(self, username, groups):
        raise NotImplementedError(
            'Subclass must override removeUserFromGroups method'
        )

    def resetPassword(self, username, password):
        raise NotImplementedError('Subclass must override resetPassword method')

    def createGroup(self, groupName, options=None):
        raise NotImplementedError('Subclass must override createGroup method')

    def deleteGroup(self, groupName, options=None):
        raise NotImplementedError('Subclass must override deleteGroup method')