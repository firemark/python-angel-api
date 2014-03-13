from flask import Flask
app = Flask(__name__)

@app.route('/')
def oauth():
    return 'Hello World!'

