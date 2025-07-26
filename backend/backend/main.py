from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from typing import List, Optional

from .database import get_db, engine
from .models import Base, ChatSession, ChatMessage, User
from .schemas import ChatMessageRequest, ChatResponse, ChatSessionResponse, ChatMessageResponse
from .llm_service import LLMService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce Customer Support Chatbot API",
    description="A customer support chatbot for an e-commerce clothing website",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "E-commerce Customer Support Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot-api"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint that handles customer messages and returns AI responses
    """
    try:
        # Get or create chat session
        session = await get_or_create_session(db, request.user_id, request.session_id)
        
        # Store user message
        user_message = ChatMessage(
            session_id=session.id,
            message_type="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Get conversation history for context
        conversation_history = get_conversation_history(db, session.id)
        
        # Generate AI response
        ai_response = llm_service.generate_response(
            db=db,
            user_message=request.message,
            conversation_history=conversation_history
        )
        
        # Store AI response
        ai_message = ChatMessage(
            session_id=session.id,
            message_type="assistant",
            content=ai_response
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)
        
        return ChatResponse(
            response=ai_response,
            session_id=session.session_id,
            message_id=ai_message.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )

@app.get("/api/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific chat session with all messages"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.timestamp).all()
    
    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        session_id=session.session_id,
        created_at=session.created_at,
        is_active=session.is_active,
        messages=[
            ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                message_type=msg.message_type,
                content=msg.content,
                timestamp=msg.timestamp
            ) for msg in messages
        ]
    )

@app.get("/api/sessions", response_model=List[ChatSessionResponse])
async def list_sessions(
    user_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List chat sessions, optionally filtered by user_id"""
    query = db.query(ChatSession)
    
    if user_id:
        query = query.filter(ChatSession.user_id == user_id)
    
    sessions = query.order_by(ChatSession.created_at.desc()).limit(limit).all()
    
    result = []
    for session in sessions:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.timestamp).all()
        
        result.append(ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            session_id=session.session_id,
            created_at=session.created_at,
            is_active=session.is_active,
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    session_id=msg.session_id,
                    message_type=msg.message_type,
                    content=msg.content,
                    timestamp=msg.timestamp
                ) for msg in messages
            ]
        ))
    
    return result

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Delete all messages in the session
    db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    
    # Delete the session
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

async def get_or_create_session(db: Session, user_id: Optional[int], session_id: Optional[str]) -> ChatSession:
    """Get existing session or create a new one"""
    if session_id:
        # Try to find existing session
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            return session
    
    # Create new session
    new_session_id = str(uuid.uuid4())
    session = ChatSession(
        user_id=user_id or 1,  # Default user if none provided
        session_id=new_session_id,
        is_active=True
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def get_conversation_history(db: Session, session_id: int) -> List[dict]:
    """Get conversation history for context"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()
    
    history = []
    for msg in messages:
        role = "user" if msg.message_type == "user" else "assistant"
        history.append({
            "role": role,
            "content": msg.content
        })
    
    return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 