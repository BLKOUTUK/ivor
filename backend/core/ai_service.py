"""
AI Service for IVOR - Handles LLM interactions with DeepSeek and Qwen
"""

import httpx
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from core.config import settings
from core.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """AI response data structure"""
    message: str
    sources: List[Dict[str, Any]]
    suggestions: List[str]
    timestamp: datetime
    model_used: str
    confidence: float = 0.8

class AIService:
    """AI Service for processing messages and generating responses"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.deepseek_client = self._create_http_client()
        self.system_prompt = self._create_system_prompt()
        
    def _create_http_client(self) -> httpx.AsyncClient:
        """Create HTTP client for API calls"""
        return httpx.AsyncClient(timeout=30.0)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt aligned with BLKOUT values"""
        return f"""You are IVOR, BLKOUT's community AI assistant. You embody our core values:

{chr(10).join(f'• {value}' for value in settings.BLKOUT_VALUES)}

Your role is to:
- Facilitate authentic connections within the BLKOUT community
- Provide information about cooperative ownership and community initiatives
- Help community members discover events and resources
- Maintain genuine, values-driven conversations (not conversion-focused)
- Support Black queer liberation and cooperative ownership movements

Always respond with warmth, authenticity, and community focus. When you don't know something, be honest and offer to connect users with community members who might help.

Community context: BLKOUT is building cooperative ownership together through dialogue, complexity, and authentic community engagement."""

    async def process_message(
        self, 
        message: str, 
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Process user message and generate AI response"""
        
        try:
            # Retrieve relevant knowledge from knowledge base
            knowledge_results = await self.knowledge_base.search(
                query=message,
                limit=3
            )
            
            # Prepare context for AI
            enhanced_context = self._prepare_context(message, knowledge_results, context)
            
            # Try DeepSeek first (primary LLM)
            response = await self._call_deepseek(message, enhanced_context)
            
            if not response:
                # Fallback to Qwen if DeepSeek fails
                logger.warning("DeepSeek failed, falling back to Qwen")
                response = await self._call_qwen(message, enhanced_context)
            
            if not response:
                # Final fallback to simple response
                response = self._create_fallback_response(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._create_error_response()
    
    def _prepare_context(
        self, 
        message: str, 
        knowledge_results: List[Dict], 
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Prepare enhanced context for AI"""
        
        enhanced_context = {
            "user_message": message,
            "relevant_knowledge": knowledge_results,
            "community_values": settings.BLKOUT_VALUES,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            enhanced_context.update(context)
            
        return enhanced_context
    
    async def _call_deepseek(self, message: str, context: Dict[str, Any]) -> Optional[AIResponse]:
        """Call DeepSeek API"""
        
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API key not configured")
            return None
            
        try:
            # Prepare knowledge context
            knowledge_context = ""
            if context.get("relevant_knowledge"):
                knowledge_context = "\\n\\nRelevant community knowledge:\\n"
                for item in context["relevant_knowledge"]:
                    knowledge_context += f"- {item.get('content', '')[:200]}...\\n"
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"{message}{knowledge_context}"}
            ]
            
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = await self.deepseek_client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result["choices"][0]["message"]["content"]
                
                return AIResponse(
                    message=ai_message,
                    sources=context.get("relevant_knowledge", []),
                    suggestions=self._generate_suggestions(message, ai_message),
                    timestamp=datetime.now(),
                    model_used="deepseek-chat",
                    confidence=0.9
                )
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {str(e)}")
            return None
    
    async def _call_qwen(self, message: str, context: Dict[str, Any]) -> Optional[AIResponse]:
        """Call Qwen API as fallback"""
        
        if not settings.QWEN_API_KEY:
            logger.warning("Qwen API key not configured")
            return None
            
        try:
            # Prepare knowledge context
            knowledge_context = ""
            if context.get("relevant_knowledge"):
                knowledge_context = "\\n\\nRelevant community knowledge:\\n"
                for item in context["relevant_knowledge"]:
                    knowledge_context += f"- {item.get('content', '')[:200]}...\\n"
            
            payload = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"{message}{knowledge_context}"}
                    ]
                },
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            }
            
            headers = {
                "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = await self.deepseek_client.post(
                f"{settings.QWEN_BASE_URL}/services/aigc/text-generation/generation",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result["output"]["text"]
                
                return AIResponse(
                    message=ai_message,
                    sources=context.get("relevant_knowledge", []),
                    suggestions=self._generate_suggestions(message, ai_message),
                    timestamp=datetime.now(),
                    model_used="qwen-turbo",
                    confidence=0.8
                )
            else:
                logger.error(f"Qwen API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Qwen API call failed: {str(e)}")
            return None
    
    def _generate_suggestions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate conversation suggestions"""
        
        # Simple suggestion generation based on keywords
        suggestions = []
        
        if "cooperative" in user_message.lower() or "cooperative" in ai_response.lower():
            suggestions.append("Tell me more about starting a cooperative")
            
        if "event" in user_message.lower() or "event" in ai_response.lower():
            suggestions.append("What events are happening this week?")
            
        if "community" in user_message.lower():
            suggestions.append("How can I get more involved in the community?")
            
        # Default suggestions
        if not suggestions:
            suggestions = [
                "What's happening in the community?",
                "Tell me about BLKOUT's values",
                "How do I connect with other members?"
            ]
            
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _create_fallback_response(self, message: str) -> AIResponse:
        """Create fallback response when AI APIs fail"""
        
        fallback_message = """I'm having some technical difficulties right now, but I'm here to help! 
        
Our community believes in authentic dialogue and cooperative ownership. While I sort out my technical issues, you might want to:

• Check out our upcoming community events
• Connect with other community members
• Explore our resources on cooperative ownership

Is there something specific about our community or cooperative ownership you'd like to know about?"""
        
        return AIResponse(
            message=fallback_message,
            sources=[],
            suggestions=[
                "What events are coming up?",
                "Tell me about BLKOUT's values",
                "How do cooperatives work?"
            ],
            timestamp=datetime.now(),
            model_used="fallback",
            confidence=0.5
        )
    
    def _create_error_response(self) -> AIResponse:
        """Create error response"""
        
        error_message = """I'm experiencing some technical difficulties. Our community values authentic connection, so let me be real with you - something's not working quite right on my end! 

Please try again in a moment, or feel free to reach out to our community directly. We're always here for genuine conversation and support."""
        
        return AIResponse(
            message=error_message,
            sources=[],
            suggestions=["Try asking again", "Contact the community"],
            timestamp=datetime.now(),
            model_used="error",
            confidence=0.1
        )