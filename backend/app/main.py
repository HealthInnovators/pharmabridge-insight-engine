from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import random
import logging
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Rest of your imports...
from .services.llm import generate_chat_response, llm_provider_name
from .orchestrator import run_workflow
from .services.report import build_report

app = FastAPI(title="PharmaBridge Agentic Backend", version="0.1.0")

logger = logging.getLogger(__name__)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    content: str
    agentsUsed: List[str]
    report_id: Optional[str] = None
    report_data: Optional[Dict[str, Any]] = None
    llm_provider: Optional[str] = None

@app.get("/debug/env")
async def debug_env():
    return {
        "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
        "PUBMED_TIMEOUT_S": os.getenv("PUBMED_TIMEOUT_S"),
        "CTGOV_TIMEOUT_S": os.getenv("CTGOV_TIMEOUT_S"),
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    await asyncio.sleep(0.5 + random.random())
    result = await run_workflow(query=req.message, history=req.history or [])

    response_length = len(str(result))
    base_delay = min(3.0, 0.5 + (response_length / 1000) * 0.5)
    jitter = random.uniform(-0.3, 0.3)
    delay = max(0.2, base_delay + jitter)
    
    if result:
        await asyncio.sleep(delay)

    fallback_content = result.get("summary", "No response")
    agents_used = result.get("agents_used", [])
    report_data = result.get("report_data", {})

    content = await generate_chat_response(
        query=req.message,
        history=[m.model_dump() for m in (req.history or [])],
        report_data=report_data if isinstance(report_data, dict) else {},
        fallback_text=fallback_content,
    )

    report_id = None
    if report_data:
        report_id = str(uuid.uuid4())
        pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports")
        os.makedirs(pdf_path, exist_ok=True)
        target = os.path.join(pdf_path, f"{report_id}.pdf")

        build_report(report_data, target)

        if not os.path.exists(target):
            logger.warning("Report build did not create expected PDF at %s", target)

    return ChatResponse(
        content=content,
        agentsUsed=agents_used,
        report_id=report_id,
        report_data=report_data if isinstance(report_data, dict) else None,
        llm_provider=llm_provider_name(),
    )


@app.get("/api/reports/{report_id}")
async def download_report(report_id: str):
    pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports", f"{report_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
