import json
from flask import Response, render_template
from shared import app
from config import (
    FRONTEND_BASE_URL,
    FRONTEND_LOGIN_URL,
    FRONTEND_REGISTER_URL,
    FRONTEND_RUN_DEBUG,
    FRONTEND_RUN_HOST,
    FRONTEND_RUN_PORT,
)

import admin_endpoint
import user_endpoint
import chatbot_endpoint


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/config.js')
def runtime_config_js():
    payload = {
        "API_BASE_URL": "",
        "FRONTEND_BASE_URL": FRONTEND_BASE_URL,
        "FRONTEND_LOGIN_URL": FRONTEND_LOGIN_URL,
        "FRONTEND_REGISTER_URL": FRONTEND_REGISTER_URL,
    }

    lines = [f"const {k} = {json.dumps(v)};" for k, v in payload.items()]
    return Response("\n".join(lines) + "\n", mimetype='application/javascript')


if __name__ == '__main__':
    app.run(debug=FRONTEND_RUN_DEBUG, host=FRONTEND_RUN_HOST, port=FRONTEND_RUN_PORT)