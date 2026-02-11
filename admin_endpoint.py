from shared import app
from flask import render_template

@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def user_login():
    return render_template('admin_dashboard.html')
