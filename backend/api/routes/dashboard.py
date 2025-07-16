"""
Community Dashboard API Routes
Real-time community analytics and insights
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta

from services.dashboard_service import CommunityDashboardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Initialize dashboard service
dashboard_service = CommunityDashboardService()

@router.get("/")
async def get_dashboard() -> Dict[str, Any]:
    """
    Get complete community dashboard data
    
    Returns:
        Complete dashboard with all metrics
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@router.get("/overview")
async def get_community_overview() -> Dict[str, Any]:
    """
    Get high-level community overview
    
    Returns:
        Community overview metrics
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        overview = dashboard_data['community_overview']
        
        return {
            "success": True,
            "overview": overview,
            "last_updated": dashboard_data['meta']['generated_at']
        }
        
    except Exception as e:
        logger.error(f"Failed to get community overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve community overview")

@router.get("/pathways")
async def get_pathway_dashboard() -> Dict[str, Any]:
    """
    Get liberation pathway dashboard
    
    Returns:
        Pathway analytics and trends
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        pathways = dashboard_data['liberation_pathways']
        
        return {
            "success": True,
            "pathways": pathways,
            "message": "Pathway dashboard retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get pathway dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pathway dashboard")

@router.get("/ivor")
async def get_ivor_dashboard() -> Dict[str, Any]:
    """
    Get IVOR AI dashboard metrics
    
    Returns:
        IVOR performance and engagement metrics
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        ivor_metrics = dashboard_data['ivor_metrics']
        
        return {
            "success": True,
            "ivor_metrics": ivor_metrics,
            "message": "IVOR dashboard retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get IVOR dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve IVOR dashboard")

@router.get("/engagement")
async def get_engagement_dashboard() -> Dict[str, Any]:
    """
    Get engagement trends and analysis
    
    Returns:
        Engagement metrics and trends
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        engagement = dashboard_data['engagement_trends']
        
        return {
            "success": True,
            "engagement": engagement,
            "message": "Engagement dashboard retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get engagement dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve engagement dashboard")

@router.get("/realtime")
async def get_realtime_activity() -> Dict[str, Any]:
    """
    Get real-time activity metrics
    
    Returns:
        Current activity and recent interactions
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        realtime = dashboard_data['real_time_activity']
        
        return {
            "success": True,
            "realtime_activity": realtime,
            "message": "Real-time activity retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get real-time activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve real-time activity")

@router.get("/privacy")
async def get_privacy_dashboard() -> Dict[str, Any]:
    """
    Get privacy compliance dashboard
    
    Returns:
        Privacy and consent metrics
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        privacy = dashboard_data['privacy_health']
        
        return {
            "success": True,
            "privacy_metrics": privacy,
            "message": "Privacy dashboard retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get privacy dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve privacy dashboard")

@router.get("/alerts")
async def get_community_alerts() -> Dict[str, Any]:
    """
    Get community alerts and recommendations
    
    Returns:
        Current alerts and action items
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        alerts = dashboard_data['community_alerts']
        
        # Count alerts by severity
        alert_counts = {
            'high': len([a for a in alerts if a.get('severity') == 'high']),
            'medium': len([a for a in alerts if a.get('severity') == 'medium']),
            'low': len([a for a in alerts if a.get('severity') == 'low'])
        }
        
        return {
            "success": True,
            "alerts": alerts,
            "alert_counts": alert_counts,
            "total_alerts": len(alerts),
            "message": "Community alerts retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get community alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve community alerts")

@router.get("/growth")
async def get_growth_dashboard() -> Dict[str, Any]:
    """
    Get growth metrics and trends
    
    Returns:
        Community growth analysis
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        growth = dashboard_data['growth_metrics']
        
        return {
            "success": True,
            "growth_metrics": growth,
            "message": "Growth dashboard retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get growth dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve growth dashboard")

