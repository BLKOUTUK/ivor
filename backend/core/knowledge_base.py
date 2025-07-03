"""
Knowledge Base for IVOR - ChromaDB integration for community knowledge
"""

import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from core.config import settings

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """ChromaDB-based knowledge base for community information"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    async def initialize(self):
        """Initialize ChromaDB and embedding model"""
        
        try:
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "BLKOUT community knowledge base"}
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info(f"Knowledge base initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {str(e)}")
            raise
    
    async def load_initial_knowledge(self):
        """Load initial community knowledge into the database"""
        
        if self.collection.count() > 0:
            logger.info("Knowledge base already contains documents, skipping initial load")
            return
        
        # BLKOUT community knowledge
        initial_knowledge = [
            {
                "id": "blkout_values",
                "content": f"""BLKOUT Core Values:
                
{chr(10).join(f'• {value}' for value in settings.BLKOUT_VALUES)}

These values guide everything we do as a community. We believe in building through dialogue, embracing complexity rather than oversimplification, and fostering authentic connections over transactional relationships.""",
                "metadata": {
                    "category": "values",
                    "title": "BLKOUT Core Values",
                    "source": "community_handbook"
                }
            },
            {
                "id": "cooperative_basics",
                "content": """What is a Cooperative?

A cooperative is a business or organization owned and operated by the people who use its services or work there. Key principles include:

• Democratic control - each member has a voice
• Shared ownership - members own the cooperative together
• Economic participation - members contribute to and benefit from the cooperative
• Autonomy and independence - cooperatives are controlled by their members
• Education and training - cooperatives provide education to members
• Cooperation among cooperatives - working together with other cooperatives
• Concern for community - sustainable development of communities

Cooperatives can be worker cooperatives, consumer cooperatives, housing cooperatives, and more.""",
                "metadata": {
                    "category": "cooperative_education",
                    "title": "Cooperative Basics",
                    "source": "cooperative_guide"
                }
            },
            {
                "id": "community_mission",
                "content": """BLKOUT Mission:

Building cooperative ownership together through authentic dialogue and community engagement. We are focused on Black queer liberation and creating economic alternatives that serve community needs over profit extraction.

Our approach emphasizes:
• Authentic conversation and relationship-building
• Complexity and nuance in understanding social issues
• Community-controlled economic development
• Black queer leadership and liberation
• Cooperative ownership models
• Dialogue over debate or conversion""",
                "metadata": {
                    "category": "mission",
                    "title": "BLKOUT Mission and Approach",
                    "source": "community_charter"
                }
            },
            {
                "id": "getting_involved",
                "content": """How to Get Involved with BLKOUT:

1. Attend Community Gatherings
   • Regular community meetings and social events
   • Workshops on cooperative development
   • Skill-sharing sessions

2. Join Working Groups
   • Cooperative development projects
   • Community organizing initiatives
   • Educational program development

3. Connect with Members
   • Reach out through community events
   • Participate in online discussions
   • Join collaborative projects

4. Start or Join a Cooperative
   • Learn about different cooperative models
   • Connect with others interested in starting cooperatives
   • Get support for existing cooperative initiatives

5. Share Your Skills and Experience
   • Offer workshops or educational sessions
   • Mentor others interested in cooperative development
   • Contribute to community resources and knowledge""",
                "metadata": {
                    "category": "engagement",
                    "title": "Getting Involved",
                    "source": "member_guide"
                }
            }
        ]
        
        try:
            # Add documents to collection
            for doc in initial_knowledge:
                await self.add_document(
                    doc_id=doc["id"],
                    content=doc["content"],
                    metadata=doc["metadata"]
                )
            
            logger.info(f"Loaded {len(initial_knowledge)} initial knowledge documents")
            
        except Exception as e:
            logger.error(f"Failed to load initial knowledge: {str(e)}")
    
    async def add_document(
        self, 
        doc_id: str, 
        content: str, 
        metadata: Dict[str, Any]
    ):
        """Add a document to the knowledge base"""
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            logger.debug(f"Added document: {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to add document {doc_id}: {str(e)}")
            raise
    
    async def search(
        self, 
        query: str, 
        limit: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = None
            if category_filter:
                where_clause = {"category": category_filter}
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and len(results["documents"][0]) > 0:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "relevance": 1 - results["distances"][0][i],  # Convert distance to relevance
                        "source": results["metadatas"][0][i].get("source", "unknown")
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {str(e)}")
            return []
    
    async def update_document(
        self, 
        doc_id: str, 
        content: str, 
        metadata: Dict[str, Any]
    ):
        """Update an existing document"""
        
        try:
            # Generate new embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Update in collection
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            logger.debug(f"Updated document: {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {str(e)}")
            raise
    
    async def delete_document(self, doc_id: str):
        """Delete a document from the knowledge base"""
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.debug(f"Deleted document: {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {str(e)}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        
        try:
            count = self.collection.count()
            
            # Get sample documents for category analysis
            sample_results = self.collection.get(
                limit=100,
                include=["metadatas"]
            )
            
            categories = {}
            if sample_results["metadatas"]:
                for metadata in sample_results["metadatas"]:
                    category = metadata.get("category", "uncategorized")
                    categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_documents": count,
                "categories": categories,
                "collection_name": settings.CHROMA_COLLECTION_NAME
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge base stats: {str(e)}")
            return {"error": str(e)}