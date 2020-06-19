import importlib


class authenticatorFactory:
    def initApp(app, authenticatorType):
        authenticatorClass = None
        authenticatorType = "."+authenticatorType
        authLib = importlib.import_module(
            authenticatorType, 'app.utils.connectors'
        )
        authenticatorClass = getattr(authLib, authenticatorType)
        app.__setattr__("authentication", authenticatorClass(app))