@router.get("/health")
async def get_health_summary() -> Dict[str, Any]:
    """
    Get community health summary
    
    Returns:
        Health score and status summary
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        overview = dashboard_data['community_overview']
        alerts = dashboard_data['community_alerts']
        
        # Calculate health summary
        health_summary = {
            'overall_score': overview['community_health_score'],
            'status': overview['health_status'],
            'active_members': overview['total_active_members'],
            'new_members_this_week': overview['new_members_this_week'],
            'critical_alerts': len([a for a in alerts if a.get('severity') == 'high']),
            'recommendations': len(alerts),
            'last_updated': dashboard_data['meta']['generated_at']
        }
        
        return {
            "success": True,
            "health_summary": health_summary,
            "message": "Health summary retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get health summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve health summary")

@router.get("/metrics")
async def get_key_metrics(
    period: str = Query(default="7d", description="Time period: 1d, 7d, 30d")
) -> Dict[str, Any]:
    """
    Get key metrics for specified time period
    
    Args:
        period: Time period for metrics (1d, 7d, 30d)
        
    Returns:
        Key metrics for the specified period
    """
    
    try:
        # Parse period
        if period == "1d":
            days = 1
        elif period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        else:
            raise HTTPException(status_code=400, detail="Invalid period. Use 1d, 7d, or 30d")
        
        dashboard_data = dashboard_service.get_dashboard_data()
        
        # Extract relevant metrics based on period
        metrics = {
            'period': period,
            'community_health_score': dashboard_data['community_overview']['community_health_score'],
            'total_active_members': dashboard_data['community_overview']['total_active_members'],
            'ivor_interactions': dashboard_data['ivor_metrics']['interactions_today'] if period == "1d" else None,
            'quiz_completion_rate': dashboard_data['community_overview']['quiz_completion_rate'],
            'top_pathways': dashboard_data['liberation_pathways']['popular_pathways'],
            'engagement_trend': dashboard_data['engagement_trends']['trend_direction'],
            'privacy_compliance': dashboard_data['privacy_health']['privacy_compliance_score'],
            'critical_alerts': len([a for a in dashboard_data['community_alerts'] if a.get('severity') == 'high'])
        }
        
        return {
            "success": True,
            "metrics": metrics,
            "message": f"Key metrics for {period} retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get key metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve key metrics")

@router.get("/export")
async def export_dashboard_data(
    format: str = Query(default="json", description="Export format: json, csv")
) -> Dict[str, Any]:
    """
    Export dashboard data
    
    Args:
        format: Export format (json, csv)
        
    Returns:
        Exported dashboard data
    """
    
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid format. Use json or csv")
        
        dashboard_data = dashboard_service.get_dashboard_data()
        
        if format == "json":
            return {
                "success": True,
                "data": dashboard_data,
                "format": "json",
                "exported_at": datetime.now().isoformat()
            }
        elif format == "csv":
            # Convert key metrics to CSV format
            csv_data = []
            
            # Community overview
            overview = dashboard_data['community_overview']
            csv_data.append([
                "Community Overview",
                f"Active Members: {overview['total_active_members']}",
                f"Health Score: {overview['community_health_score']}",
                f"New This Week: {overview['new_members_this_week']}"
            ])
            
            # Pathway data
            pathways = dashboard_data['liberation_pathways']['popular_pathways']
            csv_data.append(["Popular Pathways"] + [f"{k}: {v}" for k, v in pathways.items()])
            
            # IVOR metrics
            ivor = dashboard_data['ivor_metrics']
            csv_data.append([
                "IVOR Metrics",
                f"Interactions Today: {ivor['interactions_today']}",
                f"Avg Response Time: {ivor['avg_response_time_ms']}ms",
                f"Performance: {ivor['performance_status']}"
            ])
            
            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "exported_at": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export dashboard data")

@router.get("/widget/{widget_type}")
async def get_dashboard_widget(
    widget_type: str
) -> Dict[str, Any]:
    """
    Get specific dashboard widget data
    
    Args:
        widget_type: Type of widget (health, pathways, ivor, engagement, growth)
        
    Returns:
        Widget-specific data
    """
    
    try:
        dashboard_data = dashboard_service.get_dashboard_data()
        
        widget_map = {
            'health': dashboard_data['community_overview'],
            'pathways': dashboard_data['liberation_pathways'],
            'ivor': dashboard_data['ivor_metrics'],
            'engagement': dashboard_data['engagement_trends'],
            'growth': dashboard_data['growth_metrics'],
            'privacy': dashboard_data['privacy_health'],
            'alerts': dashboard_data['community_alerts']
        }
        
        if widget_type not in widget_map:
            raise HTTPException(
                status_code=404, 
                detail=f"Widget type '{widget_type}' not found. Available: {list(widget_map.keys())}"
            )
        
        return {
            "success": True,
            "widget_type": widget_type,
            "widget_data": widget_map[widget_type],
            "last_updated": dashboard_data['meta']['generated_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard widget: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard widget")