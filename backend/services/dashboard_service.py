"""
Community Dashboard Service
Real-time community health and engagement dashboard
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from services.report_generator import MonthlyReportGenerator

logger = logging.getLogger(__name__)

class CommunityDashboardService:
    """
    Service for generating real-time community dashboard data
    """
    
    def __init__(self, db_path: str = "blkout_community.db"):
        self.db_path = db_path
        self.report_generator = MonthlyReportGenerator(db_path)
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data
        
        Returns:
            Dictionary containing all dashboard metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            dashboard_data = {
                'meta': {
                    'generated_at': datetime.now().isoformat(),
                    'dashboard_version': '1.0.0',
                    'refresh_interval': 300  # 5 minutes
                },
                'community_overview': self._get_community_overview(cursor),
                'liberation_pathways': self._get_pathway_dashboard(cursor),
                'ivor_metrics': self._get_ivor_dashboard(cursor),
                'engagement_trends': self._get_engagement_trends(cursor),
                'real_time_activity': self._get_real_time_activity(cursor),
                'privacy_health': self._get_privacy_dashboard(cursor),
                'community_alerts': self._get_community_alerts(cursor),
                'growth_metrics': self._get_growth_dashboard(cursor)
            }
            
            conn.close()
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard data: {e}")
            raise
    
    def _get_community_overview(self, cursor) -> Dict[str, Any]:
        """Get high-level community overview"""
        
        # Total active members
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE is_active = 1')
        total_active = cursor.fetchone()[0]
        
        # New members this week
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM community_profiles 
            WHERE created_at >= ? AND is_active = 1
        ''', (week_ago,))
        new_this_week = cursor.fetchone()[0]
        
        # Quiz completion rate
        cursor.execute('SELECT COUNT(*) FROM quiz_results')
        quiz_completions = cursor.fetchone()[0]
        
        completion_rate = (quiz_completions / total_active * 100) if total_active > 0 else 0
        
        # IVOR engagement today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE DATE(created_at) = ?
        ''', (today,))
        ivor_today = cursor.fetchone()[0]
        
        # Community health score
        health_score = self._calculate_community_health_score(cursor)
        
        return {
            'total_active_members': total_active,
            'new_members_this_week': new_this_week,
            'quiz_completion_rate': round(completion_rate, 1),
            'ivor_interactions_today': ivor_today,
            'community_health_score': health_score,
            'health_status': self._get_health_status(health_score)
        }
    
    def _get_pathway_dashboard(self, cursor) -> Dict[str, Any]:
        """Get liberation pathway dashboard metrics"""
        
        # Most popular pathways (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT pathway, COUNT(*) as count
            FROM quiz_results 
            WHERE created_at >= ?
            GROUP BY pathway
            ORDER BY count DESC
            LIMIT 5
        ''', (thirty_days_ago,))
        popular_pathways = dict(cursor.fetchall())
        
        # Community matching success
        cursor.execute('''
            SELECT 
                CASE WHEN community_match IS NOT NULL THEN 'matched' ELSE 'unmatched' END as match_status,
                COUNT(*) as count
            FROM quiz_results 
            WHERE created_at >= ?
            GROUP BY match_status
        ''', (thirty_days_ago,))
        match_stats = dict(cursor.fetchall())
        
        # Pathway diversity score
        cursor.execute('''
            SELECT pathway, COUNT(*) as count
            FROM quiz_results
            GROUP BY pathway
        ''')
        all_pathways = dict(cursor.fetchall())
        
        # Calculate diversity (how evenly distributed pathways are)
        total_quizzes = sum(all_pathways.values())
        if total_quizzes > 0:
            diversity_score = len(all_pathways) / 8 * 100  # 8 total pathways
        else:
            diversity_score = 0
        
        return {
            'popular_pathways': popular_pathways,
            'community_matching': match_stats,
            'pathway_diversity_score': round(diversity_score, 1),
            'total_pathway_types': len(all_pathways),
            'completion_trend': self._get_pathway_trend(cursor)
        }
    
    def _get_ivor_dashboard(self, cursor) -> Dict[str, Any]:
        """Get IVOR AI dashboard metrics"""
        
        # Today's interactions
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE DATE(created_at) = ?
        ''', (today,))
        today_interactions = cursor.fetchone()[0]
        
        # Average response time (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT AVG(response_time_ms) FROM ivor_interactions 
            WHERE created_at >= ? AND response_time_ms IS NOT NULL
        ''', (yesterday,))
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Most discussed topics (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN LOWER(user_message) LIKE '%housing%' THEN 'housing'
                    WHEN LOWER(user_message) LIKE '%mental%' THEN 'mental_health'
                    WHEN LOWER(user_message) LIKE '%community%' THEN 'community'
                    WHEN LOWER(user_message) LIKE '%liberation%' THEN 'liberation'
                    WHEN LOWER(user_message) LIKE '%job%' OR LOWER(user_message) LIKE '%work%' THEN 'employment'
                    ELSE 'general'
                END as topic,
                COUNT(*) as count
            FROM ivor_interactions 
            WHERE created_at >= ?
            GROUP BY topic
            ORDER BY count DESC
        ''', (week_ago,))
        top_topics = dict(cursor.fetchall())
        
        # User satisfaction proxy (response length correlation)
        cursor.execute('''
            SELECT AVG(LENGTH(ivor_response)) as avg_response_length
            FROM ivor_interactions 
            WHERE created_at >= ?
        ''', (week_ago,))
        avg_response_length = cursor.fetchone()[0] or 0
        
        # Engagement by consent level
        cursor.execute('''
            SELECT consent_level, COUNT(*) as count
            FROM ivor_interactions 
            WHERE created_at >= ?
            GROUP BY consent_level
        ''', (week_ago,))
        consent_engagement = dict(cursor.fetchall())
        
        return {
            'interactions_today': today_interactions,
            'avg_response_time_ms': round(avg_response_time, 2),
            'top_discussion_topics': top_topics,
            'avg_response_length': round(avg_response_length, 1),
            'engagement_by_consent': consent_engagement,
            'performance_status': 'excellent' if avg_response_time < 500 else 'good' if avg_response_time < 1000 else 'needs_attention'
        }
    
    def _get_engagement_trends(self, cursor) -> Dict[str, Any]:
        """Get engagement trend analysis"""
        
        # Daily activity for last 7 days
        daily_activity = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # IVOR interactions
            cursor.execute('''
                SELECT COUNT(*) FROM ivor_interactions 
                WHERE DATE(created_at) = ?
            ''', (date,))
            ivor_count = cursor.fetchone()[0]
            
            # New profiles
            cursor.execute('''
                SELECT COUNT(*) FROM community_profiles 
                WHERE DATE(created_at) = ?
            ''', (date,))
            profiles_count = cursor.fetchone()[0]
            
            # Quiz completions
            cursor.execute('''
                SELECT COUNT(*) FROM quiz_results 
                WHERE DATE(created_at) = ?
            ''', (date,))
            quiz_count = cursor.fetchone()[0]
            
            daily_activity.append({
                'date': date,
                'ivor_interactions': ivor_count,
                'new_profiles': profiles_count,
                'quiz_completions': quiz_count,
                'total_activity': ivor_count + profiles_count + quiz_count
            })
        
        # Calculate trend direction
        if len(daily_activity) >= 2:
            recent_avg = sum(d['total_activity'] for d in daily_activity[:3]) / 3
            older_avg = sum(d['total_activity'] for d in daily_activity[3:]) / 4
            trend_direction = 'increasing' if recent_avg > older_avg else 'decreasing' if recent_avg < older_avg else 'stable'
        else:
            trend_direction = 'stable'
        
        # Engagement score distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN engagement_score >= 80 THEN 'highly_engaged'
                    WHEN engagement_score >= 50 THEN 'moderately_engaged'
                    WHEN engagement_score >= 20 THEN 'lightly_engaged'
                    ELSE 'low_engagement'
                END as engagement_level,
                COUNT(*) as count
            FROM community_profiles 
            WHERE is_active = 1
            GROUP BY engagement_level
        ''')
        engagement_distribution = dict(cursor.fetchall())
        
        return {
            'daily_activity': daily_activity,
            'trend_direction': trend_direction,
            'engagement_distribution': engagement_distribution,
            'peak_activity_hour': self._get_peak_activity_hour(cursor)
        }
    
    def _get_real_time_activity(self, cursor) -> Dict[str, Any]:
        """Get real-time activity metrics"""
        
        # Activity in last hour
        hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE created_at >= ?
        ''', (hour_ago,))
        activity_last_hour = cursor.fetchone()[0]
        
        # Recent interactions (last 5)
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN LOWER(user_message) LIKE '%housing%' THEN 'housing'
                    WHEN LOWER(user_message) LIKE '%mental%' THEN 'mental_health'
                    WHEN LOWER(user_message) LIKE '%community%' THEN 'community'
                    WHEN LOWER(user_message) LIKE '%liberation%' THEN 'liberation'
                    ELSE 'general'
                END as topic,
                consent_level,
                created_at
            FROM ivor_interactions 
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        recent_interactions = []
        for row in cursor.fetchall():
            recent_interactions.append({
                'topic': row[0],
                'consent_level': row[1],
                'timestamp': row[2]
            })
        
        # Active now (approximation based on recent activity)
        fifteen_min_ago = (datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT COUNT(DISTINCT session_id) FROM ivor_interactions 
            WHERE created_at >= ?
        ''', (fifteen_min_ago,))
        estimated_active_now = cursor.fetchone()[0]
        
        return {
            'activity_last_hour': activity_last_hour,
            'estimated_active_now': estimated_active_now,
            'recent_interactions': recent_interactions,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_privacy_dashboard(self, cursor) -> Dict[str, Any]:
        """Get privacy compliance dashboard"""
        
        # Consent preferences distribution
        cursor.execute('''
            SELECT consent_preferences, COUNT(*) as count
            FROM community_profiles 
            WHERE consent_preferences IS NOT NULL
            GROUP BY consent_preferences
        ''')
        
        consent_analysis = {
            'personal_service': 0,
            'community_insights': 0,
            'peer_connections': 0,
            'anonymous_only': 0
        }
        
        for row in cursor.fetchall():
            try:
                prefs = json.loads(row[0])
                count = row[1]
                
                if prefs.get('personal_service', False):
                    consent_analysis['personal_service'] += count
                if prefs.get('community_insights', False):
                    consent_analysis['community_insights'] += count
                if prefs.get('peer_connections', False):
                    consent_analysis['peer_connections'] += count
                if not any(prefs.values()):
                    consent_analysis['anonymous_only'] += count
            except json.JSONDecodeError:
                continue
        
        # Privacy compliance score
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE consent_preferences IS NOT NULL')
        with_consent = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM community_profiles')
        total_profiles = cursor.fetchone()[0]
        
        compliance_score = (with_consent / total_profiles * 100) if total_profiles > 0 else 0
        
        return {
            'consent_distribution': consent_analysis,
            'privacy_compliance_score': round(compliance_score, 1),
            'profiles_with_consent': with_consent,
            'total_profiles': total_profiles,
            'compliance_status': 'excellent' if compliance_score >= 95 else 'good' if compliance_score >= 80 else 'needs_improvement'
        }
    
    def _get_community_alerts(self, cursor) -> List[Dict[str, Any]]:
        """Get community alerts and recommendations"""
        
        alerts = []
        
        # Check for low engagement
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE DATE(created_at) = ?
        ''', (datetime.now().strftime('%Y-%m-%d'),))
        today_interactions = cursor.fetchone()[0]
        
        if today_interactions < 5:
            alerts.append({
                'type': 'engagement',
                'severity': 'medium',
                'title': 'Low Daily Engagement',
                'message': f'Only {today_interactions} IVOR interactions today. Consider community outreach.',
                'action': 'Review engagement strategies'
            })
        
        # Check for quiz completion rate
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE is_active = 1')
        active_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM quiz_results')
        quiz_completions = cursor.fetchone()[0]
        
        if active_profiles > 0:
            completion_rate = quiz_completions / active_profiles * 100
            if completion_rate < 50:
                alerts.append({
                    'type': 'conversion',
                    'severity': 'high',
                    'title': 'Low Quiz Completion Rate',
                    'message': f'Only {completion_rate:.1f}% of active members completed the liberation quiz.',
                    'action': 'Improve quiz accessibility and promotion'
                })
        
        # Check for pathway diversity
        cursor.execute('''
            SELECT COUNT(DISTINCT pathway) FROM quiz_results
        ''')
        unique_pathways = cursor.fetchone()[0]
        
        if unique_pathways < 4:
            alerts.append({
                'type': 'diversity',
                'severity': 'low',
                'title': 'Limited Pathway Diversity',
                'message': f'Only {unique_pathways} different liberation pathways represented.',
                'action': 'Review quiz questions and pathway balance'
            })
        
        # Check for response time
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT AVG(response_time_ms) FROM ivor_interactions 
            WHERE created_at >= ? AND response_time_ms IS NOT NULL
        ''', (yesterday,))
        avg_response_time = cursor.fetchone()[0] or 0
        
        if avg_response_time > 1000:
            alerts.append({
                'type': 'performance',
                'severity': 'medium',
                'title': 'Slow IVOR Response Time',
                'message': f'Average response time is {avg_response_time:.0f}ms.',
                'action': 'Optimize AI service performance'
            })
        
        return alerts
    
    def _get_growth_dashboard(self, cursor) -> Dict[str, Any]:
        """Get growth metrics dashboard"""
        
        # Monthly growth trend
        monthly_growth = []
        for i in range(6):  # Last 6 months
            date = datetime.now() - timedelta(days=30*i)
            month_start = date.replace(day=1).strftime('%Y-%m-%d')
            
            if i == 0:
                month_end = datetime.now().strftime('%Y-%m-%d')
            else:
                next_month = date.replace(day=1) + timedelta(days=32)
                month_end = next_month.replace(day=1).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT COUNT(*) FROM community_profiles 
                WHERE created_at >= ? AND created_at < ?
            ''', (month_start, month_end))
            new_profiles = cursor.fetchone()[0]
            
            monthly_growth.append({
                'month': date.strftime('%Y-%m'),
                'new_profiles': new_profiles
            })
        
        # Growth by source
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM community_profiles 
            WHERE created_at >= ?
            GROUP BY source
            ORDER BY count DESC
        ''', ((datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),))
        growth_by_source = dict(cursor.fetchall())
        
        # Calculate growth rate
        if len(monthly_growth) >= 2:
            current_month = monthly_growth[0]['new_profiles']
            previous_month = monthly_growth[1]['new_profiles']
            growth_rate = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
        else:
            growth_rate = 0
        
        return {
            'monthly_growth': monthly_growth,
            'growth_by_source': growth_by_source,
            'growth_rate_percent': round(growth_rate, 1),
            'growth_trend': 'increasing' if growth_rate > 10 else 'stable' if growth_rate > -10 else 'decreasing'
        }
    
    def _calculate_community_health_score(self, cursor) -> float:
        """Calculate overall community health score"""
        
        # Active members ratio (30% weight)
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE is_active = 1')
        active_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM community_profiles')
        total_profiles = cursor.fetchone()[0]
        
        active_ratio = (active_profiles / total_profiles) if total_profiles > 0 else 0
        
        # Recent engagement (25% weight)
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE created_at >= ?
        ''', (week_ago,))
        recent_interactions = cursor.fetchone()[0]
        
        engagement_score = min(recent_interactions / 50, 1)  # Normalize to 0-1
        
        # Quiz completion rate (25% weight)
        cursor.execute('SELECT COUNT(*) FROM quiz_results')
        quiz_completions = cursor.fetchone()[0]
        
        completion_rate = (quiz_completions / active_profiles) if active_profiles > 0 else 0
        completion_score = min(completion_rate, 1)
        
        # Diversity score (20% weight)
        cursor.execute('SELECT COUNT(DISTINCT pathway) FROM quiz_results')
        unique_pathways = cursor.fetchone()[0]
        
        diversity_score = unique_pathways / 8  # 8 total pathways
        
        # Calculate weighted score
        health_score = (
            active_ratio * 0.3 +
            engagement_score * 0.25 +
            completion_score * 0.25 +
            diversity_score * 0.2
        ) * 100
        
        return round(health_score, 2)
    
    def _get_health_status(self, score: float) -> str:
        """Get health status based on score"""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'needs_attention'
    
    def _get_pathway_trend(self, cursor) -> str:
        """Get pathway completion trend"""
        
        # Last 7 days
        recent_completions = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM quiz_results 
                WHERE DATE(created_at) = ?
            ''', (date,))
            count = cursor.fetchone()[0]
            recent_completions.append(count)
        
        if len(recent_completions) >= 4:
            recent_avg = sum(recent_completions[:3]) / 3
            older_avg = sum(recent_completions[3:]) / 4
            
            if recent_avg > older_avg * 1.1:
                return 'increasing'
            elif recent_avg < older_avg * 0.9:
                return 'decreasing'
            else:
                return 'stable'
        
        return 'stable'
    
    def _get_peak_activity_hour(self, cursor) -> int:
        """Get peak activity hour of day"""
        
        cursor.execute('''
            SELECT 
                CAST(strftime('%H', created_at) AS INTEGER) as hour,
                COUNT(*) as count
            FROM ivor_interactions 
            WHERE created_at >= ?
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        ''', ((datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),))
        
        result = cursor.fetchone()
        return result[0] if result else 12  # Default to noon if no data