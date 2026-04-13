from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import mav_advisor_terminal_test as mav_helper
import interest_scoring as interest_help
import mav_advisor as advisor
import cs_course
import ce_course
from config import USERS_DIR, BACKEND_RUN_DEBUG, BACKEND_RUN_HOST, BACKEND_RUN_PORT
from db import get_db_connection, init_db
from clubs import get_clubs



app = Flask(__name__)
CORS(app)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    major = data.get('major', '').strip()
    classification = data.get('classification', '').strip()

    if not username or not email or not password or not major or not classification:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Username or email already exists"
        }), 409

    password_hash = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    conn.commit()
    conn.close()

    user_data = {
        "username": username,
        "email": email,
        "profile": {
            "major": major,
            "classification": classification,
            "certificate_interests": [],
            "club_interests": []
        },
        "planner": {
            "courses_completed": [],
            "courses_in_progress": [],
            "certificates": [],
            "clubs": [],
            "certificates_selected": [],
            "clubs_selected": [],
            "total_hours_to_completed": 0,
            "hours_completed": 0
        }
    }

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)

    certificates = mav_helper._load_certificates_for_degree(major)
    all_keywords = interest_help.get_unique_keywords(certificates)

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": {
            "username": username,
            "email": email,
            "major": major,
            "classification": classification
        },
        "keywords": all_keywords
    }), 201

@app.route('/api/fill_interests_certificates', methods=['POST'])
def fill_interest_certificates():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get("username", "").strip()
    major = data.get("major", "").strip()
    selected_interests = data.get("interests", [])

    if not username or not major:
        return jsonify({
            "success": False,
            "message": "Username and major are required"
        }), 400

    if not isinstance(selected_interests, list):
        return jsonify({
            "success": False,
            "message": "Interests must be a list"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"

    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User file not found"
        }), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    certificates = mav_helper._load_certificates_for_degree(major)
    certificate_scores = interest_help.score_items(certificates, selected_interests)
    total_hours = mav_helper.get_major_hours(major)

    suggested_certificates = []
    if certificate_scores:
        max_score = max(certificate_scores.values())
        if max_score > 0:
            for cert_id, score in certificate_scores.items():
                if score == max_score:
                    suggested_certificates.append({
                        "certificate_id": cert_id,
                        "certificate_name": certificates[cert_id].get("name", cert_id),
                        "score": score
                    })

    suggested_certificates.sort(key=lambda x: x["score"], reverse=True)

    user_data["profile"]["certificate_interests"] = selected_interests
    user_data["planner"]["certificates"] = suggested_certificates
    user_data["planner"]["total_hours_to_completed"] = total_hours

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)

    clubs = get_clubs()
    club_keywords = interest_help.get_unique_keywords(clubs)

    return jsonify({
        "success": True,
        "message": "Certificate interests and certificate suggestions saved successfully",
        "club_keywords": club_keywords
    }), 200

@app.route('/api/fill_interests_clubs', methods=['POST'])
def fill_interest_clubs():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get("username", "").strip()
    selected_interests = data.get("interests", [])

    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400

    if not isinstance(selected_interests, list):
        return jsonify({
            "success": False,
            "message": "Interests must be a list"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"

    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User file not found"
        }), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    clubs = get_clubs()
    club_scores = interest_help.score_items(clubs, selected_interests)

    suggested_clubs = []

    for club_id, score in club_scores.items():
        if score > 0:
            suggested_clubs.append({
                "club_id": club_id,
                "club_name": clubs[club_id].get("name", club_id),
                "score": score
            })

    suggested_clubs.sort(key=lambda x: x["score"], reverse=True)

    user_data["profile"]["club_interests"] = selected_interests
    user_data["planner"]["clubs"] = suggested_clubs

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)

    return jsonify({
        "success": True,
        "message": "Club interests and club suggestions saved successfully"
    }), 200


@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required"
        }), 400    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        (username,)
    )
    existing_user = cursor.fetchone()

    if not existing_user:
        conn.close()
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    stored_password_hash = existing_user["password_hash"]

    if not check_password_hash(stored_password_hash, password):
        conn.close()
        return jsonify({
            "success": False,
            "message": "Invalid username or password"
        }), 401

    conn.close()
    return jsonify({
        "success": True,
        "message": "Login successful"
    }), 200


