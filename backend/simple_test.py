#!/usr/bin/env python3
"""
Simple test using only built-in Python modules
"""

import urllib.request
import urllib.parse
import json
import os

def load_env():
    """Simple .env loader"""
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("❌ .env file not found")
    return env_vars

def test_groq(api_key):
    """Test Groq API with built-in urllib"""
    print("🚀 Testing Groq Mixtral...")
    
    try:
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {"role": "system", "content": "You are IVOR, BLKOUT's community AI assistant."},
                {"role": "user", "content": "What is BLKOUT about?"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
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
            message = result["choices"][0]["message"]["content"]
            print(f"✅ Groq Success!")
            print(f"📝 Response: {message[:150]}...")
            return True
            
    except Exception as e:
        print(f"❌ Groq Error: {str(e)}")
        return False

def test_huggingface(api_token):
    """Test Hugging Face API with built-in urllib"""
    print("🤗 Testing Hugging Face Mixtral...")
    
    try:
        prompt = """<s>[INST] You are IVOR, BLKOUT's community AI assistant.

User message: What is BLKOUT about? [/INST]"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        request = urllib.request.Request(
            "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
            data=data,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode())
            
            if isinstance(result, list) and len(result) > 0:
                message = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                message = result.get("generated_text", "")
            else:
                message = str(result)
            
            if message.strip():
                print(f"✅ Hugging Face Success!")
                print(f"📝 Response: {message[:150]}...")
                return True
            else:
                print(f"❌ Hugging Face: Empty response")
                return False
                
    except Exception as e:
        print(f"❌ Hugging Face Error: {str(e)}")
        return False

def main():
    print("🤖 Testing IVOR Mixtral Integration (Simple Test)\n")
    
    # Load environment variables
    env_vars = load_env()
    groq_key = env_vars.get("GROQ_API_KEY")
    hf_token = env_vars.get("HUGGINGFACE_API_TOKEN")
    
    if not groq_key and not hf_token:
        print("❌ No API keys found in .env file")
        return
    
    # Test APIs
    groq_success = test_groq(groq_key) if groq_key else False
    print()
    hf_success = test_huggingface(hf_token) if hf_token else False
    print()
    
    # Summary
    if groq_success or hf_success:
        print("🎉 IVOR Mixtral APIs are working!")
        print(f"💰 Cost: $0/month for reasonable usage")
        if groq_success:
            print("   → Groq: ✅ Primary (fastest)")
        if hf_success:
            print("   → Hugging Face: ✅ Backup")
    else:
        print("❌ No APIs working. Check your keys and internet connection.")

if __name__ == "__main__":
    main()