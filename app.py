# coding: utf-8
from bottle import route, run, request, response, redirect, static_file, template
import random, string
import base64

@route('/')
def root():
    return redirect("/index.html")
    
@route('/index.html')
def index():
    return template("index")

# -----
if __name__ == "__main__":
    run(host='0.0.0.0', port=80, debug=True, reloader=True)