@app.route('/api/account/change-password', methods=['POST'])
def change_password():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = (data.get("username") or "").strip()
    current_password = (data.get("current_password") or "").strip()
    new_password = (data.get("new_password") or "").strip()

    if not username or not current_password or not new_password:
        return jsonify({"success": False, "message": "Username, current password, and new password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404

    stored_password_hash = row["password_hash"]
    if not check_password_hash(stored_password_hash, current_password):
        conn.close()
        return jsonify({"success": False, "message": "Current password is incorrect"}), 401

    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Password updated successfully"}), 200


@app.route('/api/account/delete', methods=['POST'])
def delete_account():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404

    if not check_password_hash(row["password_hash"], password):
        conn.close()
        return jsonify({"success": False, "message": "Password is incorrect"}), 401

    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

    user_file_path = USERS_DIR / f"{username}.json"
    if user_file_path.exists():
        try:
            user_file_path.unlink()
        except Exception as e:
            return jsonify({"success": False, "message": f"Failed to delete user file: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Account deleted successfully"}), 200


@app.route('/api/account/interests/<username>', methods=['GET'])
def get_account_interests(username):
    username = username.strip()
    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    profile = user_data.get("profile", {})
    major = profile.get("major", "")

    certificate_interests = profile.get("certificate_interests", []) or []
    club_interests = profile.get("club_interests", []) or []

    certificates = mav_helper._load_certificates_for_degree(major)
    certificate_keywords = interest_help.get_unique_keywords(certificates)
    clubs = get_clubs()
    club_keywords = interest_help.get_unique_keywords(clubs)

    return jsonify({
        "success": True,
        "data": {
            "username": username,
            "major": major,
            "certificate_interests": certificate_interests,
            "club_interests": club_interests,
            "certificate_keywords": certificate_keywords,
            "club_keywords": club_keywords
        }
    }), 200

def _normalize_course_code(course_code: str) -> str:
    if not isinstance(course_code, str):
        return ""
    return course_code.strip().lower().replace(" ", "").replace("-", "")


def _pretty_course_code(course_code: str) -> str:
    if not isinstance(course_code, str):
        return ""
    raw = _normalize_course_code(course_code)
    # Separate letters and numbers: cse1320 -> CSE 1320
    import re
    m = re.match(r"^([a-zA-Z]+)(\d+)$", raw)
    if m:
        return f"{m.group(1).upper()} {m.group(2)}"
    return course_code.upper()


def _get_course_credits(major: str, course_code: str) -> int:
    module = _get_course_module_for_major(major)
    graph = module.build_graph()
    normalized = _normalize_course_code(course_code)
    if normalized in graph.nodes:
        return graph.nodes[normalized].get("credits", 0)
    # try uppercase/spaced variant not in graph; also try lower
    lower = normalized.lower()
    if lower in graph.nodes:
        return graph.nodes[lower].get("credits", 0)
    return 0


def _get_course_module_for_major(major: str):
    major_key = (major or "").strip().lower()
    if "computer science" in major_key or major_key.startswith("cs"):
        return cs_course
    if "computer engineering" in major_key or major_key.startswith("ce"):
        return ce_course
    # fallback to CS by default
    return cs_course


def _get_course_name(major: str, course_code: str) -> str:
    module = _get_course_module_for_major(major)
    graph = module.build_graph()
    normalized = _normalize_course_code(course_code)
    if normalized in graph.nodes:
        return graph.nodes[normalized].get("name", "Unknown")
    # try uppercase/spaced variant not in graph; also try lower
    lower = normalized.lower()
    if lower in graph.nodes:
        return graph.nodes[lower].get("name", "Unknown")
    return "Unknown"


def _safe_user_file(username: str):
    username = (username or "").strip()
    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return None, None
    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)
    return user_file_path, user_data


def _extract_selected_certificate_ids(planner: dict) -> list:
    selected_items = planner.get("certificates_selected", []) or []
    selected_ids = []
    for item in selected_items:
        if not isinstance(item, dict):
            continue
        cert_id = (item.get("certificate_id") or "").strip()
        if cert_id and cert_id not in selected_ids:
            selected_ids.append(cert_id)
    return selected_ids


def _extract_selected_club_ids(planner: dict) -> list:
    selected_items = planner.get("clubs_selected", []) or []
    selected_ids = []
    for item in selected_items:
        if not isinstance(item, dict):
            continue
        club_id = (item.get("club_id") or "").strip()
        if club_id and club_id not in selected_ids:
            selected_ids.append(club_id)
    return selected_ids


@app.route('/user/logout', methods=['POST'])
def logout():
    # In a full auth setup, clear server-side session/cookies here.
    return jsonify({
        "success": True,
        "message": "Logout successful"
    }), 200


@app.route('/api/parse_courses', methods=['POST'])
def parse_courses():
    username = request.form.get("username", "").strip()
    print(f"Received username: '{username}'")

    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    profile = user_data.get("profile", {})
    module = _get_course_module_for_major(profile.get("major"))
    G = module.build_graph()
    rules = module.get_rules()
    unknown_options = advisor.get_unknown_course_options(rules)

    completed_courses_raw = []
    in_progress_courses_raw = []

    if 'courses' in request.form:
        try:
            # frontend should send:
            # {
            #   "completed_courses": [...],
            #   "in_progress_courses": [...]
            # }
            payload = json.loads(request.form['courses'])

            if isinstance(payload, list):
                # backward compatibility: old frontend sends just one list
                completed_courses_raw = payload
            elif isinstance(payload, dict):
                completed_courses_raw = payload.get("completed_courses", [])
                in_progress_courses_raw = payload.get("in_progress_courses", [])
                if not isinstance(completed_courses_raw, list) or not isinstance(in_progress_courses_raw, list):
                    raise ValueError
            else:
                raise ValueError

        except Exception:
            return jsonify({
                "success": False,
                "message": "Invalid courses format"
            }), 400

    elif 'transcript' in request.files:
        transcript_file = request.files['transcript']

        try:
            temp_path = USERS_DIR / f"{username}_temp_transcript.pdf"
            transcript_file.save(temp_path)

            completed_courses_raw, in_progress_courses_raw = advisor.parse_transcript_details(str(temp_path))

            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Could not parse transcript: {str(e)}"
            }), 400
    else:
        return jsonify({
            "success": False,
            "message": "No courses or transcript provided"
        }), 400

    recognized_courses = []
    unidentified_courses = []

    recognized_in_progress = []
    unidentified_in_progress = []

    for c in completed_courses_raw:
        normalized = advisor.normalize_manual_course_token(c)

        if normalized in G.nodes:
            recognized_courses.append(normalized)
        else:
            unidentified_courses.append({
                "raw": c,
                "normalized": normalized,
                "options": unknown_options,
                "status": "completed"
            })

    for c in in_progress_courses_raw:
        normalized = advisor.normalize_manual_course_token(c)

        if normalized in G.nodes:
            recognized_in_progress.append(normalized)
        else:
            unidentified_in_progress.append({
                "raw": c,
                "normalized": normalized,
                "options": unknown_options,
                "status": "in_progress"
            })

    return jsonify({
        "success": True,
        "message": "Courses parsed",
        "recognized_courses": sorted(set(recognized_courses)),
        "unidentified_courses": unidentified_courses,
        "recognized_in_progress": sorted(set(recognized_in_progress)),
        "unidentified_in_progress": unidentified_in_progress
    }), 200

