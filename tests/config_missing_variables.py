import os
APP_NAME = 'SSO'
SECRET_KEY = ''

# LDAP Settings
LDAP_PROVIDER_URL = 'DNSToLDAP'
DOMAIN = "youRDomain"
DOMAIN_OU = 'OU=YourOu,DC=example,DC=com'
LDAP_PORT = 636  # 389 clear text connection, 636 secured connection
LDAP_CA_CERT_PATH = os.getcwd()+"\\config\\YourCert.cer"
