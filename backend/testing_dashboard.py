#!/usr/bin/env python3
"""
Community Testing Dashboard
Real-time monitoring during community testing phase
"""

import sqlite3
import json
from datetime import datetime, timedelta
from services.dashboard_service import CommunityDashboardService

def get_testing_metrics():
    """Get testing-specific metrics"""
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Test participation metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_testers,
            COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as new_testers_week,
            COUNT(CASE WHEN created_at >= date('now', '-1 day') THEN 1 END) as new_testers_today
        FROM community_profiles
    """)
    participation = cursor.fetchone()
    
    # Feedback metrics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_feedback,
            AVG(rating) as avg_rating,
            COUNT(CASE WHEN created_at >= date('now', '-1 day') THEN 1 END) as feedback_today
        FROM community_feedback
        WHERE rating IS NOT NULL
    """)
    feedback = cursor.fetchone()
    
    # Feature usage metrics
    cursor.execute('SELECT COUNT(*) FROM quiz_results')
    quiz_completions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM ivor_interactions')
    ivor_interactions = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM blkouthub_requests')
    hub_requests = cursor.fetchone()[0]
    
    # Error tracking
    cursor.execute("""
        SELECT 
            feedback_type,
            COUNT(*) as count
        FROM community_feedback
        WHERE feedback_text LIKE '%error%' OR feedback_text LIKE '%bug%' OR feedback_text LIKE '%problem%'
        GROUP BY feedback_type
    """)
    error_reports = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'participation': {
            'total_testers': participation[0],
            'new_testers_week': participation[1],
            'new_testers_today': participation[2]
        },
        'feedback': {
            'total_feedback': feedback[0],
            'avg_rating': round(feedback[1], 2) if feedback[1] else 0,
            'feedback_today': feedback[2]
        },
        'feature_usage': {
            'quiz_completions': quiz_completions,
            'ivor_interactions': ivor_interactions,
            'hub_requests': hub_requests
        },
        'error_reports': error_reports
    }

def display_testing_dashboard():
    """Display testing dashboard"""
    
    print("🧪 BLKOUT Community Testing Dashboard")
    print("=" * 50)
    
    # Get system metrics
    dashboard_service = CommunityDashboardService()
    system_data = dashboard_service.get_dashboard_data()
    
    # Get testing metrics
    testing_data = get_testing_metrics()
    
    # Display overview
    print(f"📊 System Health: {system_data['community_overview']['community_health_score']}")
    print(f"👥 Total Testers: {testing_data['participation']['total_testers']}")
    print(f"🆕 New This Week: {testing_data['participation']['new_testers_week']}")
    print(f"📅 New Today: {testing_data['participation']['new_testers_today']}")
    
    # Display feedback summary
    print("\n💬 Feedback Summary:")
    print(f"  Total Feedback: {testing_data['feedback']['total_feedback']}")
    print(f"  Average Rating: {testing_data['feedback']['avg_rating']}/5")
    print(f"  Feedback Today: {testing_data['feedback']['feedback_today']}")
    
    # Display feature usage
    print("\n🎯 Feature Usage:")
    print(f"  Quiz Completions: {testing_data['feature_usage']['quiz_completions']}")
    print(f"  IVOR Interactions: {testing_data['feature_usage']['ivor_interactions']}")
    print(f"  Hub Requests: {testing_data['feature_usage']['hub_requests']}")
    
    # Display error reports
    if testing_data['error_reports']:
        print("\n🚨 Error Reports:")
        for feature, count in testing_data['error_reports'].items():
            print(f"  {feature}: {count} issues")
    else:
        print("\n✅ No error reports")
    
    # Display top IVOR topics
    ivor_topics = system_data['ivor_metrics']['top_discussion_topics']
    print(f"\n🤖 Top IVOR Topics: {ivor_topics}")
    
    # Display privacy compliance
    privacy_score = system_data['privacy_health']['privacy_compliance_score']
    print(f"\n🔒 Privacy Compliance: {privacy_score}%")
    
    print("\n⚡ Real-time Updates:")
    print(f"  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Next Update: {(datetime.now() + timedelta(minutes=5)).strftime('%H:%M:%S')}")

if __name__ == "__main__":
    display_testing_dashboard()
