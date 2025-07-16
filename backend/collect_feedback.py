#!/usr/bin/env python3
"""
Community Feedback Collection Tool
"""

import sqlite3
import json
import uuid
from datetime import datetime

def collect_feedback():
    """Interactive feedback collection"""
    
    print("🌟 BLKOUT Community Feedback Collection")
    print("=" * 50)
    
    # Get user identification
    email = input("Your email (optional, for follow-up): ").strip()
    
    # Get feedback type
    print("\nFeedback Categories:")
    print("1. User Experience")
    print("2. IVOR AI Assistant")
    print("3. Liberation Quiz")
    print("4. Privacy & Consent")
    print("5. Community Dashboard")
    print("6. General Suggestions")
    
    feedback_types = {
        '1': 'user_experience',
        '2': 'ivor_ai',
        '3': 'liberation_quiz',
        '4': 'privacy_consent',
        '5': 'community_dashboard',
        '6': 'general_suggestions'
    }
    
    choice = input("\nSelect category (1-6): ").strip()
    feedback_type = feedback_types.get(choice, 'general_suggestions')
    
    # Get rating
    rating = None
    try:
        rating = int(input("\nRating (1-5, 5 being excellent): ").strip())
        if rating < 1 or rating > 5:
            rating = None
    except ValueError:
        pass
    
    # Get detailed feedback
    print("\nDetailed Feedback:")
    feedback_text = input("What worked well? What could be improved? ").strip()
    
    # Get suggestions
    suggestions = input("\nSpecific suggestions for improvement: ").strip()
    
    # Save feedback
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Get profile ID if email provided
    profile_id = None
    if email:
        cursor.execute('SELECT id FROM community_profiles WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            profile_id = result[0]
    
    feedback_id = str(uuid.uuid4())
    
    cursor.execute("""
        INSERT INTO community_feedback 
        (id, profile_id, feedback_type, rating, feedback_text, suggestions)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (feedback_id, profile_id, feedback_type, rating, feedback_text, suggestions))
    
    conn.commit()
    conn.close()
    
    print("\n✅ Thank you for your feedback!")
    print("Your input helps make BLKOUT better for our community.")

if __name__ == "__main__":
    collect_feedback()
