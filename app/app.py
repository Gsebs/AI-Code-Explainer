from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/explain', methods=['POST'])
def explain_code():
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # Get GPT-4 explanation
    gpt_explanation = get_gpt4_explanation(code)
    
    # Get Claude explanation
    claude_explanation = get_claude_explanation(code)

    return jsonify({
        'gpt_explanation': gpt_explanation,
        'claude_explanation': claude_explanation
    })

def get_gpt4_explanation(code):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-4',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that explains code in plain English.'},
            {'role': 'user', 'content': f'Please explain this code in simple terms:\n\n{code}'}
        ]
    }
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return 'Error getting GPT-4 explanation'

def get_claude_explanation(code):
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'claude-3-sonnet-20240229',
        'messages': [
            {
                'role': 'user',
                'content': f'Please explain this code in simple terms:\n\n{code}'
            }
        ]
    }
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    return 'Error getting Claude explanation'

if __name__ == '__main__':
    app.run(debug=True) 