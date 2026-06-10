"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum

# Enums
class RecommendationType(str, Enum):
    """Type of recommendation request"""
    USER_BASED = "user_based"
    QUERY_BASED = "query_based"
    PRODUCT_BASED = "product_based"
    HYBRID = "hybrid"

# Request models
class RecommendRequest(BaseModel):
    """Request for product recommendations"""
    user_id: Optional[int] = Field(None, description="ID người dùng", ge=1)
    user_sequence: Optional[List[int]] = Field(None, description="Chuỗi sản phẩm người dùng đã xem")
    query: Optional[str] = Field(None, description="Truy vấn văn bản", min_length=1, max_length=500)
    product_id: Optional[int] = Field(None, description="ID sản phẩm để tìm tương tự", ge=1)
    k: int = Field(10, description="Số lượng gợi ý", ge=1, le=50)
    exclude_seen: bool = Field(True, description="Loại trừ sản phẩm đã xem")
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Trọng số tùy chỉnh (lstm, graph, rag)"
    )
    
    @validator('user_sequence')
    def validate_user_sequence(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("user_sequence không được rỗng")
        if v is not None and len(v) > 100:
            raise ValueError("user_sequence không được vượt quá 100 sản phẩm")
        return v
    
    @validator('weights')
    def validate_weights(cls, v):
        if v is not None:
            required_keys = {'lstm', 'graph', 'rag'}
            if not required_keys.issubset(v.keys()):
                raise ValueError(f"weights phải có các key: {required_keys}")
            
            total = sum(v.values())
            if abs(total - 1.0) > 0.01:
                raise ValueError("Tổng weights phải bằng 1.0")
            
            for key, value in v.items():
                if value < 0 or value > 1:
                    raise ValueError(f"Weight {key} phải trong khoảng [0, 1]")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "user_sequence": [1, 2, 3, 4, 5],
                "query": "laptop gaming",
                "k": 10,
                "exclude_seen": True
            }
        }

class ChatbotRequest(BaseModel):
    """Request for chatbot conversation"""
    message: str = Field(..., description="Tin nhắn người dùng", min_length=1, max_length=500)
    user_id: Optional[int] = Field(None, description="ID người dùng (tùy chọn)", ge=1)
    conversation_id: Optional[str] = Field(None, description="ID hội thoại (tùy chọn)")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Tôi muốn mua laptop gaming",
                "user_id": 1
            }
        }

class SimilarProductsRequest(BaseModel):
    """Request for similar products"""
    product_id: int = Field(..., description="ID sản phẩm", ge=1)
    k: int = Field(10, description="Số lượng gợi ý", ge=1, le=50)
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "k": 10
            }
        }

# Response models
class ScoreBreakdown(BaseModel):
    """Score breakdown from different sources"""
    final_score: float = Field(..., description="Điểm cuối cùng")
    lstm: float = Field(..., description="Điểm từ LSTM")
    graph: float = Field(..., description="Điểm từ Knowledge Graph")
    rag: float = Field(..., description="Điểm từ RAG")

class ProductRecommendation(BaseModel):
    """Single product recommendation"""
    product_id: int = Field(..., description="ID sản phẩm")
    score: float = Field(..., description="Điểm gợi ý")
    breakdown: Optional[ScoreBreakdown] = Field(None, description="Chi tiết điểm số")
    explanation: Optional[str] = Field(None, description="Giải thích gợi ý")

class RecommendResponse(BaseModel):
    """Response for recommendations"""
    recommendations: List[ProductRecommendation] = Field(..., description="Danh sách gợi ý")
    total: int = Field(..., description="Tổng số gợi ý")
    recommendation_type: str = Field(..., description="Loại gợi ý")
    weights_used: Dict[str, float] = Field(..., description="Trọng số đã sử dụng")
    
    class Config:
        schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "product_id": 27,
                        "score": 0.3750,
                        "breakdown": {
                            "final_score": 0.3750,
                            "lstm": 1.0000,
                            "graph": 0.2500,
                            "rag": 0.0000
                        }
                    }
                ],
                "total": 10,
                "recommendation_type": "hybrid",
                "weights_used": {
                    "lstm": 0.3,
                    "graph": 0.3,
                    "rag": 0.4
                }
            }
        }

class ChatbotResponse(BaseModel):
    """Response for chatbot"""
    response: str = Field(..., description="Phản hồi của chatbot")
    products: Optional[List[ProductRecommendation]] = Field(None, description="Sản phẩm được đề xuất")
    conversation_id: Optional[str] = Field(None, description="ID hội thoại")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Tôi tìm thấy 5 sản phẩm phù hợp:\n\n1. 📦 ASUS ROG Strix G16...",
                "products": [
                    {
                        "product_id": 8,
                        "score": 0.85
                    }
                ],
                "conversation_id": "conv_123"
            }
        }

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Trạng thái dịch vụ")
    version: str = Field(..., description="Phiên bản")
    components: Dict[str, str] = Field(..., description="Trạng thái các thành phần")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "components": {
                    "lstm": "healthy",
                    "graph": "healthy",
                    "rag": "healthy"
                }
            }
        }

class StatsResponse(BaseModel):
    """Statistics response"""
    total_products: int = Field(..., description="Tổng số sản phẩm")
    total_users: int = Field(..., description="Tổng số người dùng")
    total_interactions: int = Field(..., description="Tổng số tương tác")
    model_info: Dict[str, dict] = Field(..., description="Thông tin mô hình")
    
    class Config:
        schema_extra = {
            "example": {
                "total_products": 50,
                "total_users": 100,
                "total_interactions": 1731,
                "model_info": {
                    "lstm_parameters": 241267,
                    "graph_nodes": 160,
                    "rag_vectors": 50
                }
            }
        }

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Mã lỗi")
    message: str = Field(..., description="Thông báo lỗi")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "INVALID_REQUEST",
                "message": "Yêu cầu không hợp lệ",
                "detail": "user_sequence không được rỗng"
            }
        }
