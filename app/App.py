from flask import Flask
from config import config
from app.utils.connectors.authenticatorFactory import authenticatorFactory


def createApp():
    app = Flask(
        __name__
    )
    app.config.from_object(config)

    authenticatorFactory.initApp(app=app, authenticatorType='ldap2')
    return app
