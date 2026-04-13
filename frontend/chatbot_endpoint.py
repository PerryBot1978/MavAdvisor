import json
from urllib.error import URLError
from urllib.request import urlopen

from flask import jsonify, request
from openai import OpenAI

from config import BACKEND_API_BASE, BACKEND_USERS_DIR, OPENAI_API_KEY, OPENAI_MODEL
from shared import app


client = OpenAI(api_key=OPENAI_API_KEY or None)
USER_FILES_DIR = BACKEND_USERS_DIR


def _fetch_backend_json(path: str):
    url = f"{BACKEND_API_BASE}{path}"
    try:
        with urlopen(url, timeout=8) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except (URLError, TimeoutError, json.JSONDecodeError):
        return None


@app.route('/chatbot/request', methods=['POST'])
def chatbot_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400

        username = (data.get('username') or '').strip()
        messages = data.get('messages')

        if not username:
            return jsonify({'error': 'Missing username'}), 400

        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({'error': 'Messages must be a non-empty list'}), 400

        if not OPENAI_API_KEY:
            return jsonify({'error': 'Missing OPENAI_API_KEY environment variable'}), 500

        user_file_path = USER_FILES_DIR / f"{username}.json"
        if not user_file_path.exists():
            return jsonify({'error': 'User profile not found'}), 404

        with open(user_file_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)

        progress = _fetch_backend_json(f"/api/user/{username}")
        certificates = _fetch_backend_json(f"/api/certificates/{username}")
        clubs = _fetch_backend_json(f"/api/clubs/{username}")

        system_prompt = (
            "You are MavAdvisor, a concise and helpful academic planning assistant for UTA engineering students. "
            "Use the user context to provide personalized recommendations for courses, certifications, clubs, and planning. "
            "Do not expose raw JSON unless asked. Respond as plain text (no Markdown). "
            "If data is missing, state assumptions clearly and suggest next steps.\n\n"
            f"Logged-in username: {username}\n"
            f"User JSON: {json.dumps(user_data, ensure_ascii=True)}\n"
            f"Progress API: {json.dumps(progress, ensure_ascii=True)}\n"
            f"Certificates API: {json.dumps(certificates, ensure_ascii=True)}\n"
            f"Clubs API: {json.dumps(clubs, ensure_ascii=True)}"
        )

        model_messages = [{'role': 'system', 'content': system_prompt}] + messages

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=model_messages,
        )

        if response.choices and len(response.choices) > 0:
            bot_response = response.choices[0].message.content or "No response generated."
        else:
            bot_response = "No response generated."

        return jsonify({'response': bot_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
