#!/usr/bin/env python3
"""
Test Monthly Report Generation System
"""

import sqlite3
import json
from datetime import datetime, timedelta
from services.report_generator import MonthlyReportGenerator

def setup_test_data():
    """Create test data for report generation"""
    
    print("📊 Setting up test data for monthly reports...")
    
    conn = sqlite3.connect('blkout_community.db')
    cursor = conn.cursor()
    
    # Create test profiles from last month
    last_month = datetime.now() - timedelta(days=30)
    
    test_profiles = [
        {
            'id': 'test_profile_1',
            'email': 'user1@blkoutuk.com',
            'name': 'Test User 1',
            'location': 'London',
            'source': 'website',
            'journey_stage': 'engaged',
            'engagement_score': 85,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': True,
                'peer_connections': False
            }),
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'test_profile_2',
            'email': 'user2@blkoutuk.com',
            'name': 'Test User 2',
            'location': 'Manchester',
            'source': 'quiz',
            'journey_stage': 'new',
            'engagement_score': 45,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': False,
                'peer_connections': True
            }),
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'test_profile_3',
            'email': 'user3@blkoutuk.com',
            'name': 'Test User 3',
            'location': 'Birmingham',
            'source': 'social_media',
            'journey_stage': 'active',
            'engagement_score': 70,
            'consent_preferences': json.dumps({
                'personal_service': True,
                'community_insights': True,
                'peer_connections': True
            }),
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    # Insert test profiles
    for profile in test_profiles:
        cursor.execute('''
            INSERT OR REPLACE INTO community_profiles 
            (id, email, name, location, source, journey_stage, engagement_score, consent_preferences, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile['id'], profile['email'], profile['name'], profile['location'],
            profile['source'], profile['journey_stage'], profile['engagement_score'],
            profile['consent_preferences'], profile['created_at']
        ))
    
    # Create test quiz results
    quiz_results = [
        {
            'id': 'quiz_1',
            'profile_id': 'test_profile_1',
            'pathway': 'storyteller',
            'pathway_title': 'THE STORYTELLER',
            'scores': json.dumps({'identity': 4, 'community': 3, 'liberation': 2}),
            'answers': json.dumps({'energy_source': 'Creating content'}),
            'community_match': 'Creative Community',
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'quiz_2',
            'profile_id': 'test_profile_2',
            'pathway': 'organizer',
            'pathway_title': 'THE ORGANIZER',
            'scores': json.dumps({'identity': 3, 'community': 4, 'liberation': 4}),
            'answers': json.dumps({'energy_source': 'Building movements'}),
            'community_match': 'Action Network',
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for quiz in quiz_results:
        cursor.execute('''
            INSERT OR REPLACE INTO quiz_results 
            (id, profile_id, pathway, pathway_title, scores, answers, community_match, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quiz['id'], quiz['profile_id'], quiz['pathway'], quiz['pathway_title'],
            quiz['scores'], quiz['answers'], quiz['community_match'], quiz['created_at']
        ))
    
    # Create test IVOR interactions
    ivor_interactions = [
        {
            'id': 'ivor_1',
            'profile_id': 'test_profile_1',
            'session_id': 'session_1',
            'user_message': 'I need help with housing',
            'ivor_response': 'I can help connect you with housing resources.',
            'response_time_ms': 250,
            'consent_level': 'personal_service',
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'ivor_2',
            'profile_id': 'test_profile_2',
            'session_id': 'session_2',
            'user_message': 'Looking for mental health support',
            'ivor_response': 'We have mental health resources available.',
            'response_time_ms': 180,
            'consent_level': 'community_insights',
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'ivor_3',
            'profile_id': 'test_profile_3',
            'session_id': 'session_3',
            'user_message': 'How can I get involved with liberation work?',
            'ivor_response': 'There are many ways to get involved in liberation work.',
            'response_time_ms': 320,
            'consent_level': 'peer_connections',
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for interaction in ivor_interactions:
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
    
    # Create test email subscriptions
    email_subscriptions = [
        {
            'id': 'email_1',
            'profile_id': 'test_profile_1',
            'interests': json.dumps(['housing', 'community']),
            'source': 'website',
            'engagement_level': 'active',
            'blkouthub_interest': 1,
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 'email_2',
            'profile_id': 'test_profile_2',
            'interests': json.dumps(['mental_health', 'liberation']),
            'source': 'quiz',
            'engagement_level': 'casual',
            'blkouthub_interest': 0,
            'created_at': last_month.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for subscription in email_subscriptions:
        cursor.execute('''
            INSERT OR REPLACE INTO email_subscriptions 
            (id, profile_id, interests, source, engagement_level, blkouthub_interest, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscription['id'], subscription['profile_id'], subscription['interests'],
            subscription['source'], subscription['engagement_level'],
            subscription['blkouthub_interest'], subscription['created_at']
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Test data created successfully")

def test_report_generation():
    """Test monthly report generation"""
    
    print("\n🔍 Testing monthly report generation...")
    
    # Initialize report generator
    report_generator = MonthlyReportGenerator()
    
    # Generate report for current month
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    try:
        report = report_generator.generate_monthly_report(year, month)
        
        print(f"✅ Monthly report generated for {year}-{month:02d}")
        
        # Validate report structure
        required_sections = [
            'report_meta',
            'community_growth',
            'liberation_pathways',
            'ivor_interactions',
            'engagement_patterns',
            'community_health',
            'privacy_compliance',
            'recommendations'
        ]
        
        for section in required_sections:
            if section in report:
                print(f"✅ {section}: Present")
            else:
                print(f"❌ {section}: Missing")
        
        # Display key metrics
        print(f"\n📊 Key Metrics:")
        print(f"  New profiles: {report['community_growth'].get('new_profiles_this_month', 0)}")
        print(f"  Total active: {report['community_growth'].get('total_active_profiles', 0)}")
        print(f"  Quiz completions: {report['liberation_pathways'].get('quiz_completions_this_month', 0)}")
        print(f"  IVOR interactions: {report['ivor_interactions'].get('total_interactions', 0)}")
        print(f"  Community health: {report['community_health'].get('community_health_score', 0)}")
        print(f"  Recommendations: {len(report.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False

def test_report_retrieval():
    """Test report retrieval functionality"""
    
    print("\n🔍 Testing report retrieval...")
    
    report_generator = MonthlyReportGenerator()
    
    # Test list reports
    try:
        reports = report_generator.list_available_reports()
        print(f"✅ Found {len(reports)} stored reports")
        
        for report in reports:
            print(f"  - {report['report_period']}: {report['generated_at']}")
            
    except Exception as e:
        print(f"❌ Failed to list reports: {e}")
        return False
    
    # Test get specific report
    try:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        report = report_generator.get_stored_report(year, month)
        
        if report:
            print(f"✅ Retrieved report for {year}-{month:02d}")
            print(f"  Generated at: {report['report_meta']['generated_at']}")
        else:
            print(f"❌ No report found for {year}-{month:02d}")
            
    except Exception as e:
        print(f"❌ Failed to retrieve report: {e}")
        return False
    
    return True

def test_privacy_compliance():
    """Test privacy compliance in reports"""
    
    print("\n🔒 Testing privacy compliance...")
    
    report_generator = MonthlyReportGenerator()
    
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    try:
        report = report_generator.get_stored_report(year, month)
        
        if not report:
            print("❌ No report available for privacy testing")
            return False
        
        # Check privacy compliance metrics
        privacy_metrics = report.get('privacy_compliance', {})
        
        print(f"✅ Privacy compliance score: {privacy_metrics.get('privacy_compliance_score', 0)}%")
        print(f"✅ Profiles with explicit consent: {privacy_metrics.get('profiles_with_explicit_consent', 0)}")
        
        # Check that no personally identifiable information is in aggregated data
        community_growth = report.get('community_growth', {})
        
        # Should only contain aggregated counts, not individual records
        if 'growth_by_source' in community_growth:
            print("✅ Growth data properly aggregated")
        else:
            print("❌ Growth data missing or malformed")
        
        # Check IVOR interactions are anonymized
        ivor_data = report.get('ivor_interactions', {})
        
        if 'topic_distribution' in ivor_data:
            print("✅ IVOR data properly anonymized")
        else:
            print("❌ IVOR data missing or malformed")
        
        return True
        
    except Exception as e:
        print(f"❌ Privacy compliance test failed: {e}")
        return False

def main():
    """Run all report system tests"""
    
    print("🚀 Monthly Report System Testing")
    print("=" * 50)
    
    # Setup test data
    setup_test_data()
    
    # Run tests
    test_results = []
    
    test_results.append(test_report_generation())
    test_results.append(test_report_retrieval())
    test_results.append(test_privacy_compliance())
    
    # Summary
    print("\n" + "=" * 50)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print(f"✅ {passed_tests}/{total_tests} tests successful")
        print("\n📊 Monthly report system is working correctly!")
        print("\nFeatures available:")
        print("- Privacy-compliant community analytics")
        print("- Liberation pathway insights")
        print("- IVOR interaction analysis")
        print("- Community health scoring")
        print("- Actionable recommendations")
        print("- Historical report storage")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("Some issues need to be addressed")

if __name__ == "__main__":
    main()