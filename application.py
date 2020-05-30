from app import App

application = App.createApp()

if __name__ == '__main__':
    from werkzeug import run_simple
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
