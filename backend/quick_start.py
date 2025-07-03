#!/usr/bin/env python3
"""
Quick FastAPI test without dependencies
"""

import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

def load_env():
    """Load .env file"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        pass
    return env_vars

class IVORHandler(BaseHTTPRequestHandler):
    """Simple IVOR HTTP handler"""
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "healthy", "service": "IVOR", "model": "llama-3.3-70b"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat/message':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                message = request_data.get('message', '')
                
                # Call Groq API
                response = self.call_groq(message)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {
                    "message": f"I'm having technical difficulties: {str(e)}",
                    "sources": [],
                    "suggestions": ["Try again", "Check connection"],
                    "model_used": "error"
                }
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def call_groq(self, message):
        """Call Groq API"""
        env_vars = load_env()
        api_key = env_vars.get('GROQ_API_KEY')
        
        if not api_key:
            raise Exception("No Groq API key found")
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are IVOR, BLKOUT's community AI assistant. You embody values of cooperative ownership, Black queer liberation, and authentic community dialogue. Respond warmly and focus on building community connections."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
            ai_message = result["choices"][0]["message"]["content"]
            
            return {
                "message": ai_message,
                "sources": [],
                "suggestions": [
                    "Tell me about BLKOUT's values",
                    "What events are coming up?",
                    "How can I get involved?"
                ],
                "timestamp": "2025-07-03T16:00:00Z",
                "model_used": "groq-llama-3.3-70b",
                "confidence": 0.9
            }

def start_server():
    """Start simple IVOR server"""
    server = HTTPServer(('localhost', 8000), IVORHandler)
    print("🤖 IVOR Server starting on http://localhost:8000")
    print("📡 Health check: http://localhost:8000/health")
    print("💬 Send message: POST http://localhost:8000/chat/message")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 IVOR Server stopped")
        server.shutdown()

if __name__ == "__main__":
    start_server()