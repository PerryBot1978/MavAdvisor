import requests
from flask import render_template, request, Response, jsonify

from shared import app
from config import BACKEND_API_BASE


def _proxy_to_backend(path):
    try:
        target_url = f"{BACKEND_API_BASE}{path}"

        headers = {
            key: value
            for key, value in request.headers
            if key.lower() not in {"host", "content-length"}
        }

        kwargs = {
            "method": request.method,
            "url": target_url,
            "headers": headers,
            "params": request.args,
            "cookies": request.cookies,
            "allow_redirects": False,
            "timeout": 60,
        }

        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if request.is_json:
                kwargs["json"] = request.get_json(silent=True)
            else:
                kwargs["data"] = request.get_data()

        response = requests.request(**kwargs)

        excluded_headers = {
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        }

        response_headers = [
            (name, value)
            for name, value in response.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(response.content, response.status_code, response_headers)

    except requests.RequestException as e:
        return jsonify({
            "success": False,
            "message": f"Backend request failed: {str(e)}"
        }), 502


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


@app.route('/user/logout', methods=['POST'])
def user_logout():
    return _proxy_to_backend('/user/logout')


@app.route('/api/register', methods=['POST'])
def api_register():
    return _proxy_to_backend('/api/register')


@app.route('/api/login', methods=['POST'])
def api_login():
    return _proxy_to_backend('/api/login')


@app.route('/api/fill_interests_certificates', methods=['POST'])
def api_fill_interests_certificates():
    return _proxy_to_backend('/api/fill_interests_certificates')


@app.route('/api/fill_interests_clubs', methods=['POST'])
def api_fill_interests_clubs():
    return _proxy_to_backend('/api/fill_interests_clubs')


@app.route('/api/account/change-password', methods=['POST'])
def api_change_password():
    return _proxy_to_backend('/api/account/change-password')


@app.route('/api/account/delete', methods=['POST'])
def api_delete_account():
    return _proxy_to_backend('/api/account/delete')


@app.route('/api/account/interests/<username>', methods=['GET'])
def api_account_interests(username):
    return _proxy_to_backend(f'/api/account/interests/{username}')


@app.route('/api/parse_courses', methods=['POST'])
def api_parse_courses():
    return _proxy_to_backend('/api/parse_courses')


@app.route('/api/confirm_unidentified_courses', methods=['POST'])
def api_confirm_unidentified_courses():
    return _proxy_to_backend('/api/confirm_unidentified_courses')


@app.route('/api/user/<username>', methods=['GET'])
def api_get_user_progress(username):
    return _proxy_to_backend(f'/api/user/{username}')


@app.route('/api/update_course_progress', methods=['POST'])
def api_update_course_progress():
    return _proxy_to_backend('/api/update_course_progress')


@app.route('/api/recommend_course_sets', methods=['GET'])
def api_recommend_course_sets():
    return _proxy_to_backend('/api/recommend_course_sets')


@app.route('/api/course_eligibility', methods=['GET'])
def api_course_eligibility():
    return _proxy_to_backend('/api/course_eligibility')


@app.route('/api/add_courses_in_progress', methods=['POST'])
def api_add_courses_in_progress():
    return _proxy_to_backend('/api/add_courses_in_progress')


@app.route('/api/certificates/<username>', methods=['GET'])
def api_get_user_certificates(username):
    return _proxy_to_backend(f'/api/certificates/{username}')


@app.route('/api/clubs/<username>', methods=['GET'])
def api_get_user_clubs(username):
    return _proxy_to_backend(f'/api/clubs/{username}')


@app.route('/api/clubs/join', methods=['POST'])
def api_join_club():
    return _proxy_to_backend('/api/clubs/join')


@app.route('/api/clubs/leave', methods=['POST'])
def api_leave_club():
    return _proxy_to_backend('/api/clubs/leave')


@app.route('/api/certificates/select', methods=['POST', 'DELETE'])
def api_select_certificate():
    return _proxy_to_backend('/api/certificates/select')