#!/usr/bin/env python3
"""
Quick test of Mixtral integration without full FastAPI setup
"""

import asyncio
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

async def test_groq():
    """Test Groq API with Mixtral"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found")
        return False
    
    print("🚀 Testing Groq Mixtral...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [
                    {"role": "system", "content": "You are IVOR, BLKOUT's community AI assistant focused on cooperative ownership and Black queer liberation."},
                    {"role": "user", "content": "What is BLKOUT about?"}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result["choices"][0]["message"]["content"]
                print(f"✅ Groq Success!")
                print(f"📝 Response: {message[:200]}...")
                return True
            else:
                print(f"❌ Groq Error: {response.status_code}")
                print(f"📄 Details: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Groq Exception: {str(e)}")
        return False

async def test_huggingface():
    """Test Hugging Face API with Mixtral"""
    api_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not api_token:
        print("❌ HUGGINGFACE_API_TOKEN not found")
        return False
    
    print("🤗 Testing Hugging Face Mixtral...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            prompt = """<s>[INST] You are IVOR, BLKOUT's community AI assistant focused on cooperative ownership and Black queer liberation.

User message: What is BLKOUT about? [/INST]"""
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    message = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    message = result.get("generated_text", "")
                else:
                    message = str(result)
                
                if message.strip():
                    print(f"✅ Hugging Face Success!")
                    print(f"📝 Response: {message[:200]}...")
                    return True
                else:
                    print(f"❌ Hugging Face: Empty response")
                    return False
            else:
                print(f"❌ Hugging Face Error: {response.status_code}")
                print(f"📄 Details: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Hugging Face Exception: {str(e)}")
        return False

async def main():
    print("🤖 Testing IVOR Mixtral Integration\n")
    
    # Test both APIs
    groq_success = await test_groq()
    print()
    hf_success = await test_huggingface()
    print()
    
    # Summary
    if groq_success or hf_success:
        print("🎉 IVOR is ready! At least one API is working.")
        if groq_success:
            print("   → Groq will be primary (fastest)")
        if hf_success:
            print("   → Hugging Face available as backup")
    else:
        print("❌ No APIs working. Check your keys and internet connection.")

if __name__ == "__main__":
    asyncio.run(main())