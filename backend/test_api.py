#!/usr/bin/env python3
"""
API Test Script for BLKOUT Community Data System
Tests all API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime

class APITester:
    """Test all API endpoints"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        
        print("🔍 Testing Health Endpoint...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                self.log_success("Health Check", "✅ Health endpoint working")
            else:
                self.log_error("Health Check", f"❌ Health check failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Health Check", f"❌ Health check error: {str(e)}")
    
    async def test_community_profile_creation(self):
        """Test community profile creation"""
        
        print("👤 Testing Community Profile Creation...")
        
        try:
            profile_data = {
                "email": "test@blkoutuk.com",
                "name": "Test User",
                "location": "London",
                "source": "email_capture",
                "consent_preferences": {
                    "anonymous_only": False,
                    "personal_service": True,
                    "community_insights": True,
                    "peer_connections": False
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/community/profile",
                json=profile_data
            )
            
            if response.status_code == 200:
                self.log_success("Profile Creation", "✅ Profile creation working")
                return response.json()
            else:
                self.log_error("Profile Creation", f"❌ Profile creation failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_error("Profile Creation", f"❌ Profile creation error: {str(e)}")
            return None
    
    async def test_email_subscription(self):
        """Test email subscription endpoint"""
        
        print("📧 Testing Email Subscription...")
        
        try:
            subscription_data = {
                "email": "test@blkoutuk.com",
                "interests": ["newsletter", "events", "movement-updates"],
                "source": "homepage",
                "engagement_level": "active",
                "blkouthub_interest": True,
                "referrer": "direct"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/community/email-subscription",
                json=subscription_data
            )
            
            if response.status_code == 200:
                self.log_success("Email Subscription", "✅ Email subscription working")
            else:
                self.log_error("Email Subscription", f"❌ Email subscription failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Email Subscription", f"❌ Email subscription error: {str(e)}")
    
    async def test_quiz_result_submission(self):
        """Test quiz result submission"""
        
        print("🧩 Testing Quiz Result Submission...")
        
        try:
            quiz_data = {
                "email": "test@blkoutuk.com",
                "pathway": "storyteller",
                "pathway_title": "THE STORYTELLER",
                "scores": {
                    "identity": 4,
                    "community": 3,
                    "liberation": 2,
                    "connection": 3
                },
                "answers": {
                    "energy_source": "Creating something beautiful",
                    "safe_space": "Creative studio or workshop"
                },
                "community_match": "Creative Community & StoryLab",
                "next_steps": [
                    "Join our StoryLab workshops",
                    "Contribute to the BLKOUT Channel"
                ]
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/community/quiz-result",
                json=quiz_data
            )
            
            if response.status_code == 200:
                self.log_success("Quiz Submission", "✅ Quiz result submission working")
            else:
                self.log_error("Quiz Submission", f"❌ Quiz submission failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Quiz Submission", f"❌ Quiz submission error: {str(e)}")
    
    async def test_ivor_chat(self):
        """Test IVOR chat endpoint"""
        
        print("🤖 Testing IVOR Chat...")
        
        try:
            chat_data = {
                "message": "Hello IVOR, how can you help me?",
                "user_email": "test@blkoutuk.com",
                "consent_level": "personal_service",
                "context": {
                    "test": True
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/message",
                json=chat_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_success("IVOR Chat", "✅ IVOR chat working")
                else:
                    self.log_error("IVOR Chat", "❌ IVOR chat response invalid")
            else:
                self.log_error("IVOR Chat", f"❌ IVOR chat failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("IVOR Chat", f"❌ IVOR chat error: {str(e)}")
    
    async def test_conversation_history(self):
        """Test conversation history endpoint"""
        
        print("💬 Testing Conversation History...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/conversations/history/test@blkoutuk.com?limit=5"
            )
            
            if response.status_code == 200:
                self.log_success("Conversation History", "✅ Conversation history working")
            elif response.status_code == 404:
                self.log_success("Conversation History", "✅ Conversation history endpoint working (no data)")
            else:
                self.log_error("Conversation History", f"❌ Conversation history failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Conversation History", f"❌ Conversation history error: {str(e)}")
    
    async def test_unified_profile(self):
        """Test unified profile endpoint"""
        
        print("🔍 Testing Unified Profile...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/profiles/profile/test@blkoutuk.com"
            )
            
            if response.status_code == 200:
                self.log_success("Unified Profile", "✅ Unified profile working")
            elif response.status_code == 404:
                self.log_success("Unified Profile", "✅ Unified profile endpoint working (no data)")
            else:
                self.log_error("Unified Profile", f"❌ Unified profile failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Unified Profile", f"❌ Unified profile error: {str(e)}")
    
    async def test_community_analytics(self):
        """Test community analytics endpoints"""
        
        print("📊 Testing Community Analytics...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/community/analytics/community-insights"
            )
            
            if response.status_code == 200:
                self.log_success("Community Analytics", "✅ Community analytics working")
            else:
                self.log_error("Community Analytics", f"❌ Community analytics failed: {response.status_code}")
                
        except Exception as e:
            self.log_error("Community Analytics", f"❌ Community analytics error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all API tests"""
        
        print("🧪 BLKOUT Community Data System - API Tests")
        print("=" * 60)
        
        await self.test_health_endpoint()
        await self.test_community_profile_creation()
        await self.test_email_subscription()
        await self.test_quiz_result_submission()
        await self.test_ivor_chat()
        await self.test_conversation_history()
        await self.test_unified_profile()
        await self.test_community_analytics()
        
        await self.client.aclose()
        
        # Print results
        self.print_results()
    
    def log_success(self, test_name, message):
        """Log successful test"""
        self.test_results.append({"test": test_name, "status": "PASS", "message": message})
        print(f"  {message}")
    
    def log_error(self, test_name, message):
        """Log failed test"""
        self.test_results.append({"test": test_name, "status": "FAIL", "message": message})
        print(f"  {message}")
    
    def print_results(self):
        """Print test results summary"""
        
        print("\n" + "=" * 60)
        print("🧪 API TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)

async def main():
    """Run API tests"""
    
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())