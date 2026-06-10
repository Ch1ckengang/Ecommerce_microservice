"""
Smart Recommendation endpoints with microservices integration
"""
from fastapi import APIRouter, Request, HTTPException, status
from models.schemas import ProductRecommendation, ScoreBreakdown
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

router = APIRouter()

class SmartRecommendRequest(BaseModel):
    """Request for smart recommendations"""
    user_id: int = Field(..., description="ID người dùng", ge=1)
    k: int = Field(10, description="Số lượng gợi ý", ge=1, le=50)
    filter_available: bool = Field(True, description="Lọc sản phẩm còn hàng")
    weights: Optional[Dict[str, float]] = Field(None, description="Trọng số tùy chỉnh")

class EnrichedRecommendation(BaseModel):
    """Enriched recommendation with product details"""
    product_id: int
    score: float
    breakdown: Dict  # Changed from ScoreBreakdown to Dict for flexibility
    product: Dict

class SmartRecommendResponse(BaseModel):
    """Response for smart recommendations"""
    recommendations: List[EnrichedRecommendation]
    total: int
    user_context: Dict
    weights_used: Dict[str, float]

@router.post("/smart-recommend", response_model=SmartRecommendResponse)
async def get_smart_recommendations(
    request: Request,
    req: SmartRecommendRequest
):
    """
    Lấy gợi ý thông minh sử dụng dữ liệu từ các microservices
    
    Tính năng:
    - Lấy lịch sử mua hàng từ Order Service
    - Lấy thông tin người dùng từ User Service
    - Lấy thông tin sản phẩm từ Product Service
    - Lọc sản phẩm còn hàng
    - Làm giàu dữ liệu gợi ý
    """
    ai_manager = request.app.state.ai_manager
    
    try:
        # Get smart recommendations with user context
        recommendations, context = await ai_manager.get_smart_recommendations_for_user(
            user_id=req.user_id,
            k=req.k,
            weights=req.weights
        )
        
        # Get enriched recommendations
        enriched, weights_used = await ai_manager.get_enriched_recommendations(
            user_id=req.user_id,
            user_sequence=context.get("interaction_sequence", []),
            k=req.k,
            exclude_seen=True,
            weights=req.weights,
            filter_available=req.filter_available
        )
        
        return SmartRecommendResponse(
            recommendations=enriched,
            total=len(enriched),
            user_context={
                "user_id": req.user_id,
                "purchase_count": len(context.get("purchase_history", [])),
                "interaction_count": len(context.get("interaction_sequence", []))
            },
            weights_used=weights_used
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo gợi ý thông minh: {str(e)}"
        )

@router.get("/user/{user_id}/context")
async def get_user_context(
    request: Request,
    user_id: int
):
    """
    Lấy ngữ cảnh người dùng từ các microservices
    
    Args:
        user_id: ID người dùng
    """
    ai_manager = request.app.state.ai_manager
    
    if not ai_manager.service_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Manager không khả dụng"
        )
    
    try:
        context = await ai_manager.service_manager.get_user_context(user_id)
        
        return {
            "user_id": user_id,
            "user": context.get("user"),
            "preferences": context.get("preferences"),
            "purchase_history": context.get("purchase_history", []),
            "interaction_sequence": context.get("interaction_sequence", []),
            "stats": {
                "total_purchases": len(context.get("purchase_history", [])),
                "total_interactions": len(context.get("interaction_sequence", []))
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy ngữ cảnh người dùng: {str(e)}"
        )
