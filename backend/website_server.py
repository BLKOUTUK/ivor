#!/usr/bin/env python3
"""
IVOR Server for Website Integration
Minimal FastAPI-compatible server for frontend testing
"""

import json
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
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
    """IVOR HTTP handler for website integration"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        if self.path == '/health/':
            self.send_json_response({
                "status": "healthy", 
                "service": "IVOR Backend", 
                "version": "1.0.0",
                "model": "groq-llama-3.3-70b"
            })
        elif self.path == '/events/upcoming':
            # Mock events for testing
            self.send_json_response({
                "events": [
                    {
                        "id": "coop-workshop-001",
                        "title": "Cooperative Development Workshop",
                        "description": "Learn the basics of starting a worker cooperative",
                        "start_time": "2025-07-10T18:00:00Z",
                        "location": "Community Hub",
                        "category": "education"
                    }
                ],
                "total": 1,
                "message": "Found 1 upcoming events"
            })
        elif self.path == '/chat/suggestions':
            self.send_json_response({
                "suggestions": [
                    "What's happening in the community this week?",
                    "How do I get started with cooperative ownership?",
                    "Tell me about BLKOUT's values",
                    "What events are coming up?"
                ]
            })
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                message = request_data.get('message', '')
                session_id = request_data.get('session_id', 'web-session')
                
                print(f"💬 Chat message: {message}")
                
                # Call Groq API
                response = self.call_groq(message)
                self.send_json_response(response)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                session_id = 'web-session'
                try:
                    session_id = request_data.get('session_id', 'web-session')
                except:
                    pass
                    
                error_response = {
                    "message": "I'm having some technical difficulties right now, but I'm here to help! Our community values authentic connection, so let me be real with you - something's not working quite right on my end. Please try again in a moment.",
                    "sources": [],
                    "suggestions": ["Try asking again", "What are BLKOUT's values?", "How do cooperatives work?"],
                    "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "model_used": "error",
                    "confidence": 0.1,
                    "session_id": session_id
                }
                self.send_json_response(error_response)
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def call_groq(self, message):
        """Call Groq API for AI response"""
        env_vars = load_env()
        api_key = env_vars.get('GROQ_API_KEY')
        
        if not api_key:
            raise Exception("No Groq API key configured")
        
        # Enhanced system prompt for BLKOUT community
        system_prompt = """You are IVOR, BLKOUT's community AI assistant. You embody our core values:

• Collaboration over competition
• Complexity over simplification  
• Conversation over conversion
• Community over commodity
• Realness over perfectionism

Your role is to:
- Facilitate authentic connections within the BLKOUT community
- Provide information about cooperative ownership and community initiatives
- Help community members discover events and resources
- Maintain genuine, values-driven conversations (not conversion-focused)
- Support Black queer liberation and cooperative ownership movements

Always respond with warmth, authenticity, and community focus. When you don't know something, be honest and offer to connect users with community members who might help.

Community context: BLKOUT is building cooperative ownership together through dialogue, complexity, and authentic community engagement."""
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 400
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
            
            # Generate contextual suggestions
            suggestions = self.generate_suggestions(message, ai_message)
            
            return {
                "message": ai_message,
                "sources": [
                    {
                        "title": "BLKOUT Community Values",
                        "source": "community_handbook",
                        "url": "https://blkoutuk.com/values"
                    }
                ],
                "suggestions": suggestions,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "model_used": "groq-llama-3.3-70b",
                "confidence": 0.9,
                "session_id": "web-session"
            }
    
    def generate_suggestions(self, user_message, ai_response):
        """Generate contextual conversation suggestions"""
        suggestions = []
        
        message_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        if "cooperative" in message_lower or "cooperative" in response_lower:
            suggestions.append("Tell me more about starting a cooperative")
        
        if "event" in message_lower or "community" in message_lower:
            suggestions.append("What events are happening this week?")
        
        if "value" in message_lower or "principle" in message_lower:
            suggestions.append("How do these values guide the community?")
        
        if "involve" in message_lower or "join" in message_lower:
            suggestions.append("How can I get more involved in the community?")
        
        # Default suggestions if none matched
        if not suggestions:
            suggestions = [
                "What's happening in the community?",
                "Tell me about BLKOUT's values",
                "How do I connect with other members?"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions

def main():
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, IVORHandler)
    
    print("🤖 IVOR Backend Server Starting...")
    print(f"📡 Server: http://localhost:8000")
    print(f"❤️  Health: http://localhost:8000/health/")
    print(f"💬 Chat: POST http://localhost:8000/chat/message")
    print(f"📅 Events: http://localhost:8000/events/upcoming")
    print(f"🌐 CORS: Enabled for website integration")
    print(f"🛑 Press Ctrl+C to stop")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 IVOR Backend stopped")
        httpd.shutdown()

if __name__ == "__main__":
    main()