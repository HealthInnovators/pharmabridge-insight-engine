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


import asyncio
import random

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
    content = result.get("summary", "No response")
    agents_used = result.get("agents_used", [])
    report_data = result.get("report_data", {})

    print(f"Report data keys: {report_data.keys() if isinstance(report_data, dict) else 'Not a dict'}")
    if isinstance(report_data, dict):
        for key, value in report_data.items():
            if isinstance(value, (list, dict)):
                print(f"- {key}: {len(value) if hasattr(value, '__len__') else 'N/A'} items")
            else:
                print(f"- {key}: {value}")

    report_id = None
    if report_data:
        report_id = str(uuid.uuid4())
        pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports")
        os.makedirs(pdf_path, exist_ok=True)
        target = os.path.join(pdf_path, f"{report_id}.pdf")
        
        # Debug: Print the target path
        print(f"Generating report at: {target}")
        
        build_report(report_data, target)
        
        if os.path.exists(target):
            print(f"Successfully generated report at: {target}")
        else:
            print(f"Failed to generate report at: {target}")
        
        result["report_data"] = report_data

    return ChatResponse(content=content, agentsUsed=agents_used, report_id=report_id)


@app.get("/api/reports/{report_id}")
async def download_report(report_id: str):
    pdf_path = os.path.join(os.path.dirname(__file__), "storage", "reports", f"{report_id}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
