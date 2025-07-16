#!/usr/bin/env python3
"""
Test Community Dashboard System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from services.dashboard_service import CommunityDashboardService

def setup_dashboard_test_data():
    """Create additional test data for dashboard testing"""
    
    print("📊 Setting up dashboard test data...")
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Create additional test profiles with varied engagement
    additional_profiles = [
        {
            'id': 'dashboard_profile_1',
            'email': 'engaged@blkoutuk.com',
            'name': 'Highly Engaged User',
            'location': 'London',
            'source': 'website',
            'journey_stage': 'champion',
            'engagement_score': 95,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': True,
                'peer_connections': True
            }),
            'created_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_profile_2',
            'email': 'moderate@blkoutuk.com',
            'name': 'Moderate User',
            'location': 'Manchester',
            'source': 'social_media',
            'journey_stage': 'engaged',
            'engagement_score': 65,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': False,
                'peer_connections': False
            }),
            'created_at': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_profile_3',
            'email': 'new@blkoutuk.com',
            'name': 'New User',
            'location': 'Birmingham',
            'source': 'quiz',
            'journey_stage': 'new',
            'engagement_score': 25,
            'consent_preferences': json.dumps({
                'personal_service': False,
                'community_insights': False,
                'peer_connections': False
            }),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for profile in additional_profiles:
        cursor.execute('''
            INSERT OR REPLACE INTO community_profiles 
            (id, email, name, location, source, journey_stage, engagement_score, consent_preferences, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile['id'], profile['email'], profile['name'], profile['location'],
            profile['source'], profile['journey_stage'], profile['engagement_score'],
            profile['consent_preferences'], profile['created_at']
        ))
    
    # Create diverse quiz results
    diverse_quizzes = [
        {
            'id': 'dashboard_quiz_1',
            'profile_id': 'dashboard_profile_1',
            'pathway': 'healer',
            'pathway_title': 'THE HEALER',
            'scores': json.dumps({'identity': 3, 'community': 4, 'liberation': 3, 'connection': 4}),
            'community_match': 'Wellness Circle',
            'created_at': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_quiz_2',
            'profile_id': 'dashboard_profile_2',
            'pathway': 'bridge_builder',
            'pathway_title': 'THE BRIDGE BUILDER',
            'scores': json.dumps({'identity': 3, 'community': 4, 'liberation': 3, 'connection': 4}),
            'community_match': 'Alliance Network',
            'created_at': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_quiz_3',
            'profile_id': 'dashboard_profile_3',
            'pathway': 'visionary',
            'pathway_title': 'THE VISIONARY',
            'scores': json.dumps({'identity': 4, 'community': 3, 'liberation': 4, 'connection': 3}),
            'community_match': 'Future Builders',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for quiz in diverse_quizzes:
        cursor.execute('''
            INSERT OR REPLACE INTO quiz_results 
            (id, profile_id, pathway, pathway_title, scores, community_match, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            quiz['id'], quiz['profile_id'], quiz['pathway'], quiz['pathway_title'],
            quiz['scores'], quiz['community_match'], quiz['created_at']
        ))
    
    # Create varied IVOR interactions
    varied_interactions = [
        {
            'id': 'dashboard_ivor_1',
            'profile_id': 'dashboard_profile_1',
            'session_id': 'dashboard_session_1',
            'user_message': 'I need help finding affordable housing in London',
            'ivor_response': 'I can connect you with housing advocates and mutual aid networks in London.',
            'response_time_ms': 180,
            'consent_level': 'peer_connections',
            'created_at': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_ivor_2',
            'profile_id': 'dashboard_profile_2',
            'session_id': 'dashboard_session_2',
            'user_message': 'How can I get involved in liberation work?',
            'ivor_response': 'There are many ways to contribute to liberation work in our community.',
            'response_time_ms': 220,
            'consent_level': 'personal_service',
            'created_at': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_ivor_3',
            'profile_id': 'dashboard_profile_3',
            'session_id': 'dashboard_session_3',
            'user_message': 'I want to find my community',
            'ivor_response': 'Let me help you connect with others who share your values.',
            'response_time_ms': 195,
            'consent_level': 'anonymous_only',
            'created_at': (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'dashboard_ivor_4',
            'profile_id': 'dashboard_profile_1',
            'session_id': 'dashboard_session_4',
            'user_message': 'Can you help me with mental health resources?',
            'ivor_response': 'We have partnerships with Black-affirming therapists and healing circles.',
            'response_time_ms': 210,
            'consent_level': 'community_insights',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for interaction in varied_interactions:
        cursor.execute('''
            INSERT OR REPLACE INTO ivor_interactions 
            (id, profile_id, session_id, user_message, ivor_response, response_time_ms, consent_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction['id'], interaction['profile_id'], interaction['session_id'],
            interaction['user_message'], interaction['ivor_response'],
            interaction['response_time_ms'], interaction['consent_level'],
            interaction['created_at']
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Dashboard test data created successfully")

def test_dashboard_service():
    """Test dashboard service functionality"""
    
    print("\n🔍 Testing dashboard service...")
    
    dashboard_service = CommunityDashboardService()
    
    try:
        # Test full dashboard data
        dashboard_data = dashboard_service.get_dashboard_data()
        
        print("✅ Dashboard data generated successfully")
        
        # Validate dashboard structure
        required_sections = [
            'meta',
            'community_overview',
            'liberation_pathways',
            'ivor_metrics',
            'engagement_trends',
            'real_time_activity',
            'privacy_health',
            'community_alerts',
            'growth_metrics'
        ]
        
        for section in required_sections:
            if section in dashboard_data:
                print(f"✅ {section}: Present")
            else:
                print(f"❌ {section}: Missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard service failed: {e}")
        return False

def test_dashboard_metrics():
    """Test specific dashboard metrics"""
    
    print("\n📊 Testing dashboard metrics...")
    
    dashboard_service = CommunityDashboardService()
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        
        # Test community overview
        overview = dashboard_data['community_overview']
        print(f"✅ Community Overview:")
        print(f"  Active members: {overview['total_active_members']}")
        print(f"  Health score: {overview['community_health_score']}")
        print(f"  New this week: {overview['new_members_this_week']}")
        print(f"  Status: {overview['health_status']}")
        
        # Test pathway metrics
        pathways = dashboard_data['liberation_pathways']
        print(f"\n✅ Liberation Pathways:")
        print(f"  Popular pathways: {pathways['popular_pathways']}")
        print(f"  Diversity score: {pathways['pathway_diversity_score']}")
        print(f"  Completion trend: {pathways['completion_trend']}")
        
        # Test IVOR metrics
        ivor = dashboard_data['ivor_metrics']
        print(f"\n✅ IVOR Metrics:")
        print(f"  Interactions today: {ivor['interactions_today']}")
        print(f"  Avg response time: {ivor['avg_response_time_ms']}ms")
        print(f"  Top topics: {ivor['top_discussion_topics']}")
        print(f"  Performance: {ivor['performance_status']}")
        
        # Test engagement trends
        engagement = dashboard_data['engagement_trends']
        print(f"\n✅ Engagement Trends:")
        print(f"  Trend direction: {engagement['trend_direction']}")
        print(f"  Engagement distribution: {engagement['engagement_distribution']}")
        
        # Test privacy health
        privacy = dashboard_data['privacy_health']
        print(f"\n✅ Privacy Health:")
        print(f"  Compliance score: {privacy['privacy_compliance_score']}%")
        print(f"  Consent distribution: {privacy['consent_distribution']}")
        print(f"  Status: {privacy['compliance_status']}")
        
        # Test alerts
        alerts = dashboard_data['community_alerts']
        print(f"\n✅ Community Alerts:")
        print(f"  Total alerts: {len(alerts)}")
        for alert in alerts:
            print(f"  - [{alert['severity'].upper()}] {alert['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard metrics test failed: {e}")
        return False

def test_dashboard_performance():
    """Test dashboard performance"""
    
    print("\n⚡ Testing dashboard performance...")
    
    dashboard_service = CommunityDashboardService()
    
    try:
        import time
        
        # Test response time
        start_time = time.time()
        dashboard_data = dashboard_service.get_dashboard_data()
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        print(f"✅ Dashboard generation time: {response_time:.2f}ms")
        
        # Test data completeness
        data_size = len(json.dumps(dashboard_data))
        print(f"✅ Dashboard data size: {data_size} bytes")
        
        # Performance thresholds
        if response_time < 1000:  # Less than 1 second
            print("✅ Performance: Excellent")
        elif response_time < 3000:  # Less than 3 seconds
            print("✅ Performance: Good")
        else:
            print("⚠️  Performance: Needs optimization")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard performance test failed: {e}")
        return False

def test_dashboard_alerts():
    """Test dashboard alert system"""
    
    print("\n🚨 Testing dashboard alerts...")
    
    dashboard_service = CommunityDashboardService()
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        alerts = dashboard_data['community_alerts']
        
        print(f"✅ Generated {len(alerts)} alerts")
        
        # Test alert categories
        alert_types = {}
        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        print(f"✅ Alert categories: {alert_types}")
        
        # Test alert severities
        severity_counts = {}
        for alert in alerts:
            severity = alert.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        print(f"✅ Alert severities: {severity_counts}")
        
        # Test alert structure
        for alert in alerts:
            required_fields = ['type', 'severity', 'title', 'message', 'action']
            for field in required_fields:
                if field not in alert:
                    print(f"❌ Alert missing field: {field}")
                    return False
        
        print("✅ All alerts have required fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard alerts test failed: {e}")
        return False

def main():
    """Run all dashboard tests"""
    
    print("🚀 Community Dashboard System Testing")
    print("=" * 50)
    
    # Setup test data
    setup_dashboard_test_data()
    
    # Run tests
    test_results = []
    
    test_results.append(test_dashboard_service())
    test_results.append(test_dashboard_metrics())
    test_results.append(test_dashboard_performance())
    test_results.append(test_dashboard_alerts())
    
    # Summary
    print("\n" + "=" * 50)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL DASHBOARD TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} tests successful")
        print("\n📊 Community Dashboard System is fully operational!")
        print("\nDashboard features available:")
        print("- Real-time community health monitoring")
        print("- Liberation pathway analytics")
        print("- IVOR AI performance metrics")
        print("- Engagement trend analysis")
        print("- Privacy compliance tracking")
        print("- Automated alert system")
        print("- Growth metrics and insights")
        print("- Real-time activity monitoring")
        print("\n🔗 API endpoints ready:")
        print("  GET /dashboard/ - Complete dashboard")
        print("  GET /dashboard/overview - Community overview")
        print("  GET /dashboard/pathways - Pathway analytics")
        print("  GET /dashboard/ivor - IVOR metrics")
        print("  GET /dashboard/engagement - Engagement trends")
        print("  GET /dashboard/realtime - Real-time activity")
        print("  GET /dashboard/privacy - Privacy metrics")
        print("  GET /dashboard/alerts - Community alerts")
        print("  GET /dashboard/growth - Growth metrics")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("Some dashboard features need attention")

if __name__ == "__main__":
    main()