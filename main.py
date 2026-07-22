from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import NewsRequest,NewsResponse,ErrorResponse
from agents import process_news_async
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

app=FastAPI(
    title='News Bot API',
    description='AI-powered news aggregation and WhatsApp notification system',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return {
        'message':'Welcome to news bot API',
        'endpoints':{
            "post_news": "/api/news",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        # "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/news",response_model=NewsResponse)
async def get_news(request:NewsRequest):

    try:
        logger.info(f"Processing news request for topic: {request.topic}")

        result=await process_news_async(
            topic=request.topic,
            send_whatsapp=request.send_whatsapp
        )
        
        return NewsResponse(
            success=True,
            topic=request.topic,
            news_text=result,  # Direct LLM formatted output
            whatsapp_sent=request.send_whatsapp,
            # processing_time=round(processing_time, 2),
            # message=f"Successfully processed news in {processing_time:.2f}s"
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing news: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process news: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="Request Error",
            detail=str(exc.detail)
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="Something went wrong. Please try again later."
        ).model_dump()
    )
