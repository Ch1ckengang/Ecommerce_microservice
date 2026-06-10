"""
Recommendation endpoints
"""
from fastapi import APIRouter, Request, HTTPException, status
from models.schemas import (
    RecommendRequest,
    RecommendResponse,
    SimilarProductsRequest,
    ProductRecommendation,
    ScoreBreakdown,
    ErrorResponse
)
from typing import List

router = APIRouter()

@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(
    request: Request,
    req: RecommendRequest
):
    """
    Lấy gợi ý sản phẩm
    
    Hỗ trợ nhiều loại gợi ý:
    - Dựa trên người dùng (user_id + user_sequence)
    - Dựa trên truy vấn văn bản (query)
    - Dựa trên sản phẩm (product_id)
    - Kết hợp (hybrid)
    """
    ai_manager = request.app.state.ai_manager
    
    # Validate request
    if not any([req.user_id, req.user_sequence, req.query, req.product_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phải cung cấp ít nhất một trong: user_id, user_sequence, query, hoặc product_id"
        )
    
    try:
        # Get recommendations
        recommendations, weights_used = ai_manager.get_recommendations(
            user_id=req.user_id,
            user_sequence=req.user_sequence,
            query=req.query,
            product_id=req.product_id,
            k=req.k,
            exclude_seen=req.exclude_seen,
            weights=req.weights
        )
        
        # Determine recommendation type
        if req.query and not req.user_sequence and not req.product_id:
            rec_type = "query_based"
        elif req.product_id and not req.user_sequence and not req.query:
            rec_type = "product_based"
        elif req.user_sequence and not req.query and not req.product_id:
            rec_type = "user_based"
        else:
            rec_type = "hybrid"
        
        # Format response
        formatted_recs = []
        for product_id, scores in recommendations:
            formatted_recs.append(
                ProductRecommendation(
                    product_id=product_id,
                    score=scores['final_score'],
                    breakdown=ScoreBreakdown(
                        final_score=scores['final_score'],
                        lstm=scores['lstm'],
                        graph=scores['graph'],
                        rag=scores['rag']
                    )
                )
            )
        
        return RecommendResponse(
            recommendations=formatted_recs,
            total=len(formatted_recs),
            recommendation_type=rec_type,
            weights_used=weights_used
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo gợi ý: {str(e)}"
        )

@router.get("/similar/{product_id}", response_model=RecommendResponse)
async def get_similar_products(
    request: Request,
    product_id: int,
    k: int = 10
):
    """
    Lấy sản phẩm tương tự
    
    Args:
        product_id: ID sản phẩm
        k: Số lượng gợi ý (mặc định: 10)
    """
    ai_manager = request.app.state.ai_manager
    
    if product_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id phải lớn hơn 0"
        )
    
    if k < 1 or k > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="k phải trong khoảng [1, 50]"
        )
    
    try:
        recommendations = ai_manager.get_similar_products(
            product_id=product_id,
            k=k
        )
        
        # Format response
        formatted_recs = []
        for pid, scores in recommendations:
            formatted_recs.append(
                ProductRecommendation(
                    product_id=pid,
                    score=scores['final_score'],
                    breakdown=ScoreBreakdown(
                        final_score=scores['final_score'],
                        lstm=scores['lstm'],
                        graph=scores['graph'],
                        rag=scores['rag']
                    )
                )
            )
        
        return RecommendResponse(
            recommendations=formatted_recs,
            total=len(formatted_recs),
            recommendation_type="product_based",
            weights_used=ai_manager.hybrid.weights
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tìm sản phẩm tương tự: {str(e)}"
        )

@router.post("/explain")
async def explain_recommendation(
    request: Request,
    product_id: int,
    breakdown: ScoreBreakdown
):
    """
    Giải thích gợi ý
    
    Args:
        product_id: ID sản phẩm
        breakdown: Chi tiết điểm số
    """
    ai_manager = request.app.state.ai_manager
    
    try:
        explanation = ai_manager.explain_recommendation(
            product_id=product_id,
            score_breakdown={
                'final_score': breakdown.final_score,
                'lstm': breakdown.lstm,
                'graph': breakdown.graph,
                'rag': breakdown.rag
            }
        )
        
        return {
            "product_id": product_id,
            "explanation": explanation
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo giải thích: {str(e)}"
        )
