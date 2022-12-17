# coding: utf-8
from bottle import route, run, request, response, redirect, static_file, template, default_app
import random, string
import base64

@route('/')
def hello():
    return "<h1>Hello world!</h1>"

@route('/index.html')
def index():
    return template("index")

# -----
if __name__ == "__main__":
    run(host='0.0.0.0', port=80, server="gnuicorn", workers=4, debug=True, reloader=True)

app = default_app()
