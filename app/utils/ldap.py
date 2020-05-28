from flask import current_app
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, Tls
from ldap3.core.exceptions import LDAPCursorError, LDAPUnknownAuthenticationMethodError, LDAPSocketOpenError
import ssl

class Flask_LDAP(object):
    ldapProviderUrl = None
    ldapDomain = None
    ldapOU = None
    ldapSSL = None

    server = None
    port = 389

    def __init__(self, app=None):
        if app is not None:
            self.initApp(app)

    def initApp(self, app):
        self.ldapProviderUrl = app.config.get('LDAP_PROVIDER_URL')
        self.ldapDomain = app.config.get('DOMAIN')
        self.ldapOU = app.config.get('DOMAIN_OU')
        self.ldapSSL = app.config.get('LDAP_SSL')
        self.port = app.config.get('LDAP_PORT')
        
        tls_configuration = None
        
        if(self.ldapSSL):
            tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1)

        self.server = Server(self.ldapProviderUrl, port=self.port, use_ssl=self.ldapSSL, get_info=ALL, tls=tls_configuration)

        app.__setattr__("ldap", self)

    def authenticateUser(self, username, password):
        authenticated = False
        try: 
            connection = Connection(self.server, user=f"{self.ldapDomain}\\{username}", password=password, authentication=NTLM)
            connection.bind()
            if connection.extend.standard.who_am_i():
                authenticated = True
        except LDAPUnknownAuthenticationMethodError:
            pass
        except LDAPSocketOpenError:
            pass
        finally:
            return authenticated
        

    def random():
        connection.search(app.config.get('DOMAIN_OU'),'(&(sAMAccountName={}))'.format(app.config.get('DOMAIN_USER')), attributes=['memberOf'])
        entry = connection.entries
        
        groups = []
        for group in entry[0]['memberOf']:
            
            connection.search(group, '(objectClass=group)', attributes=['sAMAccountName'])
            groups.append(connection.entries[0]['sAMAccountName'])
        
        if 'Administrators' in groups:
            print("Is Admin")
        connection.unbind()