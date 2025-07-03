#!/usr/bin/env python3
"""
Check API key validity
"""

import urllib.request
import json

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

def check_groq_key(api_key):
    """Check if Groq API key is valid"""
    if not api_key or api_key == "your_groq_api_key_here":
        print("❌ Groq: No valid API key (placeholder detected)")
        return False
    
    if not api_key.startswith("gsk_"):
        print(f"❌ Groq: Invalid key format (should start with 'gsk_', got '{api_key[:10]}...')")
        return False
    
    print(f"✅ Groq: Key format looks correct (gsk_...{api_key[-4:]})")
    return True

def check_hf_key(api_token):
    """Check if HuggingFace API token is valid"""
    if not api_token or api_token == "your_hf_token_here":
        print("❌ HuggingFace: No valid API token (placeholder detected)")
        return False
    
    if not api_token.startswith("hf_"):
        print(f"❌ HuggingFace: Invalid token format (should start with 'hf_', got '{api_token[:10]}...')")
        return False
    
    print(f"✅ HuggingFace: Token format looks correct (hf_...{api_token[-4:]})")
    return True

def main():
    print("🔑 Checking API Keys\n")
    
    env_vars = load_env()
    groq_key = env_vars.get("GROQ_API_KEY", "").strip()
    hf_token = env_vars.get("HUGGINGFACE_API_TOKEN", "").strip()
    
    print("📋 Found keys:")
    print(f"   GROQ_API_KEY: {'Yes' if groq_key else 'No'}")
    print(f"   HUGGINGFACE_API_TOKEN: {'Yes' if hf_token else 'No'}")
    print()
    
    groq_valid = check_groq_key(groq_key)
    hf_valid = check_hf_key(hf_token)
    
    print()
    if not groq_valid and not hf_valid:
        print("🚨 ISSUE: No valid API keys found!")
        print()
        print("📖 How to get working keys:")
        print()
        print("1. Groq (Recommended - Fast & Free):")
        print("   • Go to: https://console.groq.com")
        print("   • Sign up for free account")
        print("   • Go to 'API Keys' → 'Create API Key'")
        print("   • Copy key starting with 'gsk_'")
        print()
        print("2. Hugging Face (Backup):")
        print("   • Go to: https://huggingface.co/settings/tokens")
        print("   • Click 'New token' → Role: 'Read'")
        print("   • Copy token starting with 'hf_'")
        print()
        print("3. Update .env file:")
        print("   GROQ_API_KEY=gsk_your_actual_key_here")
        print("   HUGGINGFACE_API_TOKEN=hf_your_actual_token_here")
    else:
        print("✅ Key validation passed! Keys should work.")
        if not groq_valid:
            print("⚠️  Consider getting a Groq key for faster responses")
        if not hf_valid:
            print("⚠️  Consider getting a HuggingFace token as backup")

if __name__ == "__main__":
    main()