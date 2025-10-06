from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import json
import asyncio
from datetime import datetime

# Import your existing AI class
from main import SierraLeoneAI, SIERRA_LEONE_CONTEXT

# Initialize FastAPI
app = FastAPI(
    title="Sierra Leonean Context AI API",
    description="Intelligent Q&A system with deep knowledge of Sierra Leone",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI (singleton pattern)
ai_instance = None


def get_ai():
    """Get or create AI instance"""
    global ai_instance
    if ai_instance is None:
        ai_instance = SierraLeoneAI()
    return ai_instance


# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    include_sources: Optional[bool] = True
    max_sources: Optional[int] = 3


class HealthResponse(BaseModel):
    status: str
    message: str
    categories_loaded: list[str]
    timestamp: str


# Helper Functions
def format_source_document(doc) -> dict:
    """Convert LangChain document to API response format"""
    metadata = doc.metadata
    source = metadata.get('source', 'Unknown')
    category = metadata.get('category', 'Unknown')
    retrieved_from = metadata.get('retrieved_from', category)

    # Clean up source path
    if 'data/' in source:
        source = source.split('data/')[-1]
    source = source.replace('.txt', '')

    return {
        "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
        "source": source,
        "category": category,
        "retrieved_from": retrieved_from
    }


async def generate_streaming_response(question: str, ai: SierraLeoneAI, include_sources: bool = True, max_sources: int = 3) -> AsyncGenerator[str, None]:
    """Generate streaming response"""

    # Classify and get initial info
    category = ai.classify_question(question)

    yield json.dumps({
        "type": "metadata",
        "data": {
            "category": category,
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
    }) + "\n"

    await asyncio.sleep(0.1)

    # Get the full response
    try:
        result, _ = ai.query(question)
        answer = result['result']

        # Stream the answer word by word
        words = answer.split()
        chunk_size = 3  # Send 3 words at a time

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size]) + " "
            yield json.dumps({
                "type": "content",
                "data": {"text": chunk}
            }) + "\n"
            await asyncio.sleep(0.05)  # Small delay for streaming effect

        # Send sources if available
        if include_sources and result.get('source_documents'):
            sources = [format_source_document(doc) for doc in result['source_documents'][:max_sources]]
            yield json.dumps({
                "type": "sources",
                "data": {"sources": sources}
            }) + "\n"

        # Send completion signal
        yield json.dumps({
            "type": "done",
            "data": {"status": "complete"}
        }) + "\n"

    except Exception as e:
        yield json.dumps({
            "type": "error",
            "data": {"message": str(e)}
        }) + "\n"


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Sierra Leonean Context AI API",
        "version": "1.0.0",
        "description": "Intelligent Q&A system with deep knowledge of Sierra Leone",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST) - streaming by default",
            "categories": "/categories",
            "about": "/about",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        ai = get_ai()
        return HealthResponse(
            status="healthy",
            message="Sierra Leonean Context AI is running",
            categories_loaded=list(ai.vectorstores.keys()),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


@app.get("/categories", response_model=dict)
async def get_categories():
    """Get available knowledge categories"""
    ai = get_ai()

    categories_info = {}
    for category, vectorstore in ai.vectorstores.items():
        try:
            # Get document count
            doc_count = vectorstore.index.ntotal
            categories_info[category] = {
                "name": category,
                "document_count": doc_count,
                "status": "active"
            }
        except:
            categories_info[category] = {
                "name": category,
                "status": "active"
            }

    return {
        "categories": categories_info,
        "total": len(categories_info)
    }


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Query endpoint with streaming by default (like ChatGPT)

    Returns Server-Sent Events (SSE) stream with:
    - Metadata (category, timestamp)
    - Content chunks (streamed answer)
    - Sources (at the end)
    - Done signal
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        ai = get_ai()

        return StreamingResponse(
            generate_streaming_response(
                request.question,
                ai,
                request.include_sources,
                request.max_sources
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/about", response_model=dict)
async def about():
    """Information about Sierra Leone context and capabilities"""
    return {
        "name": "Sierra Leonean Context AI",
        "description": "AI assistant with deep expertise in Sierra Leone",
        "context": SIERRA_LEONE_CONTEXT,
        "capabilities": {
            "history": "Civil war, independence, colonial period, post-war recovery",
            "culture": "Ethnic diversity, languages, traditions, music, food, religion",
            "politics": "Democracy, paramount chiefs, governance, elections",
            "economy": "Mining, agriculture, fishing, development challenges",
            "general": "Geography, demographics, health, education"
        },
        "features": [
            "Context-aware responses",
            "Multi-category knowledge base",
            "Real-time streaming responses",
            "Source citations",
            "Simple explanations"
        ]
    }


# Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize AI on startup"""
    print("\n" + "=" * 80)
    print("🇸🇱 SIERRA LEONEAN CONTEXT AI - API SERVER")
    print("=" * 80)
    print("\n🚀 Initializing AI system...")

    try:
        ai = get_ai()
        print(f"✅ Loaded {len(ai.vectorstores)} knowledge categories")
        print("✅ API server ready!")
        print("\n📝 API Documentation available at: http://localhost:8000/docs")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n👋 Shutting down Sierra Leonean Context AI API...")


# Run with: uvicorn api:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)