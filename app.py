from flask import Flask
from shared import app

@app.route('/')
def hello_world():
    return '<b>Hello World!</b>'