@app.route('/api/confirm_unidentified_courses', methods=['POST'])
def confirm_unidentified_courses():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get("username", "").strip().lower()
    recognized_courses = data.get("recognized_courses", [])
    recognized_in_progress = data.get("recognized_in_progress", [])
    resolved_courses = data.get("resolved_courses", [])

    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400

    if (
        not isinstance(recognized_courses, list)
        or not isinstance(recognized_in_progress, list)
        or not isinstance(resolved_courses, list)
    ):
        return jsonify({
            "success": False,
            "message": "Invalid course data"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"

    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User file not found"
        }), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    profile = user_data.get("profile", {})
    planner = user_data.setdefault("planner", {})

    module = _get_course_module_for_major(profile.get("major"))
    G = module.build_graph()
    rules = module.get_rules()

    existing_completed = set(planner.get("courses_completed", []))
    existing_in_progress = set(planner.get("courses_in_progress", []))

    completed = set()
    in_progress = set()

    for c in recognized_courses:
        if c in G.nodes:
            completed.add(c)

    for c in recognized_in_progress:
        if c in G.nodes:
            in_progress.add(c)

    resolution_messages = []

    # This is the key fix:
    # slot filling must look at ALL occupied slots, not just one temp bucket
    working_state = set(existing_completed) | set(existing_in_progress) | set(completed) | set(in_progress)

    for item in resolved_courses:
        raw = item.get("raw", "").strip()
        selected_option = item.get("selected_option", "").strip()
        status = item.get("status", "completed").strip().lower()

        if not selected_option:
            continue

        if selected_option == "extra":
            msg = f"{raw} counted as EXTRA."
            resolution_messages.append(msg)
            continue

        before_state = set(working_state)

        msg = advisor.mark_elective_satisfied(
            G=G,
            completed=working_state,
            rules=rules,
            elective_name=selected_option
        )
        resolution_messages.append(msg)

        newly_added = working_state - before_state

        # Put any newly created slot/group marker into the correct bucket
        if status == "completed":
            completed.update(newly_added)
        else:
            in_progress.update(newly_added)

    combined_completed = sorted(existing_completed | completed)
    combined_in_progress = sorted((existing_in_progress | in_progress) - set(combined_completed))

    new_completed = completed - existing_completed
    additional_hours = sum(G.nodes[c].get("credits", 0) for c in new_completed if c in G.nodes)
    current_hours = planner.get("hours_completed", 0)

    planner["hours_completed"] = current_hours + additional_hours
    planner["courses_completed"] = combined_completed
    planner["courses_in_progress"] = combined_in_progress
    planner["electives_met"] = advisor.compute_electives_met(
        G,
        set(combined_completed),
        set(combined_in_progress),
        rules
    )

    if "updates" not in user_data:
        user_data["updates"] = []

    user_data["updates"].append({
        "type": "courses_updated_from_web",
        "recognized_courses": sorted(set(recognized_courses)),
        "recognized_in_progress": sorted(set(recognized_in_progress)),
        "resolved_courses": resolved_courses,
        "messages": resolution_messages,
        "electives_met": planner["electives_met"]
    })

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)

    return jsonify({
        "success": True,
        "message": "Courses updated successfully",
        "completed_courses": combined_completed,
        "courses_in_progress": combined_in_progress,
        "electives_met": planner["electives_met"],
        "resolution_messages": resolution_messages
    }), 200

