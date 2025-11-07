from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import os
import uuid

from .orchestrator import run_workflow
from .services.report import build_report

app = FastAPI(title="PharmaBridge Agentic Backend", version="0.1.0")

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


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await run_workflow(query=req.message, history=req.history or [])
    content = result.get("summary", "No response")
    agents_used = result.get("agents_used", [])

    report_id = None
    if result.get("report_data"):
        report_id = str(uuid.uuid4())
        pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports")
        os.makedirs(pdf_path, exist_ok=True)
        target = os.path.join(pdf_path, f"{report_id}.pdf")
        build_report(result["report_data"], target)

    return ChatResponse(content=content, agentsUsed=agents_used, report_id=report_id)


@app.get("/api/reports/{report_id}")
async def download_report(report_id: str):
    pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports", f"{report_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
