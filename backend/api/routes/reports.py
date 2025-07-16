"""
Monthly Reports API Routes
Community analytics and insights endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from services.report_generator import MonthlyReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])

# Initialize report generator
report_generator = MonthlyReportGenerator()

@router.post("/generate/{year}/{month}")
async def generate_monthly_report(
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Generate monthly community report
    
    Args:
        year: Report year (e.g., 2024)
        month: Report month (1-12)
        
    Returns:
        Generated report data
    """
    
    # Validate date parameters
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    if year < 2020 or year > datetime.now().year:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    # Check if requesting future month
    current_date = datetime.now()
    report_date = datetime(year, month, 1)
    
    if report_date > current_date:
        raise HTTPException(status_code=400, detail="Cannot generate report for future dates")
    
    try:
        report = report_generator.generate_monthly_report(year, month)
        
        return {
            "success": True,
            "report": report,
            "message": f"Monthly report generated for {year}-{month:02d}"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate report for {year}-{month:02d}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

@router.get("/list")
async def list_reports() -> Dict[str, Any]:
    """
    List all available monthly reports
    
    Returns:
        List of available reports with metadata
    """
    
    try:
        reports = report_generator.list_available_reports()
        
        return {
            "success": True,
            "reports": reports,
            "total_reports": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list reports")

@router.get("/{year}/{month}")
async def get_monthly_report(
    year: int,
    month: int
) -> Dict[str, Any]:
    """
    Get specific monthly report
    
    Args:
        year: Report year
        month: Report month (1-12)
        
    Returns:
        Monthly report data
    """
    
    # Validate parameters
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    try:
        report = report_generator.get_stored_report(year, month)
        
        if not report:
            raise HTTPException(
                status_code=404, 
                detail=f"Report not found for {year}-{month:02d}"
            )
        
        return {
            "success": True,
            "report": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve report for {year}-{month:02d}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report")

@router.get("/current")
async def get_current_month_report() -> Dict[str, Any]:
    """
    Get current month's report, generating if necessary
    
    Returns:
        Current month report data
    """
    
    try:
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Try to get existing report
        report = report_generator.get_stored_report(current_year, current_month)
        
        if not report:
            # Generate new report for current month
            report = report_generator.generate_monthly_report(current_year, current_month)
        
        return {
            "success": True,
            "report": report,
            "generated_fresh": report is None
        }
        
    except Exception as e:
        logger.error(f"Failed to get current month report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get current month report")

@router.get("/summary")
async def get_report_summary(
    months: int = Query(default=3, description="Number of recent months to include")
) -> Dict[str, Any]:
    """
    Get summary of recent reports
    
    Args:
        months: Number of recent months to include in summary
        
    Returns:
        Summary data across multiple months
    """
    
    try:
        if months < 1 or months > 12:
            raise HTTPException(status_code=400, detail="Months must be between 1 and 12")
        
        # Get recent reports
        current_date = datetime.now()
        summary_data = {
            "period_start": None,
            "period_end": current_date.strftime("%Y-%m-%d"),
            "total_months": 0,
            "reports_included": [],
            "aggregated_metrics": {
                "total_new_profiles": 0,
                "total_quiz_completions": 0,
                "total_ivor_interactions": 0,
                "growth_trend": []
            }
        }
        
        for i in range(months):
            # Calculate month/year for each period
            month_date = current_date - timedelta(days=30 * i)
            year = month_date.year
            month = month_date.month
            
            report = report_generator.get_stored_report(year, month)
            
            if report:
                summary_data["total_months"] += 1
                summary_data["reports_included"].append(f"{year}-{month:02d}")
                
                # Aggregate metrics
                if "community_growth" in report:
                    summary_data["aggregated_metrics"]["total_new_profiles"] += report["community_growth"].get("new_profiles_this_month", 0)
                    summary_data["aggregated_metrics"]["growth_trend"].append({
                        "month": f"{year}-{month:02d}",
                        "new_profiles": report["community_growth"].get("new_profiles_this_month", 0)
                    })
                
                if "liberation_pathways" in report:
                    summary_data["aggregated_metrics"]["total_quiz_completions"] += report["liberation_pathways"].get("quiz_completions_this_month", 0)
                
                if "ivor_interactions" in report:
                    summary_data["aggregated_metrics"]["total_ivor_interactions"] += report["ivor_interactions"].get("total_interactions", 0)
        
        # Set period start
        if summary_data["reports_included"]:
            summary_data["period_start"] = min(summary_data["reports_included"]) + "-01"
        
        return {
            "success": True,
            "summary": summary_data,
            "message": f"Summary generated for {summary_data['total_months']} months"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate report summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report summary")

@router.get("/health")
async def get_community_health() -> Dict[str, Any]:
    """
    Get real-time community health metrics
    
    Returns:
        Current community health indicators
    """
    
    try:
        # Generate a quick health report
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Get or generate current report
        report = report_generator.get_stored_report(current_year, current_month)
        
        if not report:
            report = report_generator.generate_monthly_report(current_year, current_month)
        
        # Extract health metrics
        community_health = report.get("community_health", {})
        growth_metrics = report.get("community_growth", {})
        engagement_metrics = report.get("engagement_patterns", {})
        
        health_summary = {
            "overall_health_score": community_health.get("community_health_score", 0),
            "active_profile_ratio": community_health.get("active_profile_ratio", 0),
            "total_active_profiles": growth_metrics.get("total_active_profiles", 0),
            "new_profiles_this_month": growth_metrics.get("new_profiles_this_month", 0),
            "engagement_distribution": engagement_metrics.get("engagement_score_distribution", {}),
            "last_updated": report["report_meta"]["generated_at"]
        }
        
        return {
            "success": True,
            "health_metrics": health_summary,
            "status": "healthy" if health_summary["overall_health_score"] > 70 else "needs_attention"
        }
        
    except Exception as e:
        logger.error(f"Failed to get community health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get community health")

@router.get("/recommendations")
async def get_recommendations() -> Dict[str, Any]:
    """
    Get current community recommendations
    
    Returns:
        Actionable recommendations for community growth
    """
    
    try:
        # Get current month's report
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        report = report_generator.get_stored_report(current_year, current_month)
        
        if not report:
            report = report_generator.generate_monthly_report(current_year, current_month)
        
        recommendations = report.get("recommendations", [])
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "high_priority_count": len([r for r in recommendations if r.get("priority") == "high"])
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")