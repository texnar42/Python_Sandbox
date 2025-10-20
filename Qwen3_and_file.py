import random

# import File
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime
import uuid
import time
from typing import Optional
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import StreamingResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi.responses import JSONResponse


app = FastAPI(title="Mock GPT-4-Turbo API")
Instrumentator().instrument(app).expose(app)

class ChatMessage(BaseModel):
    role: str  # "system", "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    file: UploadFile = File(...),
    prompt: str = Form(...)
    temperature: Optional[float] = 0.7



class ChatResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str


class ChatResponseUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatResponseChoice]
    usage: ChatResponseUsage


@app.post("/v1/chat/completions/file", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    try:
        contents = await file.read()
        return JSONResponse({
            "filename": file.filename,
            "size": len(contents),
            "prompt": prompt
        })
    except Exception as e:
        raise HTTPException(400, detail=f"File processing error: {str(e)}")




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)