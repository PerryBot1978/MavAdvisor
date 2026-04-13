from shared import app
from flask import render_template

@app.route('/user/login')
def user_login():
    return render_template('user_login.html')

@app.route('/user/register')
def user_register():
    return render_template('user_registration.html')

@app.route('/user/dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/user/course-planner')
def course_planner():
    return render_template('course_planner.html')

@app.route('/user/ai-assistant')
def ai_assistant():
    return render_template('ai_assistant.html')

@app.route('/user/clubs')
def clubs():
    return render_template('clubs_organizations.html')

@app.route('/user/event-calendar')
def event_calendar():
    return render_template('event_calendar.html')

@app.route('/user/certificates')
def certificates():
    return render_template('certificates.html')

@app.route('/user/account-management')
def account_management():
    return render_template('account_management.html')
