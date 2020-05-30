from ldap3 import Server, Connection, ALL, NTLM, Tls
from ldap3.core.exceptions import LDAPUnknownAuthenticationMethodError,\
    LDAPSocketOpenError, LDAPSSLConfigurationError
from ldap3.utils import conv
from app.utils.exceptions import FLASKLDAPMissingConfigurationError
import ssl


class Flask_LDAP(object):
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
            auto_bind=False
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
        connection = Connection(auto_bind=True)
        connection.search(
            self.ldapOU,
            f'(&(sAMAccountName={escapedUsername}))',
            attributes=['memberOf']
        )
        entry = connection.entries

        groups = []
        for group in entry[0]['memberOf']:

            connection.search(
                group, '(objectClass=group)',
                attributes=['sAMAccountName']
            )
            groups.append(connection.entries[0]['sAMAccountName'])

        if 'Administrators' in groups:
            print("Is Admin")
        connection.unbind()
