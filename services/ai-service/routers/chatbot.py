"""
Chatbot endpoints
"""
from fastapi import APIRouter, Request, HTTPException, status
from models.schemas import ChatbotRequest, ChatbotResponse
import uuid

router = APIRouter()

@router.post("/chatbot", response_model=ChatbotResponse)
async def chat(
    request: Request,
    req: ChatbotRequest
):
    """
    Tương tác với chatbot tư vấn sản phẩm
    
    Chatbot có thể:
    - Trả lời câu hỏi về sản phẩm
    - Tìm kiếm sản phẩm theo mô tả
    - Gợi ý sản phẩm tương tự
    """
    ai_manager = request.app.state.ai_manager
    
    try:
        # Get chatbot response
        response_text = ai_manager.get_chatbot_response(req.message)
        
        # Generate conversation ID if not provided
        conversation_id = req.conversation_id or f"conv_{uuid.uuid4().hex[:8]}"
        
        return ChatbotResponse(
            response=response_text,
            products=None,  # Could extract products from response in future
            conversation_id=conversation_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi chatbot: {str(e)}"
        )
