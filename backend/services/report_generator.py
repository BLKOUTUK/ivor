"""
Monthly Report Generation Service
Generates privacy-compliant community analytics and insights
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MonthlyReportGenerator:
    """
    Generates monthly community reports with privacy-compliant analytics
    """
    
    def __init__(self, db_path: str = "blkout_community.db"):
        self.db_path = db_path
        
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """
        Generate comprehensive monthly report
        
        Args:
            year: Report year
            month: Report month (1-12)
            
        Returns:
            Dictionary containing report data
        """
        try:
            # Calculate date range
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build comprehensive report
            report = {
                'report_meta': {
                    'generated_at': datetime.now().isoformat(),
                    'report_period': f"{year}-{month:02d}",
                    'period_start': start_str,
                    'period_end': end_str,
                    'report_type': 'monthly_community_analytics'
                },
                'community_growth': self._get_community_growth(cursor, start_str, end_str),
                'liberation_pathways': self._get_pathway_analytics(cursor, start_str, end_str),
                'ivor_interactions': self._get_ivor_analytics(cursor, start_str, end_str),
                'engagement_patterns': self._get_engagement_patterns(cursor, start_str, end_str),
                'community_health': self._get_community_health(cursor, start_str, end_str),
                'privacy_compliance': self._get_privacy_metrics(cursor, start_str, end_str),
                'recommendations': self._generate_recommendations(cursor, start_str, end_str)
            }
            
            conn.close()
            
            # Store report in database
            self._store_report(report)
            
            logger.info(f"Monthly report generated for {year}-{month:02d}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate monthly report: {e}")
            raise
    
    def _get_community_growth(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get community growth metrics"""
        
        # New profiles this month
        cursor.execute('''
            SELECT COUNT(*) FROM community_profiles 
            WHERE created_at >= ? AND created_at < ?
        ''', (start_date, end_date))
        new_profiles = cursor.fetchone()[0]
        
        # Total active profiles
        cursor.execute('''
            SELECT COUNT(*) FROM community_profiles 
            WHERE is_active = 1
        ''')
        total_active = cursor.fetchone()[0]
        
        # Growth by source
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM community_profiles 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY source
        ''', (start_date, end_date))
        growth_by_source = dict(cursor.fetchall())
        
        # Journey stage distribution
        cursor.execute('''
            SELECT journey_stage, COUNT(*) as count
            FROM community_profiles 
            WHERE is_active = 1
            GROUP BY journey_stage
        ''')
        journey_stages = dict(cursor.fetchall())
        
        return {
            'new_profiles_this_month': new_profiles,
            'total_active_profiles': total_active,
            'growth_by_source': growth_by_source,
            'journey_stage_distribution': journey_stages
        }
    
    def _get_pathway_analytics(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get liberation pathway analytics"""
        
        # Quiz completions this month
        cursor.execute('''
            SELECT COUNT(*) FROM quiz_results 
            WHERE created_at >= ? AND created_at < ?
        ''', (start_date, end_date))
        quiz_completions = cursor.fetchone()[0]
        
        # Popular pathways
        cursor.execute('''
            SELECT pathway, COUNT(*) as count
            FROM quiz_results 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY pathway
            ORDER BY count DESC
        ''', (start_date, end_date))
        popular_pathways = dict(cursor.fetchall())
        
        # Community matches
        cursor.execute('''
            SELECT community_match, COUNT(*) as count
            FROM quiz_results 
            WHERE created_at >= ? AND created_at < ?
            AND community_match IS NOT NULL
            GROUP BY community_match
            ORDER BY count DESC
        ''', (start_date, end_date))
        community_matches = dict(cursor.fetchall())
        
        return {
            'quiz_completions_this_month': quiz_completions,
            'popular_pathways': popular_pathways,
            'community_matches': community_matches
        }
    
    def _get_ivor_analytics(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get IVOR interaction analytics"""
        
        # Total interactions
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE created_at >= ? AND created_at < ?
        ''', (start_date, end_date))
        total_interactions = cursor.fetchone()[0]
        
        # Interactions by consent level
        cursor.execute('''
            SELECT consent_level, COUNT(*) as count
            FROM ivor_interactions 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY consent_level
        ''', (start_date, end_date))
        interactions_by_consent = dict(cursor.fetchall())
        
        # Average response time
        cursor.execute('''
            SELECT AVG(response_time_ms) FROM ivor_interactions 
            WHERE created_at >= ? AND created_at < ?
            AND response_time_ms IS NOT NULL
        ''', (start_date, end_date))
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Topic analysis (simplified)
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN LOWER(user_message) LIKE '%housing%' THEN 'housing'
                    WHEN LOWER(user_message) LIKE '%mental%' THEN 'mental_health'
                    WHEN LOWER(user_message) LIKE '%community%' THEN 'community'
                    WHEN LOWER(user_message) LIKE '%liberation%' THEN 'liberation'
                    ELSE 'general'
                END as topic,
                COUNT(*) as count
            FROM ivor_interactions 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY topic
        ''', (start_date, end_date))
        topic_distribution = dict(cursor.fetchall())
        
        return {
            'total_interactions': total_interactions,
            'interactions_by_consent_level': interactions_by_consent,
            'average_response_time_ms': round(avg_response_time, 2),
            'topic_distribution': topic_distribution
        }
    
    def _get_engagement_patterns(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get community engagement patterns"""
        
        # Email subscription engagement
        cursor.execute('''
            SELECT engagement_level, COUNT(*) as count
            FROM email_subscriptions 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY engagement_level
        ''', (start_date, end_date))
        email_engagement = dict(cursor.fetchall())
        
        # Hub interest
        cursor.execute('''
            SELECT 
                CASE WHEN blkouthub_interest = 1 THEN 'interested' ELSE 'not_interested' END as hub_interest,
                COUNT(*) as count
            FROM email_subscriptions 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY blkouthub_interest
        ''', (start_date, end_date))
        hub_interest = dict(cursor.fetchall())
        
        # Engagement score distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN engagement_score >= 80 THEN 'high'
                    WHEN engagement_score >= 50 THEN 'medium'
                    WHEN engagement_score >= 20 THEN 'low'
                    ELSE 'minimal'
                END as engagement_level,
                COUNT(*) as count
            FROM community_profiles 
            WHERE is_active = 1
            GROUP BY engagement_level
        ''')
        engagement_distribution = dict(cursor.fetchall())
        
        return {
            'email_engagement_levels': email_engagement,
            'hub_interest_distribution': hub_interest,
            'engagement_score_distribution': engagement_distribution
        }
    
    def _get_community_health(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get community health metrics"""
        
        # Active profiles ratio
        cursor.execute('SELECT COUNT(*) FROM community_profiles WHERE is_active = 1')
        active_profiles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM community_profiles')
        total_profiles = cursor.fetchone()[0]
        
        active_ratio = (active_profiles / total_profiles * 100) if total_profiles > 0 else 0
        
        # Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE created_at >= ?
        ''', (start_date,))
        recent_interactions = cursor.fetchone()[0]
        
        # Diversity metrics (location-based)
        cursor.execute('''
            SELECT location, COUNT(*) as count
            FROM community_profiles 
            WHERE location IS NOT NULL AND location != ''
            GROUP BY location
            ORDER BY count DESC
            LIMIT 10
        ''')
        location_diversity = dict(cursor.fetchall())
        
        return {
            'active_profile_ratio': round(active_ratio, 2),
            'recent_interaction_count': recent_interactions,
            'location_diversity': location_diversity,
            'community_health_score': self._calculate_health_score(active_ratio, recent_interactions)
        }
    
    def _get_privacy_metrics(self, cursor, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get privacy compliance metrics"""
        
        # Get total profiles for compliance calculation
        cursor.execute('SELECT COUNT(*) FROM community_profiles')
        total_profiles = cursor.fetchone()[0]
        
        # Consent level distribution
        cursor.execute('''
            SELECT 
                JSON_EXTRACT(consent_preferences, '$.personal_service') as personal_service,
                JSON_EXTRACT(consent_preferences, '$.community_insights') as community_insights,
                JSON_EXTRACT(consent_preferences, '$.peer_connections') as peer_connections,
                COUNT(*) as count
            FROM community_profiles 
            WHERE consent_preferences IS NOT NULL
            GROUP BY personal_service, community_insights, peer_connections
        ''')
        consent_distribution = []
        for row in cursor.fetchall():
            consent_distribution.append({
                'personal_service': bool(row[0]),
                'community_insights': bool(row[1]),
                'peer_connections': bool(row[2]),
                'count': row[3]
            })
        
        # Privacy compliance score
        cursor.execute('''
            SELECT COUNT(*) FROM community_profiles 
            WHERE consent_preferences IS NOT NULL
        ''')
        profiles_with_consent = cursor.fetchone()[0]
        
        privacy_compliance = (profiles_with_consent / total_profiles * 100) if total_profiles > 0 else 0
        
        return {
            'consent_distribution': consent_distribution,
            'privacy_compliance_score': round(privacy_compliance, 2),
            'profiles_with_explicit_consent': profiles_with_consent
        }
    
    def _generate_recommendations(self, cursor, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Check growth patterns
        cursor.execute('''
            SELECT COUNT(*) FROM community_profiles 
            WHERE created_at >= ? AND created_at < ?
        ''', (start_date, end_date))
        new_profiles = cursor.fetchone()[0]
        
        if new_profiles < 5:
            recommendations.append({
                'type': 'growth',
                'priority': 'high',
                'title': 'Increase Community Outreach',
                'description': 'New member growth is below target. Consider expanding social media presence and community events.',
                'action': 'Review and enhance outreach strategies'
            })
        
        # Check IVOR engagement
        cursor.execute('''
            SELECT COUNT(*) FROM ivor_interactions 
            WHERE created_at >= ? AND created_at < ?
        ''', (start_date, end_date))
        interactions = cursor.fetchone()[0]
        
        if interactions > 100:
            recommendations.append({
                'type': 'engagement',
                'priority': 'medium',
                'title': 'High IVOR Engagement',
                'description': 'Strong AI assistant usage indicates healthy community interaction.',
                'action': 'Continue current engagement strategies'
            })
        
        # Check popular pathways
        cursor.execute('''
            SELECT pathway, COUNT(*) as count
            FROM quiz_results 
            WHERE created_at >= ? AND created_at < ?
            GROUP BY pathway
            ORDER BY count DESC
            LIMIT 1
        ''', (start_date, end_date))
        top_pathway = cursor.fetchone()
        
        if top_pathway:
            recommendations.append({
                'type': 'content',
                'priority': 'medium',
                'title': f'Focus on {top_pathway[0]} Content',
                'description': f'The {top_pathway[0]} pathway is most popular with {top_pathway[1]} completions.',
                'action': 'Develop more content and resources for this pathway'
            })
        
        return recommendations
    
    def _calculate_health_score(self, active_ratio: float, recent_interactions: int) -> float:
        """Calculate overall community health score"""
        
        # Weighted scoring
        activity_score = min(active_ratio, 100) * 0.6  # 60% weight for active profiles
        interaction_score = min(recent_interactions / 10, 100) * 0.4  # 40% weight for interactions
        
        return round(activity_score + interaction_score, 2)
    
    def _store_report(self, report: Dict[str, Any]) -> None:
        """Store generated report in database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create reports table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_reports (
                    id TEXT PRIMARY KEY,
                    report_period TEXT NOT NULL,
                    report_data TEXT NOT NULL,
                    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            report_id = f"report_{report['report_meta']['report_period']}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO monthly_reports (id, report_period, report_data)
                VALUES (?, ?, ?)
            ''', (report_id, report['report_meta']['report_period'], json.dumps(report)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store report: {e}")
            raise
    
    def get_stored_report(self, year: int, month: int) -> Optional[Dict[str, Any]]:
        """Retrieve stored report from database"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            report_period = f"{year}-{month:02d}"
            cursor.execute('''
                SELECT report_data FROM monthly_reports 
                WHERE report_period = ?
            ''', (report_period,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve report: {e}")
            return None
    
    def list_available_reports(self) -> List[Dict[str, Any]]:
        """List all available reports"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT report_period, generated_at FROM monthly_reports 
                ORDER BY report_period DESC
            ''')
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'report_period': row[0],
                    'generated_at': row[1]
                })
            
            conn.close()
            return reports
            
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return []