@app.route('/api/user/<username>', methods=['GET'])
def get_user_progress(username):
    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    planner = user_data.get("planner", {}) or {}
    profile = user_data.get("profile", {}) or {}

    hours_completed = planner.get("hours_completed", 0)
    total_hours = planner.get("total_hours_to_completed", 0)
    electives_met = planner.get("electives_met", {}) or {}

    percentage = 0
    if isinstance(total_hours, (int, float)) and total_hours > 0:
        percentage = min(100, max(0, (hours_completed / total_hours) * 100))

    completed = planner.get("courses_completed", []) or []
    in_progress = planner.get("courses_in_progress", []) or []

    major = profile.get("major", "")
    classification = profile.get("classification", "")
    email = user_data.get("email", "") or profile.get("email", "")

    completed_ids = set(_normalize_course_code(c) for c in completed)
    in_progress_ids = set(_normalize_course_code(c) for c in in_progress)

    completed_list = []
    in_progress_list = []
    not_completed_list = []

    for c in completed:
        normalized = _normalize_course_code(c)
        completed_list.append({
            "code": _pretty_course_code(normalized),
            "name": _get_course_name(major, normalized),
            "status": "Complete"
        })

    for c in in_progress:
        normalized = _normalize_course_code(c)
        in_progress_list.append({
            "code": _pretty_course_code(normalized),
            "name": _get_course_name(major, normalized),
            "status": "In Progress"
        })

    course_module = _get_course_module_for_major(major)
    all_major_courses = course_module.course_list()
    rules = course_module.get_rules()

    # Only option-based elective group placeholders should be skipped when met.
    # Example: security, tech_options
    option_elective_names = {
        str(e.get("name", "")).strip().lower()
        for e in rules.get("electives", [])
        if e.get("options") is not None
    }

    for c in all_major_courses:
        normalized = _normalize_course_code(c)

        if normalized in completed_ids or normalized in in_progress_ids:
            continue

        # If this is an option-based elective group and it is already met,
        # do not show it as "Not Started".
        if normalized in option_elective_names and electives_met.get(normalized, False):
            continue

        course_name = _get_course_name(major, normalized)
        if not course_name or course_name == "Unknown":
            course_name = c.replace('_', ' ').upper()

        not_completed_list.append({
            "code": _pretty_course_code(normalized),
            "name": course_name,
            "status": "Not Started"
        })

    def sort_key(x):
        return x["code"]

    completed_list.sort(key=sort_key)
    in_progress_list.sort(key=sort_key)
    not_completed_list.sort(key=sort_key)

    selected_club_ids = _extract_selected_club_ids(planner)
    selected_clubs = []
    clubs_dict = get_clubs()
    for club_id in selected_club_ids:
        club_info = clubs_dict.get(club_id)
        if not club_info:
            continue
        selected_clubs.append({
            "id": club_id,
            "name": club_info.get("name", club_id)
        })

    selected_cert_ids = _extract_selected_certificate_ids(planner)
    selected_certificates = []
    certificate_catalog = _get_course_module_for_major(major).get_certificates()
    for cert_id in selected_cert_ids:
        cert_info = certificate_catalog.get(cert_id)
        if not cert_info:
            continue
        selected_certificates.append({
            "key": cert_id,
            "name": cert_info.get("name", cert_id)
        })

    return jsonify({
        "success": True,
        "data": {
            "username": username,
            "major": major,
            "classification": classification,
            "email": email,
            "hours_completed": hours_completed,
            "total_hours": total_hours,
            "completion_percent": round(percentage, 2),
            "courses_completed": completed_list,
            "courses_in_progress": in_progress_list,
            "courses_not_completed": not_completed_list,
            "selected_clubs": selected_clubs,
            "selected_certificates": selected_certificates,
            "electives_met": electives_met
        }
    }), 200

