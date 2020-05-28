from flask import Flask
from config import config
from app.utils.ldap import Flask_LDAP

def createApp():
    app = Flask(
        __name__
    )
    app.config.from_object(config)

    Flask_LDAP(app)