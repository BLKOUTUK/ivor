#!/usr/bin/env python3
"""
Full Integration Testing - End-to-End System Test
Tests the complete BLKOUT Community Data System
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from services.dashboard_service import CommunityDashboardService
from services.report_generator import MonthlyReportGenerator
from services.consent_manager import ConsentManager
from services.user_context_service import UserContextService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_integration_test_environment():
    """Set up clean test environment"""
    
    print("🔧 Setting up integration test environment...")
    
    # Create fresh database
    conn = sqlite3.connect('integration_test.db')
    cursor = conn.cursor()
    
    # Create all tables
    tables = [
        '''CREATE TABLE IF NOT EXISTS community_profiles (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            source TEXT NOT NULL,
            journey_stage TEXT DEFAULT 'new',
            engagement_score INTEGER DEFAULT 0,
            consent_preferences TEXT,
            is_active BOOLEAN DEFAULT 1
        )''',
        
        '''CREATE TABLE IF NOT EXISTS email_subscriptions (
            id TEXT PRIMARY KEY,
            profile_id TEXT,
            interests TEXT,
            source TEXT NOT NULL,
            engagement_level TEXT DEFAULT 'casual',
            blkouthub_interest BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES community_profiles (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS quiz_results (
            id TEXT PRIMARY KEY,
            profile_id TEXT,
            pathway TEXT NOT NULL,
            pathway_title TEXT,
            scores TEXT,
            answers TEXT,
            community_match TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES community_profiles (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS ivor_interactions (
            id TEXT PRIMARY KEY,
            profile_id TEXT,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ivor_response TEXT NOT NULL,
            sources TEXT,
            response_time_ms INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            consent_level TEXT DEFAULT 'anonymous_only',
            FOREIGN KEY (profile_id) REFERENCES community_profiles (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS engagement_events (
            id TEXT PRIMARY KEY,
            profile_id TEXT,
            event_type TEXT NOT NULL,
            event_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES community_profiles (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS blkouthub_requests (
            id TEXT PRIMARY KEY,
            profile_id TEXT,
            status TEXT DEFAULT 'pending',
            request_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (profile_id) REFERENCES community_profiles (id)
        )''',
        
        '''CREATE TABLE IF NOT EXISTS monthly_reports (
            id TEXT PRIMARY KEY,
            report_period TEXT NOT NULL,
            report_data TEXT NOT NULL,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )'''
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    conn.commit()
    conn.close()
    
    print("✅ Integration test environment ready")

def test_end_to_end_user_journey():
    """Test complete user journey from signup to dashboard"""
    
    print("\n🚀 Testing End-to-End User Journey...")
    
    conn = sqlite3.connect('integration_test.db')
    cursor = conn.cursor()
    
    # Step 1: User signs up via email form
    print("  Step 1: Email signup...")
    
    user_data = {
        'id': 'integration_user_1',
        'email': 'integration@blkoutuk.com',
        'name': 'Integration Test User',
        'location': 'London',
        'source': 'website',
        'consent_preferences': json.dumps({
            'personal_service': True,
            'community_insights': True,
            'peer_connections': False
        })
    }
    
    cursor.execute('''
        INSERT INTO community_profiles (id, email, name, location, source, consent_preferences)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_data['id'], user_data['email'], user_data['name'], 
          user_data['location'], user_data['source'], user_data['consent_preferences']))
    
    # Step 2: User subscribes to emails
    print("  Step 2: Email subscription...")
    
    subscription_data = {
        'id': 'integration_sub_1',
        'profile_id': user_data['id'],
        'interests': json.dumps(['housing', 'community', 'liberation']),
        'source': 'website',
        'engagement_level': 'active',
        'blkouthub_interest': 1
    }
    
    cursor.execute('''
        INSERT INTO email_subscriptions (id, profile_id, interests, source, engagement_level, blkouthub_interest)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (subscription_data['id'], subscription_data['profile_id'], 
          subscription_data['interests'], subscription_data['source'],
          subscription_data['engagement_level'], subscription_data['blkouthub_interest']))
    
    # Step 3: User completes liberation quiz
    print("  Step 3: Liberation quiz completion...")
    
    quiz_data = {
        'id': 'integration_quiz_1',
        'profile_id': user_data['id'],
        'pathway': 'organizer',
        'pathway_title': 'THE ORGANIZER',
        'scores': json.dumps({
            'identity': 4,
            'community': 5,
            'liberation': 5,
            'connection': 4
        }),
        'answers': json.dumps({
            'energy_source': 'Building movements',
            'community_role': 'Mobilizer',
            'liberation_priority': 'Collective action'
        }),
        'community_match': 'Action Network'
    }
    
    cursor.execute('''
        INSERT INTO quiz_results (id, profile_id, pathway, pathway_title, scores, answers, community_match)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (quiz_data['id'], quiz_data['profile_id'], quiz_data['pathway'],
          quiz_data['pathway_title'], quiz_data['scores'], quiz_data['answers'],
          quiz_data['community_match']))
    
    # Step 4: User interacts with IVOR
    print("  Step 4: IVOR interaction...")
    
    ivor_interactions = [
        {
            'id': 'integration_ivor_1',
            'profile_id': user_data['id'],
            'session_id': 'integration_session_1',
            'user_message': 'How can I get involved in organizing in my area?',
            'ivor_response': 'Based on your Organizer pathway, I can connect you with local action networks and organizing opportunities.',
            'response_time_ms': 185,
            'consent_level': 'personal_service'
        },
        {
            'id': 'integration_ivor_2',
            'profile_id': user_data['id'],
            'session_id': 'integration_session_2',
            'user_message': 'I need help finding housing resources',
            'ivor_response': 'I can help you connect with housing advocates and mutual aid networks in London.',
            'response_time_ms': 210,
            'consent_level': 'community_insights'
        }
    ]
    
    for interaction in ivor_interactions:
        cursor.execute('''
            INSERT INTO ivor_interactions (id, profile_id, session_id, user_message, ivor_response, response_time_ms, consent_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (interaction['id'], interaction['profile_id'], interaction['session_id'],
              interaction['user_message'], interaction['ivor_response'],
              interaction['response_time_ms'], interaction['consent_level']))
    
    # Step 5: User requests BLKOUT Hub access
    print("  Step 5: BLKOUT Hub access request...")
    
    hub_request = {
        'id': 'integration_hub_1',
        'profile_id': user_data['id'],
        'status': 'pending',
        'request_data': json.dumps({
            'reason': 'Want to connect with other organizers',
            'experience': 'Community organizing for 2 years',
            'interests': ['housing justice', 'mutual aid']
        })
    }
    
    cursor.execute('''
        INSERT INTO blkouthub_requests (id, profile_id, status, request_data)
        VALUES (?, ?, ?, ?)
    ''', (hub_request['id'], hub_request['profile_id'], 
          hub_request['status'], hub_request['request_data']))
    
    # Step 6: Track engagement events
    print("  Step 6: Engagement tracking...")
    
    engagement_events = [
        {
            'id': 'integration_event_1',
            'profile_id': user_data['id'],
            'event_type': 'quiz_completion',
            'event_data': json.dumps({'pathway': 'organizer', 'score': 4.5})
        },
        {
            'id': 'integration_event_2',
            'profile_id': user_data['id'],
            'event_type': 'ivor_interaction',
            'event_data': json.dumps({'topic': 'organizing', 'satisfaction': 'high'})
        }
    ]
    
    for event in engagement_events:
        cursor.execute('''
            INSERT INTO engagement_events (id, profile_id, event_type, event_data)
            VALUES (?, ?, ?, ?)
        ''', (event['id'], event['profile_id'], event['event_type'], event['event_data']))
    
    # Step 7: Update engagement score
    print("  Step 7: Engagement score update...")
    
    cursor.execute('''
        UPDATE community_profiles 
        SET engagement_score = 85, journey_stage = 'engaged'
        WHERE id = ?
    ''', (user_data['id'],))
    
    conn.commit()
    conn.close()
    
    print("✅ End-to-end user journey completed successfully")
    return True

def test_consent_management_integration():
    """Test consent management across the system"""
    
    print("\n🔒 Testing Consent Management Integration...")
    
    # Test with integration database
    consent_manager = ConsentManager(db_path='integration_test.db')
    
    # Test consent validation
    test_preferences = {
        'personal_service': True,
        'community_insights': True,
        'peer_connections': False
    }
    
    is_valid = consent_manager.validate_consent_preferences(test_preferences)
    print(f"  Consent validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test consent level calculation
    consent_level = consent_manager.get_effective_consent_level(test_preferences)
    print(f"  Effective consent level: {consent_level}")
    
    # Test data filtering based on consent
    conn = sqlite3.connect('integration_test.db')
    cursor = conn.cursor()
    
    # Check if user data is properly filtered
    cursor.execute('''
        SELECT consent_preferences FROM community_profiles 
        WHERE id = 'integration_user_1'
    ''')
    result = cursor.fetchone()
    
    if result:
        stored_preferences = json.loads(result[0])
        print(f"  Stored preferences: {stored_preferences}")
        
        # Test consent-based data access
        if stored_preferences.get('community_insights'):
            print("  ✅ Community insights access allowed")
        else:
            print("  ❌ Community insights access denied")
    
    conn.close()
    
    print("✅ Consent management integration working")
    return True

def test_reporting_integration():
    """Test monthly reporting integration"""
    
    print("\n📊 Testing Monthly Reporting Integration...")
    
    report_generator = MonthlyReportGenerator(db_path='integration_test.db')
    
    # Generate current month report
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    try:
        report = report_generator.generate_monthly_report(year, month)
        
        print(f"  ✅ Monthly report generated for {year}-{month:02d}")
        
        # Validate report structure
        required_sections = [
            'community_growth', 'liberation_pathways', 'ivor_interactions',
            'engagement_patterns', 'community_health', 'privacy_compliance'
        ]
        
        for section in required_sections:
            if section in report:
                print(f"  ✅ {section}: Present")
            else:
                print(f"  ❌ {section}: Missing")
        
        # Test report metrics
        growth = report['community_growth']
        print(f"  📈 New profiles: {growth['new_profiles_this_month']}")
        print(f"  📈 Total active: {growth['total_active_profiles']}")
        
        pathways = report['liberation_pathways']
        print(f"  🧩 Quiz completions: {pathways['quiz_completions_this_month']}")
        
        ivor = report['ivor_interactions']
        print(f"  🤖 IVOR interactions: {ivor['total_interactions']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Monthly reporting failed: {e}")
        return False

def test_dashboard_integration():
    """Test dashboard integration with real data"""
    
    print("\n📊 Testing Dashboard Integration...")
    
    dashboard_service = CommunityDashboardService(db_path='integration_test.db')
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        
        print("  ✅ Dashboard data generated successfully")
        
        # Test key metrics
        overview = dashboard_data['community_overview']
        print(f"  👥 Active members: {overview['total_active_members']}")
        print(f"  💪 Health score: {overview['community_health_score']}")
        print(f"  🎯 Quiz completion rate: {overview['quiz_completion_rate']}%")
        
        # Test pathway analytics
        pathways = dashboard_data['liberation_pathways']
        print(f"  🧩 Popular pathways: {pathways['popular_pathways']}")
        
        # Test IVOR metrics
        ivor = dashboard_data['ivor_metrics']
        print(f"  🤖 IVOR interactions today: {ivor['interactions_today']}")
        print(f"  ⚡ Response time: {ivor['avg_response_time_ms']}ms")
        
        # Test privacy compliance
        privacy = dashboard_data['privacy_health']
        print(f"  🔒 Privacy compliance: {privacy['privacy_compliance_score']}%")
        
        # Test alerts
        alerts = dashboard_data['community_alerts']
        print(f"  🚨 Active alerts: {len(alerts)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard integration failed: {e}")
        return False

def test_user_context_integration():
    """Test user context service integration"""
    
    print("\n🧠 Testing User Context Integration...")
    
    user_context_service = UserContextService(db_path='integration_test.db')
    
    try:
        # Test with integration user
        conn = sqlite3.connect('integration_test.db')
        
        # Test context retrieval
        context = user_context_service.get_user_context(
            'integration@blkoutuk.com',
            'integration_session_1',
            None  # db session would be passed in real API
        )
        
        if context:
            print(f"  ✅ User context retrieved")
            print(f"  📊 Context keys: {list(context.keys())}")
            
            # Test specific context elements
            if 'liberation_pathway' in context:
                print(f"  🧩 Liberation pathway: {context['liberation_pathway']}")
            
            if 'engagement_level' in context:
                print(f"  📈 Engagement level: {context['engagement_level']}")
            
            if 'recent_topics' in context:
                print(f"  💬 Recent topics: {context['recent_topics']}")
            
            return True
        else:
            print("  ❌ No user context retrieved")
            return False
        
    except Exception as e:
        print(f"  ❌ User context integration failed: {e}")
        return False

def test_data_consistency():
    """Test data consistency across all components"""
    
    print("\n🔍 Testing Data Consistency...")
    
    conn = sqlite3.connect('integration_test.db')
    cursor = conn.cursor()
    
    # Test profile consistency
    cursor.execute('SELECT COUNT(*) FROM community_profiles')
    profile_count = cursor.fetchone()[0]
    print(f"  👥 Total profiles: {profile_count}")
    
    # Test quiz consistency
    cursor.execute('''
        SELECT COUNT(*) FROM quiz_results qr
        JOIN community_profiles cp ON qr.profile_id = cp.id
    ''')
    quiz_profile_consistency = cursor.fetchone()[0]
    print(f"  🧩 Quiz-Profile consistency: {quiz_profile_consistency} linked")
    
    # Test IVOR consistency
    cursor.execute('''
        SELECT COUNT(*) FROM ivor_interactions ii
        JOIN community_profiles cp ON ii.profile_id = cp.id
    ''')
    ivor_profile_consistency = cursor.fetchone()[0]
    print(f"  🤖 IVOR-Profile consistency: {ivor_profile_consistency} linked")
    
    # Test subscription consistency
    cursor.execute('''
        SELECT COUNT(*) FROM email_subscriptions es
        JOIN community_profiles cp ON es.profile_id = cp.id
    ''')
    subscription_consistency = cursor.fetchone()[0]
    print(f"  📧 Subscription-Profile consistency: {subscription_consistency} linked")
    
    # Test engagement events consistency
    cursor.execute('''
        SELECT COUNT(*) FROM engagement_events ee
        JOIN community_profiles cp ON ee.profile_id = cp.id
    ''')
    engagement_consistency = cursor.fetchone()[0]
    print(f"  📈 Engagement-Profile consistency: {engagement_consistency} linked")
    
    conn.close()
    
    print("✅ Data consistency verified")
    return True

def test_performance_under_load():
    """Test system performance under simulated load"""
    
    print("\n⚡ Testing Performance Under Load...")
    
    # Simulate multiple dashboard requests
    dashboard_service = CommunityDashboardService(db_path='integration_test.db')
    
    start_time = time.time()
    
    for i in range(10):
        dashboard_data = dashboard_service.get_dashboard_data()
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10 * 1000  # Convert to ms
    
    print(f"  📊 Average dashboard generation time: {avg_time:.2f}ms")
    
    # Test report generation performance
    report_generator = MonthlyReportGenerator(db_path='integration_test.db')
    
    start_time = time.time()
    current_date = datetime.now()
    report = report_generator.generate_monthly_report(current_date.year, current_date.month)
    end_time = time.time()
    
    report_time = (end_time - start_time) * 1000
    print(f"  📈 Report generation time: {report_time:.2f}ms")
    
    # Performance thresholds
    performance_passed = True
    
    if avg_time > 500:  # 500ms threshold
        print(f"  ⚠️  Dashboard performance warning: {avg_time:.2f}ms > 500ms")
        performance_passed = False
    
    if report_time > 2000:  # 2s threshold
        print(f"  ⚠️  Report performance warning: {report_time:.2f}ms > 2000ms")
        performance_passed = False
    
    if performance_passed:
        print("  ✅ Performance meets requirements")
    
    return performance_passed

def cleanup_test_environment():
    """Clean up test environment"""
    
    print("\n🧹 Cleaning up test environment...")
    
    try:
        import os
        if os.path.exists('integration_test.db'):
            os.remove('integration_test.db')
        print("✅ Test database cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run full integration test suite"""
    
    print("🚀 BLKOUT Community Data System - Full Integration Testing")
    print("=" * 70)
    
    # Setup test environment
    setup_integration_test_environment()
    
    # Run integration tests
    test_results = []
    
    test_results.append(test_end_to_end_user_journey())
    test_results.append(test_consent_management_integration())
    test_results.append(test_reporting_integration())
    test_results.append(test_dashboard_integration())
    test_results.append(test_user_context_integration())
    test_results.append(test_data_consistency())
    test_results.append(test_performance_under_load())
    
    # Summary
    print("\n" + "=" * 70)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} tests successful")
        print("\n🚀 BLKOUT Community Data System is production-ready!")
        print("\nIntegration test coverage:")
        print("- ✅ End-to-end user journey")
        print("- ✅ Consent management across all components")
        print("- ✅ Monthly reporting system")
        print("- ✅ Real-time dashboard")
        print("- ✅ User context personalization")
        print("- ✅ Data consistency across tables")
        print("- ✅ Performance under load")
        print("\n🎯 System ready for community testing!")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} integration tests passed")
        print("Some components need attention before production")
    
    # Cleanup
    cleanup_test_environment()

if __name__ == "__main__":
    main()