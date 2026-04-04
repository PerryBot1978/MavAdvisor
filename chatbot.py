from openai import OpenAI
from flask import request, jsonify
from shared import app
client = OpenAI()

@app.route('/chatbot/request', methods=['POST'])
def chatbot_request():
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'Missing messages field'}), 400
        
        messages = data['messages']
        # Validate messages format
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({'error': 'Messages must be a non-empty list'}), 400
        
        messages.insert(0, {
            'role': 'system',
            'content': f'''
                The user is an Engineering major at the University of Texas Arlington.
                You should focus on helping the student plan courses, certifications, and clubs.
                Your response should be readable as plain text, not using any special features (i.e. Markdown).
            '''
        })

        # Call OpenAI Chat Completions API
        response = client.chat.completions.create(
            model='gpt-5.2',
            messages=messages
        )
        
        # Extract assistant's reply
        if response.choices and len(response.choices) > 0:
            bot_response = response.choices[0].message.content
        else:
            bot_response = "No response generated."
        
        return jsonify({'response': bot_response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
