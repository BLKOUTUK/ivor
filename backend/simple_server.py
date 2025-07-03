#!/usr/bin/env python3
import json, urllib.request, time
from http.server import HTTPServer, BaseHTTPRequestHandler

def load_env():
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except: 
        pass
    return env_vars

class IVORHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): 
        pass
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health/':
            self.send_json({'status': 'healthy', 'service': 'IVOR', 'model': 'llama-3.3-70b'})
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat/message':
            try:
                length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(length).decode())
                message = data.get('message', '')
                
                env = load_env()
                api_key = env.get('GROQ_API_KEY')
                
                payload = {
                    'model': 'llama-3.3-70b-versatile',
                    'messages': [
                        {'role': 'system', 'content': 'You are IVOR, BLKOUT community AI assistant focused on cooperative ownership and Black queer liberation. Respond warmly and authentically.'},
                        {'role': 'user', 'content': message}
                    ],
                    'max_tokens': 200
                }
                
                req = urllib.request.Request(
                    'https://api.groq.com/openai/v1/chat/completions',
                    data=json.dumps(payload).encode(),
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read().decode())
                    ai_message = result['choices'][0]['message']['content']
                    
                    self.send_json({
                        'message': ai_message,
                        'sources': [],
                        'suggestions': ['Tell me more about BLKOUT', 'What events are coming up?', 'How can I get involved?'],
                        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'model_used': 'groq-llama-3.3-70b',
                        'confidence': 0.9,
                        'session_id': data.get('session_id', 'web')
                    })
                    
            except Exception as e:
                print(f"Error: {e}")
                self.send_json({
                    'message': 'I am having some technical difficulties. Our community values authentic connection, so let me be real - something is not working quite right! Please try again.',
                    'sources': [], 
                    'suggestions': ['Try again', 'What are BLKOUT values?'],
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'model_used': 'error', 
                    'confidence': 0.1, 
                    'session_id': 'web'
                })
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    print('🤖 IVOR Backend starting on http://localhost:8000')
    HTTPServer(('localhost', 8000), IVORHandler).serve_forever()