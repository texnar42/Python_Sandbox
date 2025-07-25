from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import time
from typing import Optional

app = FastAPI(title="Mock GPT-4-Turbo API")


class ChatMessage(BaseModel):
    role: str  # "system", "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    model: str = "gpt-4-turbo"
    messages: list[ChatMessage]
    max_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False


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


def generate_mock_response(request: ChatRequest):
    """Генерирует mock-ответ, похожий на ответ GPT-4-turbo"""
    last_message = request.messages[-1]

    # Генерируем ответ на основе последнего сообщения пользователя
    assistant_response = f"Это mock-ответ на ваше сообщение: '{last_message.content}'. " \
                         f"Параметры запроса: temperature={request.temperature}, " \
                         f"max_tokens={request.max_tokens}."

    # Создаем структуру ответа
    return ChatResponse(
        id=f"chatcmpl-{uuid.uuid4()}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatResponseChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=assistant_response
                ),
                finish_reason="stop"
            )
        ],
        usage=ChatResponseUsage(
            prompt_tokens=sum(len(m.content) for m in request.messages) // 4,
            completion_tokens=len(assistant_response) // 4,
            total_tokens=(sum(len(m.content) for m in request.messages) + len(assistant_response)) // 4
        )
    )


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Эндпоинт, имитирующий /v1/chat/completions OpenAI"""
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty")

    if request.model != "gpt-4-turbo":
        raise HTTPException(status_code=400,
                            detail=f"Model {request.model} is not supported. Only gpt-4-turbo is available")

    return generate_mock_response(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)