from flask import Flask, request
from . import api
app = Flask(__name__)

@app.route('/')
def oauth():

    api.code = request.args.get('code')
    api.account_event.set()

    #shutdown server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not  None:
        func()

    return 'Thanks!'

