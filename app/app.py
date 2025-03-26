from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv
import tiktoken
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Cost limits (in USD)
MAX_COST_PER_REQUEST = float(os.getenv('MAX_COST_PER_REQUEST', '0.5'))  # $0.50 by default
MONTHLY_BUDGET = float(os.getenv('MONTHLY_BUDGET', '10'))  # $10 by default

# Token limits
MAX_INPUT_TOKENS = 4000
MAX_OUTPUT_TOKENS = 4000

def estimate_tokens(text):
    """Estimate the number of tokens in a text."""
    encoding = tiktoken.get_encoding("cl100k_base")  # Works for both GPT-4 and Claude
    return len(encoding.encode(text))

def estimate_cost(input_tokens, output_tokens):
    """Estimate the cost for both APIs."""
    # GPT-3.5-turbo costs
    gpt_cost = (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000
    
    # Claude costs
    claude_cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
    
    return {
        'gpt4_cost': gpt_cost,
        'claude_cost': claude_cost,
        'total_cost': gpt_cost + claude_cost
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/estimate', methods=['POST'])
def estimate_request():
    """Endpoint to estimate tokens and cost before processing."""
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    input_tokens = estimate_tokens(code)
    estimated_output_tokens = min(input_tokens * 2, MAX_OUTPUT_TOKENS)  # Rough estimate
    
    cost_estimate = estimate_cost(input_tokens, estimated_output_tokens)
    
    if cost_estimate['total_cost'] > MAX_COST_PER_REQUEST:
        return jsonify({
            'error': 'Estimated cost exceeds maximum allowed cost per request',
            'estimated_cost': cost_estimate,
            'max_allowed': MAX_COST_PER_REQUEST
        }), 400
    
    if input_tokens > MAX_INPUT_TOKENS:
        return jsonify({
            'error': 'Input code is too long',
            'tokens': input_tokens,
            'max_allowed': MAX_INPUT_TOKENS
        }), 400
    
    return jsonify({
        'input_tokens': input_tokens,
        'estimated_output_tokens': estimated_output_tokens,
        'estimated_cost': cost_estimate
    })

@app.route('/explain', methods=['POST'])
def explain_code():
    code = request.json.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # First, get the estimate
    input_tokens = estimate_tokens(code)
    estimated_output_tokens = min(input_tokens * 2, MAX_OUTPUT_TOKENS)
    cost_estimate = estimate_cost(input_tokens, estimated_output_tokens)
    
    # Check limits
    if cost_estimate['total_cost'] > MAX_COST_PER_REQUEST:
        return jsonify({
            'error': 'Estimated cost exceeds maximum allowed cost per request',
            'estimated_cost': cost_estimate,
            'max_allowed': MAX_COST_PER_REQUEST
        }), 400
    
    if input_tokens > MAX_INPUT_TOKENS:
        return jsonify({
            'error': 'Input code is too long',
            'tokens': input_tokens,
            'max_allowed': MAX_INPUT_TOKENS
        }), 400

    # Get explanations
    gpt_explanation = get_gpt4_explanation(code, max_tokens=MAX_OUTPUT_TOKENS)
    claude_explanation = get_claude_explanation(code, max_tokens=MAX_OUTPUT_TOKENS)
    
    actual_output_tokens = estimate_tokens(gpt_explanation) + estimate_tokens(claude_explanation)
    actual_cost = estimate_cost(input_tokens, actual_output_tokens)

    return jsonify({
        'gpt_explanation': gpt_explanation,
        'claude_explanation': claude_explanation,
        'usage': {
            'input_tokens': input_tokens,
            'output_tokens': actual_output_tokens,
            'cost': actual_cost
        }
    })

def get_gpt4_explanation(code, max_tokens=None):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that explains code in plain English.'},
            {'role': 'user', 'content': f'Please explain this code in simple terms:\n\n{code}'}
        ],
        'max_tokens': max_tokens
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f'Error getting GPT-3.5 explanation: {response.text}'
    except Exception as e:
        return f'Error: {str(e)}'

def get_claude_explanation(code, max_tokens=None):
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    }
    
    data = {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': max_tokens if max_tokens else 1024,
        'messages': [
            {
                'role': 'user',
                'content': f'Please explain this code in simple terms:\n\n{code}'
            }
        ]
    }
    
    try:
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=10
        )
        
        response_text = response.text
        print(f"Claude API Response: {response_text}")  # Debug logging
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        elif response.status_code == 401:
            return f'Authentication error. Please check your Claude API key. Full error: {response_text}'
        else:
            return f'Error getting Claude explanation (Status {response.status_code}): {response_text}'
    except Exception as e:
        return f'Error: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True) 