@app.route('/api/update_course_progress', methods=['POST'])
def update_course_progress():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    username = data.get('username', '').strip()
    updated_courses = data.get('updated_courses', [])

    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required"
        }), 400

    if not isinstance(updated_courses, list):
        return jsonify({
            "success": False,
            "message": "updated_courses must be a list"
        }), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    # Load current user data
    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    planner = user_data.get("planner", {})
    courses_completed = planner.get("courses_completed", [])
    courses_in_progress = planner.get("courses_in_progress", [])
    hours_completed = planner.get("hours_completed", 0)
    major = user_data.get("profile", {}).get("major", "")

    # Process each updated course
    for course_update in updated_courses:
        course_code = course_update.get('course_code', '').strip()
        action = course_update.get('action', '').strip()

        if not course_code or not action:
            continue

        normalized_code = _normalize_course_code(course_code)

        if action == 'completed':
            # Move from in_progress to completed and add credits
            if normalized_code in [_normalize_course_code(c) for c in courses_in_progress]:
                # Remove from in_progress
                courses_in_progress = [c for c in courses_in_progress if _normalize_course_code(c) != normalized_code]
                # Add to completed (using original case from the request)
                courses_completed.append(course_code)
                # Add credits
                credits = _get_course_credits(major, course_code)
                hours_completed += credits

        elif action == 'drop':
            # Remove from in_progress
            if normalized_code in [_normalize_course_code(c) for c in courses_in_progress]:
                courses_in_progress = [c for c in courses_in_progress if _normalize_course_code(c) != normalized_code]

    # Update the planner data
    planner["courses_completed"] = courses_completed
    planner["courses_in_progress"] = courses_in_progress
    planner["hours_completed"] = hours_completed
    user_data["planner"] = planner

    # normalize + dedupe course lists before save
    norm_completed = []
    seen_completed = set()
    for c in courses_completed:
        normalized = _normalize_course_code(c)
        if normalized and normalized not in seen_completed:
            seen_completed.add(normalized)
            norm_completed.append(normalized)

    norm_in_progress = []
    seen_in_progress = set()
    for c in courses_in_progress:
        normalized = _normalize_course_code(c)
        if normalized and normalized not in seen_in_progress and normalized not in seen_completed:
            seen_in_progress.add(normalized)
            norm_in_progress.append(normalized)

    planner["courses_completed"] = norm_completed
    planner["courses_in_progress"] = norm_in_progress
    planner["hours_completed"] = hours_completed
    user_data["planner"] = planner

    # Save updated user data
    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    return jsonify({
        "success": True,
        "message": "Course progress updated successfully",
        "data": {
            "courses_completed": norm_completed,
            "courses_in_progress": norm_in_progress,
            "hours_completed": hours_completed
        }
    }), 200


