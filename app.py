from flask import Flask
from shared import app

import admin_endpoint, user_endpoint

@app.route('/')
def hello_world():
    return '<b>Hello World!</b>'