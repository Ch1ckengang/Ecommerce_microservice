"""
Health check endpoints
"""
from fastapi import APIRouter, Request
from models.schemas import HealthResponse, StatsResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Kiểm tra sức khỏe của dịch vụ
    """
    ai_manager = request.app.state.ai_manager
    
    components = ai_manager.get_health_status()
    
    # Determine overall status
    if all(status == 'healthy' for status in components.values()):
        overall_status = "healthy"
    elif any(status == 'healthy' for status in components.values()):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "version": "1.0.0",
        "components": components
    }

@router.get("/stats", response_model=StatsResponse)
async def get_stats(request: Request):
    """
    Lấy thống kê về hệ thống AI
    """
    ai_manager = request.app.state.ai_manager
    
    stats = ai_manager.get_stats()
    
    return stats
