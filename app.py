from flask import Flask, redirect
from waitress import serve
from shared import app

import admin_endpoint, user_endpoint, chatbot

@app.route('/')
def root():
    return redirect('/user/dashboard', code=302)

# serve(app, listen='*:8080')
