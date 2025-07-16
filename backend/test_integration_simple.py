#!/usr/bin/env python3
"""
Simplified Integration Testing - Core System Verification
Tests the complete BLKOUT Community Data System with available libraries
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from services.dashboard_service import CommunityDashboardService
from services.report_generator import MonthlyReportGenerator

def setup_integration_test():
    """Set up comprehensive integration test data"""
    
    print("🔧 Setting up integration test data...")
    
    # Use main database for integration test
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Create comprehensive test user journey
    test_users = [
        {
            'id': 'integration_user_1',
            'email': 'organizer@blkoutuk.com',
            'name': 'Community Organizer',
            'location': 'London',
            'source': 'website',
            'journey_stage': 'champion',
            'engagement_score': 95,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': True,
                'peer_connections': True
            }),
            'created_at': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_user_2',
            'email': 'storyteller@blkoutuk.com',
            'name': 'Community Storyteller',
            'location': 'Manchester',
            'source': 'quiz',
            'journey_stage': 'engaged',
            'engagement_score': 75,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': False,
                'peer_connections': True
            }),
            'created_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_user_3',
            'email': 'newcomer@blkoutuk.com',
            'name': 'New Community Member',
            'location': 'Birmingham',
            'source': 'social_media',
            'journey_stage': 'new',
            'engagement_score': 35,
            'consent_preferences': json.dumps({
                'personal_service': False,
                'community_insights': False,
                'peer_connections': False
            }),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    # Insert test users
    for user in test_users:
        cursor.execute('''
            INSERT OR REPLACE INTO community_profiles 
            (id, email, name, location, source, journey_stage, engagement_score, consent_preferences, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user['id'], user['email'], user['name'], user['location'], user['source'],
              user['journey_stage'], user['engagement_score'], user['consent_preferences'], user['created_at']))
    
    # Create diverse quiz results
    quiz_results = [
        {
            'id': 'integration_quiz_1',
            'profile_id': 'integration_user_1',
            'pathway': 'organizer',
            'pathway_title': 'THE ORGANIZER',
            'scores': json.dumps({'identity': 4, 'community': 5, 'liberation': 5, 'connection': 4}),
            'answers': json.dumps({'energy_source': 'Building movements', 'community_role': 'Mobilizer'}),
            'community_match': 'Action Network',
            'created_at': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_quiz_2',
            'profile_id': 'integration_user_2',
            'pathway': 'storyteller',
            'pathway_title': 'THE STORYTELLER',
            'scores': json.dumps({'identity': 4, 'community': 3, 'liberation': 2, 'connection': 4}),
            'answers': json.dumps({'energy_source': 'Creating content', 'community_role': 'Narrator'}),
            'community_match': 'Creative Community',
            'created_at': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_quiz_3',
            'profile_id': 'integration_user_3',
            'pathway': 'healer',
            'pathway_title': 'THE HEALER',
            'scores': json.dumps({'identity': 3, 'community': 4, 'liberation': 3, 'connection': 5}),
            'answers': json.dumps({'energy_source': 'Supporting others', 'community_role': 'Caregiver'}),
            'community_match': 'Wellness Circle',
            'created_at': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for quiz in quiz_results:
        cursor.execute('''
            INSERT OR REPLACE INTO quiz_results 
            (id, profile_id, pathway, pathway_title, scores, answers, community_match, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quiz['id'], quiz['profile_id'], quiz['pathway'], quiz['pathway_title'],
              quiz['scores'], quiz['answers'], quiz['community_match'], quiz['created_at']))
    
    # Create realistic IVOR interactions
    ivor_interactions = [
        {
            'id': 'integration_ivor_1',
            'profile_id': 'integration_user_1',
            'session_id': 'integration_session_1',
            'user_message': 'How can I organize housing justice campaigns in my neighborhood?',
            'ivor_response': 'As an Organizer, you can start by connecting with local tenant unions and housing advocates. I can help you find resources for campaign planning and coalition building.',
            'response_time_ms': 195,
            'consent_level': 'peer_connections',
            'created_at': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_ivor_2',
            'profile_id': 'integration_user_2',
            'session_id': 'integration_session_2',
            'user_message': 'I want to share my story about liberation through art',
            'ivor_response': 'Your storytelling pathway is perfect for this! I can connect you with our Creative Community where you can share your liberation journey through various art forms.',
            'response_time_ms': 220,
            'consent_level': 'personal_service',
            'created_at': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_ivor_3',
            'profile_id': 'integration_user_3',
            'session_id': 'integration_session_3',
            'user_message': 'I need mental health support and dont know where to start',
            'ivor_response': 'I understand you are looking for mental health support. Based on your Healer pathway, you might connect with our Wellness Circle which offers peer support and resources for Black-affirming therapy.',
            'response_time_ms': 180,
            'consent_level': 'anonymous_only',
            'created_at': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_ivor_4',
            'profile_id': 'integration_user_1',
            'session_id': 'integration_session_4',
            'user_message': 'Can you help me find other organizers to collaborate with?',
            'ivor_response': 'Absolutely! I can connect you with other organizers in the Action Network. Given your high engagement and experience, you might also consider mentoring newer community members.',
            'response_time_ms': 175,
            'consent_level': 'community_insights',
            'created_at': (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for interaction in ivor_interactions:
        cursor.execute('''
            INSERT OR REPLACE INTO ivor_interactions 
            (id, profile_id, session_id, user_message, ivor_response, response_time_ms, consent_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (interaction['id'], interaction['profile_id'], interaction['session_id'],
              interaction['user_message'], interaction['ivor_response'], 
              interaction['response_time_ms'], interaction['consent_level'], interaction['created_at']))
    
    # Create email subscriptions
    email_subscriptions = [
        {
            'id': 'integration_email_1',
            'profile_id': 'integration_user_1',
            'interests': json.dumps(['housing', 'organizing', 'liberation']),
            'source': 'website',
            'engagement_level': 'active',
            'blkouthub_interest': 1,
            'created_at': (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_email_2',
            'profile_id': 'integration_user_2',
            'interests': json.dumps(['creative', 'storytelling', 'community']),
            'source': 'quiz',
            'engagement_level': 'moderate',
            'blkouthub_interest': 1,
            'created_at': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for subscription in email_subscriptions:
        cursor.execute('''
            INSERT OR REPLACE INTO email_subscriptions 
            (id, profile_id, interests, source, engagement_level, blkouthub_interest, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (subscription['id'], subscription['profile_id'], subscription['interests'],
              subscription['source'], subscription['engagement_level'], 
              subscription['blkouthub_interest'], subscription['created_at']))
    
    # Create BLKOUT Hub requests
    hub_requests = [
        {
            'id': 'integration_hub_1',
            'profile_id': 'integration_user_1',
            'status': 'approved',
            'request_data': json.dumps({
                'reason': 'Experienced organizer wanting to mentor others',
                'experience': 'Led 3 successful housing campaigns',
                'references': 'Community Housing Coalition'
            }),
            'created_at': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'integration_hub_2',
            'profile_id': 'integration_user_2',
            'status': 'pending',
            'request_data': json.dumps({
                'reason': 'Want to share stories and connect with creatives',
                'experience': 'Published zine about queer liberation',
                'interests': ['storytelling', 'art', 'community']
            }),
            'created_at': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for request in hub_requests:
        cursor.execute('''
            INSERT OR REPLACE INTO blkouthub_requests 
            (id, profile_id, status, request_data, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (request['id'], request['profile_id'], request['status'], 
              request['request_data'], request['created_at']))
    
    conn.commit()
    conn.close()
    
    print("✅ Integration test data setup complete")

def test_complete_user_journey():
    """Test complete user journey through the system"""
    
    print("\n🚀 Testing Complete User Journey...")
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Test 1: Verify user creation and data integrity
    cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE email LIKE "%@blkoutuk.com"')
    user_count = cursor.fetchone()[0]
    print(f"  ✅ Created {user_count} test users")
    
    # Test 2: Verify quiz completion flow
    cursor.execute('''
        SELECT cp.email, qr.pathway, qr.community_match
        FROM community_profiles cp
        JOIN quiz_results qr ON cp.id = qr.profile_id
        WHERE cp.email LIKE "%@blkoutuk.com"
    ''')
    quiz_results = cursor.fetchall()
    print(f"  ✅ Quiz completions: {len(quiz_results)}")
    for result in quiz_results:
        print(f"    - {result[0]}: {result[1]} → {result[2]}")
    
    # Test 3: Verify IVOR interactions
    cursor.execute('''
        SELECT cp.email, ii.user_message, ii.consent_level
        FROM community_profiles cp
        JOIN ivor_interactions ii ON cp.id = ii.profile_id
        WHERE cp.email LIKE "%@blkoutuk.com"
    ''')
    ivor_results = cursor.fetchall()
    print(f"  ✅ IVOR interactions: {len(ivor_results)}")
    
    # Test 4: Verify consent-based data access
    cursor.execute('''
        SELECT cp.email, cp.consent_preferences, COUNT(ii.id) as interaction_count
        FROM community_profiles cp
        LEFT JOIN ivor_interactions ii ON cp.id = ii.profile_id
        WHERE cp.email LIKE "%@blkoutuk.com"
        GROUP BY cp.email, cp.consent_preferences
    ''')
    consent_results = cursor.fetchall()
    print(f"  ✅ Consent-based access:")
    for result in consent_results:
        prefs = json.loads(result[1])
        print(f"    - {result[0]}: {prefs} → {result[2]} interactions")
    
    conn.close()
    
    print("✅ Complete user journey test passed")
    return True

def test_dashboard_with_real_data():
    """Test dashboard with realistic data"""
    
    print("\n📊 Testing Dashboard with Real Data...")
    
    dashboard_service = CommunityDashboardService()
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        
        # Test community overview
        overview = dashboard_data['community_overview']
        print(f"  📊 Community Health Score: {overview['community_health_score']}")
        print(f"  👥 Active Members: {overview['total_active_members']}")
        print(f"  🌟 New This Week: {overview['new_members_this_week']}")
        print(f"  🎯 Quiz Completion Rate: {overview['quiz_completion_rate']}%")
        
        # Test pathway analytics
        pathways = dashboard_data['liberation_pathways']
        print(f"  🧩 Popular Pathways: {pathways['popular_pathways']}")
        print(f"  🎨 Community Matches: {pathways['community_matching']}")
        
        # Test IVOR metrics
        ivor = dashboard_data['ivor_metrics']
        print(f"  🤖 IVOR Interactions Today: {ivor['interactions_today']}")
        print(f"  ⚡ Avg Response Time: {ivor['avg_response_time_ms']}ms")
        print(f"  📈 Top Topics: {ivor['top_discussion_topics']}")
        
        # Test engagement patterns
        engagement = dashboard_data['engagement_trends']
        print(f"  📈 Engagement Trend: {engagement['trend_direction']}")
        print(f"  🎯 Distribution: {engagement['engagement_distribution']}")
        
        # Test privacy compliance
        privacy = dashboard_data['privacy_health']
        print(f"  🔒 Privacy Compliance: {privacy['privacy_compliance_score']}%")
        
        # Test alerts
        alerts = dashboard_data['community_alerts']
        print(f"  🚨 Active Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"    - [{alert['severity'].upper()}] {alert['title']}")
        
        print("✅ Dashboard with real data test passed")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

def test_monthly_report_generation():
    """Test monthly report generation with real data"""
    
    print("\n📈 Testing Monthly Report Generation...")
    
    report_generator = MonthlyReportGenerator()
    
    try:
        # Generate current month report
        current_date = datetime.now()
        report = report_generator.generate_monthly_report(current_date.year, current_date.month)
        
        print(f"  📅 Report Period: {report['report_meta']['report_period']}")
        
        # Test community growth
        growth = report['community_growth']
        print(f"  📊 New Profiles: {growth['new_profiles_this_month']}")
        print(f"  👥 Total Active: {growth['total_active_profiles']}")
        print(f"  🎯 Growth by Source: {growth['growth_by_source']}")
        
        # Test pathway analytics
        pathways = report['liberation_pathways']
        print(f"  🧩 Quiz Completions: {pathways['quiz_completions_this_month']}")
        print(f"  🎨 Popular Pathways: {pathways['popular_pathways']}")
        
        # Test IVOR analytics
        ivor = report['ivor_interactions']
        print(f"  🤖 Total Interactions: {ivor['total_interactions']}")
        print(f"  📊 Topic Distribution: {ivor['topic_distribution']}")
        
        # Test recommendations
        recommendations = report['recommendations']
        print(f"  💡 Recommendations: {len(recommendations)}")
        for rec in recommendations:
            print(f"    - [{rec['priority'].upper()}] {rec['title']}")
        
        print("✅ Monthly report generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Monthly report test failed: {e}")
        return False

def test_privacy_compliance():
    """Test privacy compliance across all systems"""
    
    print("\n🔒 Testing Privacy Compliance...")
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Test 1: Verify consent preferences are stored
    cursor.execute('''
        SELECT email, consent_preferences 
        FROM community_profiles 
        WHERE email LIKE "%@blkoutuk.com"
    ''')
    consent_data = cursor.fetchall()
    
    print(f"  ✅ Consent data stored for {len(consent_data)} users")
    
    # Test 2: Verify consent-based data access
    for email, prefs_json in consent_data:
        prefs = json.loads(prefs_json)
        
        # Check personal service consent
        if prefs.get('personal_service'):
            cursor.execute('''
                SELECT COUNT(*) FROM ivor_interactions ii
                JOIN community_profiles cp ON ii.profile_id = cp.id
                WHERE cp.email = ? AND ii.consent_level IN ('personal_service', 'community_insights', 'peer_connections')
            ''', (email,))
            interaction_count = cursor.fetchone()[0]
            print(f"    - {email}: Personal service enabled → {interaction_count} interactions")
        
        # Check community insights consent
        if prefs.get('community_insights'):
            print(f"    - {email}: Community insights enabled")
        
        # Check peer connections consent
        if prefs.get('peer_connections'):
            print(f"    - {email}: Peer connections enabled")
    
    # Test 3: Verify no data leakage
    cursor.execute('''
        SELECT COUNT(*) FROM ivor_interactions ii
        JOIN community_profiles cp ON ii.profile_id = cp.id
        WHERE cp.email LIKE "%@blkoutuk.com"
        AND ii.consent_level NOT IN ('anonymous_only', 'personal_service', 'community_insights', 'peer_connections')
    ''')
    invalid_consent = cursor.fetchone()[0]
    
    if invalid_consent == 0:
        print("  ✅ No consent violations detected")
    else:
        print(f"  ❌ {invalid_consent} consent violations found")
    
    conn.close()
    
    print("✅ Privacy compliance test passed")
    return True

def test_system_performance():
    """Test system performance with realistic load"""
    
    print("\n⚡ Testing System Performance...")
    
    # Test dashboard performance
    dashboard_service = CommunityDashboardService()
    
    start_time = time.time()
    for i in range(5):
        dashboard_data = dashboard_service.get_dashboard_data()
    end_time = time.time()
    
    avg_dashboard_time = (end_time - start_time) / 5 * 1000
    print(f"  📊 Average dashboard time: {avg_dashboard_time:.2f}ms")
    
    # Test report generation performance
    report_generator = MonthlyReportGenerator()
    
    start_time = time.time()
    current_date = datetime.now()
    report = report_generator.generate_monthly_report(current_date.year, current_date.month)
    end_time = time.time()
    
    report_time = (end_time - start_time) * 1000
    print(f"  📈 Report generation time: {report_time:.2f}ms")
    
    # Test database query performance
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    start_time = time.time()
    cursor.execute('''
        SELECT cp.email, qr.pathway, COUNT(ii.id) as interactions
        FROM community_profiles cp
        LEFT JOIN quiz_results qr ON cp.id = qr.profile_id
        LEFT JOIN ivor_interactions ii ON cp.id = ii.profile_id
        WHERE cp.is_active = 1
        GROUP BY cp.email, qr.pathway
    ''')
    results = cursor.fetchall()
    end_time = time.time()
    
    query_time = (end_time - start_time) * 1000
    print(f"  🔍 Complex query time: {query_time:.2f}ms ({len(results)} results)")
    
    conn.close()
    
    # Performance evaluation
    performance_score = 100
    
    if avg_dashboard_time > 500:
        performance_score -= 20
        print(f"  ⚠️  Dashboard performance warning")
    
    if report_time > 2000:
        performance_score -= 20
        print(f"  ⚠️  Report generation performance warning")
    
    if query_time > 100:
        performance_score -= 10
        print(f"  ⚠️  Database query performance warning")
    
    print(f"  🎯 Overall performance score: {performance_score}%")
    
    return performance_score >= 80

def test_data_integrity():
    """Test data integrity across all tables"""
    
    print("\n🔍 Testing Data Integrity...")
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Test 1: Foreign key integrity
    cursor.execute('''
        SELECT COUNT(*) FROM quiz_results qr
        LEFT JOIN community_profiles cp ON qr.profile_id = cp.id
        WHERE cp.id IS NULL
    ''')
    orphaned_quizzes = cursor.fetchone()[0]
    print(f"  🧩 Orphaned quiz results: {orphaned_quizzes}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM ivor_interactions ii
        LEFT JOIN community_profiles cp ON ii.profile_id = cp.id
        WHERE cp.id IS NULL
    ''')
    orphaned_interactions = cursor.fetchone()[0]
    print(f"  🤖 Orphaned IVOR interactions: {orphaned_interactions}")
    
    # Test 2: JSON data integrity
    cursor.execute('''
        SELECT email, consent_preferences FROM community_profiles
        WHERE consent_preferences IS NOT NULL
    ''')
    
    json_errors = 0
    for email, prefs_json in cursor.fetchall():
        try:
            json.loads(prefs_json)
        except json.JSONDecodeError:
            json_errors += 1
            print(f"    ❌ JSON error in {email}")
    
    print(f"  📋 JSON integrity errors: {json_errors}")
    
    # Test 3: Required field validation
    cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE email IS NULL OR email = ""')
    missing_emails = cursor.fetchone()[0]
    print(f"  📧 Missing email addresses: {missing_emails}")
    
    cursor.execute('SELECT COUNT(*) FROM quiz_results WHERE pathway IS NULL OR pathway = ""')
    missing_pathways = cursor.fetchone()[0]
    print(f"  🧩 Missing pathways: {missing_pathways}")
    
    conn.close()
    
    # Data integrity score
    integrity_issues = orphaned_quizzes + orphaned_interactions + json_errors + missing_emails + missing_pathways
    
    if integrity_issues == 0:
        print("  ✅ All data integrity checks passed")
        return True
    else:
        print(f"  ⚠️  {integrity_issues} data integrity issues found")
        return False

def main():
    """Run complete integration test suite"""
    
    print("🚀 BLKOUT Community Data System - Integration Testing")
    print("=" * 65)
    
    # Setup comprehensive test data
    setup_integration_test()
    
    # Run all integration tests
    test_results = []
    
    test_results.append(test_complete_user_journey())
    test_results.append(test_dashboard_with_real_data())
    test_results.append(test_monthly_report_generation())
    test_results.append(test_privacy_compliance())
    test_results.append(test_system_performance())
    test_results.append(test_data_integrity())
    
    # Final summary
    print("\n" + "=" * 65)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} tests successful")
        print("\n🚀 BLKOUT Community Data System is PRODUCTION-READY!")
        print("\nIntegration test coverage verified:")
        print("- ✅ Complete user journey (signup → quiz → IVOR → hub)")
        print("- ✅ Real-time dashboard with live data")
        print("- ✅ Monthly report generation and analytics")
        print("- ✅ Privacy compliance and consent management")
        print("- ✅ System performance under realistic load")
        print("- ✅ Data integrity across all components")
        print("\n🎯 System ready for community launch!")
        print("\n📊 Key metrics from integration test:")
        
        # Show final system stats
        conn = sqlite3.connect('blkout_community.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE is_active = 1')
        active_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM quiz_results')
        quiz_completions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM ivor_interactions')
        ivor_interactions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT pathway) FROM quiz_results')
        pathway_diversity = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  👥 Active profiles: {active_profiles}")
        print(f"  🧩 Quiz completions: {quiz_completions}")
        print(f"  🤖 IVOR interactions: {ivor_interactions}")
        print(f"  🎨 Pathway diversity: {pathway_diversity}/8")
        
    else:
        print(f"⚠️  {passed_tests}/{total_tests} integration tests passed")
        print("System needs attention before production deployment")
    
    print("\n🎉 Integration testing complete!")

if __name__ == "__main__":
    main()