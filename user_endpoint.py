from shared import app
from flask import render_template

@app.route('/user/login')
def user_login():
    return render_template('user_login.html')

@app.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')