@app.route('/api/recommend_course_sets', methods=['GET'])
def recommend_course_sets():
    username = request.args.get('username', '').strip()
    target_hours = request.args.get('target_hours', '').strip()

    if not username:
        return jsonify({"success": False, "message": "Username is required"}), 400

    if not target_hours.isdigit():
        return jsonify({"success": False, "message": "target_hours must be an integer"}), 400

    target_hours = int(target_hours)
    if target_hours < 1 or target_hours > 30:
        return jsonify({"success": False, "message": "target_hours must be between 1 and 30"}), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    major = user_data.get("profile", {}).get("major", "")
    planner = user_data.get("planner", {})
    completed_set = set(_normalize_course_code(c) for c in planner.get("courses_completed", []) if _normalize_course_code(c))
    in_progress_set = set(_normalize_course_code(c) for c in planner.get("courses_in_progress", []) if _normalize_course_code(c))

    course_module = _get_course_module_for_major(major)
    G = course_module.build_graph()
    rules = course_module.get_rules()

    try:
        plans = advisor.recommend_three_options(
            G,
            completed_set,
            target_hours,
            rules,
            current_in_progress=in_progress_set,
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Error computing recommendations: {e}"}), 500

    if not plans:
        return jsonify({"success": True, "data": {"plans": []}}), 200

    def to_course_obj(code):
        pretty = _pretty_course_code(code)
        return {
            "code": code,
            "pretty_code": pretty,
            "name": _get_course_name(major, code),
            "credits": _get_course_credits(major, code),
        }

    plan_options = []
    for label, plan in plans.items():
        entries = []
        for entry in plan.get("entries", []):
            if entry.get("kind") == "course":
                for course_code in entry.get("courses", []):
                    entries.append({
                        "kind": "course",
                        "course": to_course_obj(course_code),
                    })
            elif entry.get("kind") == "choice_group":
                options = []
                for course_code in entry.get("options", []):
                    options.append(to_course_obj(course_code))
                entries.append({
                    "kind": "choice_group",
                    "label": entry.get("display", "Choice Group"),
                    "options": options,
                })

        plan_options.append({
            "label": label,
            "total_credits": plan.get("total_credits", 0),
            "entries": entries,
        })

    return jsonify({"success": True, "data": {"plans": plan_options}}), 200


@app.route('/api/course_eligibility', methods=['GET'])
def course_eligibility():
    username = request.args.get('username', '').strip()
    course_code = request.args.get('course_code', '').strip()

    if not username or not course_code:
        return jsonify({"success": False, "message": "username and course_code are required"}), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    major = user_data.get("profile", {}).get("major", "")
    planner = user_data.get("planner", {})

    completed = set(_normalize_course_code(c) for c in planner.get("courses_completed", []) if _normalize_course_code(c))
    in_progress = set(_normalize_course_code(c) for c in planner.get("courses_in_progress", []) if _normalize_course_code(c))

    module = _get_course_module_for_major(major)
    G = module.build_graph()
    rules = module.get_rules()

    norm_course = _normalize_course_code(course_code)
    if not norm_course or norm_course not in G.nodes:
        return jsonify({"success": True, "data": {"eligible": False, "reason": "Course unknown in major graph"}}), 200

    if norm_course in completed:
        return jsonify({"success": True, "data": {"eligible": False, "reason": "Course already completed"}}), 200

    if norm_course in in_progress:
        return jsonify({"success": True, "data": {"eligible": False, "reason": "Course already in progress"}}), 200

    eligible = advisor.can_take(G, norm_course, completed, in_progress, rules)
    return jsonify({"success": True, "data": {"eligible": bool(eligible), "course": norm_course}}), 200


@app.route('/api/add_courses_in_progress', methods=['POST'])
def add_courses_in_progress():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = data.get('username', '').strip()
    courses = data.get('courses', [])

    if not username:
        return jsonify({"success": False, "message": "Username is required"}), 400

    if not isinstance(courses, list):
        return jsonify({"success": False, "message": "courses must be a list"}), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    major = user_data.get("profile", {}).get("major", "")
    planner = user_data.setdefault("planner", {})

    completed = set(_normalize_course_code(c) for c in planner.get("courses_completed", []) if _normalize_course_code(c))
    in_progress = set(_normalize_course_code(c) for c in planner.get("courses_in_progress", []) if _normalize_course_code(c))

    module = _get_course_module_for_major(major)
    G = module.build_graph()
    rules = module.get_rules()

    added = []
    for course_code in courses:
        norm = _normalize_course_code(course_code)
        if not norm:
            continue
        if norm in completed or norm in in_progress:
            continue
        if norm not in G.nodes:
            continue
        if advisor.can_take(G, norm, completed, in_progress, rules):
            in_progress.add(norm)
            added.append(norm)

    planner["courses_in_progress"] = sorted(in_progress)
    user_data["planner"] = planner

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    return jsonify({"success": True, "message": "Courses added to in progress", "data": {"added": added, "courses_in_progress": sorted(in_progress)}}), 200


@app.route('/api/certificates/<username>', methods=['GET'])
def get_user_certificates(username):
    username = username.strip()
    
    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    major = user_data.get("profile", {}).get("major", "")
    profile = user_data.get("profile", {})
    user_interests = profile.get("certificate_interests", profile.get("interests", []))
    planner = user_data.get("planner", {})
    
    module = _get_course_module_for_major(major)
    
    all_certificates = module.get_certificates()

    planner_certificates = planner.get("certificates", []) or []
    suggested = []
    suggested_ids = []

    for cert_item in planner_certificates:
        if not isinstance(cert_item, dict):
            continue

        cert_key = cert_item.get("certificate_id", "").strip()
        if not cert_key or cert_key not in all_certificates or cert_key in suggested_ids:
            continue

        cert_data = all_certificates.get(cert_key, {})
        suggested.append({
            "key": cert_key,
            "name": cert_item.get("certificate_name", cert_data.get("name", cert_key)),
            "description": cert_data.get("description", ""),
            "courses": cert_data.get("courses", []),
            "keywords": cert_data.get("keywords", []),
            "degree": cert_data.get("degree", ""),
            "score": cert_item.get("score", 0)
        })
        suggested_ids.append(cert_key)

    available = []
    for cert_key, cert_data in all_certificates.items():
        if cert_key in suggested_ids:
            continue
        available.append({
            "key": cert_key,
            "name": cert_data.get("name", cert_key),
            "description": cert_data.get("description", ""),
            "courses": cert_data.get("courses", []),
            "keywords": cert_data.get("keywords", []),
            "degree": cert_data.get("degree", ""),
            "score": 0
        })

    selected_cert_ids = _extract_selected_certificate_ids(planner)
    selected_certificates = []
    for cert_key in selected_cert_ids:
        cert_data = all_certificates.get(cert_key)
        if not cert_data:
            continue
        selected_certificates.append({
            "key": cert_key,
            "name": cert_data.get("name", cert_key),
            "description": cert_data.get("description", ""),
            "courses": cert_data.get("courses", []),
            "keywords": cert_data.get("keywords", []),
            "degree": cert_data.get("degree", ""),
            "score": 0
        })

    suggested.sort(key=lambda x: x["score"], reverse=True)
    available.sort(key=lambda x: x["name"].lower())
    
    return jsonify({
        "success": True,
        "data": {
            "major": major,
            "suggested_certificates": suggested,
            "available_certificates": available,
            "selected_certificates": selected_certificates,
            "user_interests": user_interests
        }
    }), 200


@app.route('/api/clubs/<username>', methods=['GET'])
def get_user_clubs(username):
    """Get recommended clubs from user planner data and all remaining clubs."""
    username = username.strip()
    user_file_path = USERS_DIR / f"{username}.json"
    
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    clubs_dict = get_clubs()
    planner = user_data.get("planner", {})
    planner_clubs = planner.get("clubs", [])
    recommended_ids = []
    for item in planner_clubs:
        club_id = item.get("club_id") if isinstance(item, dict) else None
        if club_id and club_id in clubs_dict and club_id not in recommended_ids:
            recommended_ids.append(club_id)

    recommended_clubs = []
    for club_id in recommended_ids:
        club_info = clubs_dict.get(club_id, {})
        recommended_clubs.append({
            "id": club_id,
            "name": club_info.get("name", ""),
            "description": club_info.get("description", ""),
            "keywords": club_info.get("keywords", []),
            "contact": club_info.get("contact", {})
        })

    all_clubs = []
    for club_id, club_info in clubs_dict.items():
        if club_id in recommended_ids:
            continue
        all_clubs.append({
            "id": club_id,
            "name": club_info.get("name", ""),
            "description": club_info.get("description", ""),
            "keywords": club_info.get("keywords", []),
            "contact": club_info.get("contact", {})
        })

    selected_ids = _extract_selected_club_ids(planner)
    selected_clubs = []
    for club_id in selected_ids:
        club_info = clubs_dict.get(club_id, {})
        if not club_info:
            continue
        selected_clubs.append({
            "id": club_id,
            "name": club_info.get("name", ""),
            "description": club_info.get("description", ""),
            "keywords": club_info.get("keywords", []),
            "contact": club_info.get("contact", {})
        })

    return jsonify({
        "success": True,
        "data": {
            "username": username,
            "recommended_clubs": recommended_clubs,
            "all_clubs": all_clubs,
            "selected_clubs": selected_clubs,
            "recommended_count": len(recommended_clubs),
            "all_count": len(all_clubs)
        }
    }), 200


@app.route('/api/clubs/join', methods=['POST'])
def join_club():
    """Join a club"""
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = data.get('username', '').strip()
    club_id = data.get('club_id', '').strip()

    if not username or not club_id:
        return jsonify({"success": False, "message": "Username and club_id are required"}), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    clubs_dict = get_clubs()
    if club_id not in clubs_dict:
        return jsonify({"success": False, "message": "Club not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    planner = user_data.setdefault("planner", {})
    selected = planner.setdefault("clubs_selected", [])

    if not any((item.get("club_id") == club_id) for item in selected if isinstance(item, dict)):
        selected.append({
            "club_id": club_id,
            "club_name": clubs_dict[club_id].get("name", club_id)
        })

    planner["clubs_selected"] = selected
    user_data["planner"] = planner
    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    joined_ids = _extract_selected_club_ids(planner)
    return jsonify({
        "success": True,
        "message": f"Successfully joined {clubs_dict[club_id].get('name', club_id)}",
        "data": {
            "club_id": club_id,
            "joined_clubs": joined_ids
        }
    }), 200


@app.route('/api/clubs/leave', methods=['POST'])
def leave_club():
    """Leave a club"""
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = data.get('username', '').strip()
    club_id = data.get('club_id', '').strip()

    if not username or not club_id:
        return jsonify({"success": False, "message": "Username and club_id are required"}), 400

    user_file_path = USERS_DIR / f"{username}.json"
    if not user_file_path.exists():
        return jsonify({"success": False, "message": "User not found"}), 404

    clubs_dict = get_clubs()
    if club_id not in clubs_dict:
        return jsonify({"success": False, "message": "Club not found"}), 404

    with open(user_file_path, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    planner = user_data.setdefault("planner", {})
    selected = planner.setdefault("clubs_selected", [])
    planner["clubs_selected"] = [
        item for item in selected
        if not (isinstance(item, dict) and item.get("club_id") == club_id)
    ]
    user_data["planner"] = planner
    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    joined_ids = _extract_selected_club_ids(planner)
    return jsonify({
        "success": True,
        "message": f"Successfully left club",
        "data": {
            "club_id": club_id,
            "joined_clubs": joined_ids
        }
    }), 200


@app.route('/api/certificates/select', methods=['POST'])
def select_certificate():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    username = (data.get("username") or "").strip()
    cert_id = (data.get("certificate_id") or "").strip()
    if not username or not cert_id:
        return jsonify({"success": False, "message": "Username and certificate_id are required"}), 400

    user_file_path, user_data = _safe_user_file(username)
    if not user_file_path:
        return jsonify({"success": False, "message": "User not found"}), 404

    major = user_data.get("profile", {}).get("major", "")
    all_certificates = _get_course_module_for_major(major).get_certificates()
    if cert_id not in all_certificates:
        return jsonify({"success": False, "message": "Certificate not found"}), 404

    planner = user_data.setdefault("planner", {})
    selected = planner.setdefault("certificates_selected", [])

    if not any((item.get("certificate_id") == cert_id) for item in selected if isinstance(item, dict)):
        selected.append({
            "certificate_id": cert_id,
            "certificate_name": all_certificates[cert_id].get("name", cert_id)
        })

    planner["certificates_selected"] = selected
    user_data["planner"] = planner

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    return jsonify({
        "success": True,
        "message": "Certificate added",
        "data": {"certificate_id": cert_id, "selected": _extract_selected_certificate_ids(planner)}
    }), 200


@app.route('/api/certificates/select', methods=['DELETE'])
def unselect_certificate():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or request.args.get("username") or "").strip()
    cert_id = (data.get("certificate_id") or request.args.get("certificate_id") or "").strip()

    if not username or not cert_id:
        return jsonify({"success": False, "message": "Username and certificate_id are required"}), 400

    user_file_path, user_data = _safe_user_file(username)
    if not user_file_path:
        return jsonify({"success": False, "message": "User not found"}), 404

    planner = user_data.setdefault("planner", {})
    selected = planner.setdefault("certificates_selected", [])
    planner["certificates_selected"] = [
        item for item in selected
        if not (isinstance(item, dict) and item.get("certificate_id") == cert_id)
    ]
    user_data["planner"] = planner

    with open(user_file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

    return jsonify({
        "success": True,
        "message": "Certificate removed",
        "data": {"certificate_id": cert_id, "selected": _extract_selected_certificate_ids(planner)}
    }), 200


if __name__ == '__main__':
    init_db()
    app.run(debug=BACKEND_RUN_DEBUG, host=BACKEND_RUN_HOST, port=BACKEND_RUN_PORT)