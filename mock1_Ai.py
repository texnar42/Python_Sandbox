import logging

import app
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import time
import random
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import StreamingResponse


app = FastAPI(title="Mock LLM API Server")
Instrumentator().instrument(app).expose(app)

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    stream: bool = False


class ChatMessage(BaseModel):
    role: str
    content: str
    stream: bool = False


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    #max_tokens: int = 100
    #stream: bool = False
    model: str = "gpt-4-turbo"
    role: str
    content: str
    stream: bool = False
    temperature: float = 0.7

# In-memory "database" of generated responses
response_history: Dict[str, dict] = {}


def generate_mock_llm_response(prompt: str, is_chat: bool = False) -> str:
    """Generate a realistic mock LLM response"""
    responses = [
        f"I'm a mock LLM responding to: {prompt}",
        f"Here's a generated response about {prompt[:20]}...",
        "As an AI assistant, I can't provide real answers but this is a mock response.",
        "Mock response: The answer is 42.",
        f"Analysis of '{prompt}': [MOCK DATA]"
    ]

    return random.choice(responses)


@app.post("/v1/completions/prompt")
async def create_completion(request: CompletionRequest):
    """Mock OpenAI completion endpoint"""
    response_id = f"cmpl-{random.randint(1000, 9999)}"
    response_text = generate_mock_llm_response(request.prompt)
    time.sleep(10.1) # - время отклика
    if request.stream:
        # Simulate streaming response
        def generate():
            for word in response_text.split():
                yield f"data: {{\"id\": \"{response_id}\", \"choices\": [{{\"text\": \"{word} \", \"index\": 0}}]}}\n\n"
            yield "data: [DONE]\n\n"

        return generate()

    response = {
        "id": response_id,
        "object": "text_completion",
        "created": int(time.time()),
        "model": "text-davinci-003",
        "choices": [{
            "text": response_text,
            "index": 0,
            "logprobs": None,
            "finish_reason": "length"
        }],
        "usage": {
            "prompt_tokens": len(request.prompt.split()),
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(request.prompt.split()) + len(response_text.split())
        }
    }
    response_history[response_id] = response
    return response

@app.post("/v1/chat/completions/message1")
async def create_chat_completion(request: ChatMessage):
    """Mock OpenAI chat endpoint"""
    response_id = f"chatcmpl-{random.randint(1000, 9999)}"
    last_message = request.messages[-1].content
    response_text = generate_mock_llm_response(last_message, is_chat=True)

    if request.stream:
        # Simulate streaming chat response
        def generate():
            for word in response_text.split():
                yield f"data: {{\"id\": \"{response_id}\", \"choices\": [{{\"delta\": {{\"content\": \"{word} \"}}, \"index\": 0}}]}}\n\n"
            yield "data: [DONE]\n\n"

        return generate()

    response = {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "message": {
                "role": "assistant",
                "content": response_text
            },
            "index": 0,
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
            "completion_tokens": len(response_text.split()),
            "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(response_text.split())
        }
    }
    response_history[response_id] = response
    return response

@app.post("/v1/chat/completions/message")
async def create_chat_completion(request: ChatRequest):
    """Mock OpenAI chat endpoint"""
    # response_id = f"chatcmpl-{random.randint(1000, 9999)}"
    last_message = request.messages[-1].content
    response_text = generate_mock_llm_response(last_message, is_chat=True)
print("!!!!")
    # if request.stream:
    #     # Simulate streaming chat response
    #     def generate():
    #         for word in response_text.split():
    #             yield f"data: {{\"id\": \"{response_id}\", \"choices\": [{{\"delta\": {{\"content\": \"{word} \"}}, \"index\": 0}}]}}\n\n"
    #         yield "data: [DONE]\n\n"
    #
    #     # return generate()
    # return StreamingResponse(generate(), media_type="text/event-stream")

    # response = {
    #     "id": response_id,
    #     "object": "chat.completion",
    #     "created": int(time.time()),
    #     "model": request.model,
    #     "choices": [{
    #         "message": {
    #             "role": "assistant",
    #             "content": response_text
    #         },
    #         "index": 0,
    #         "finish_reason": "stop"
    #     }],
    #     "usage": {
    #         "prompt_tokens": sum(len(m.content.split()) for m in request.messages),
    #         "completion_tokens": len(response_text.split()),
    #         "total_tokens": sum(len(m.content.split()) for m in request.messages) + len(response_text.split())
    #     }
    # }
    # response_history[response_id] = response
    # return response


@app.get("/v1/responses/{response_id}")
async def get_response(response_id: str):
    """Retrieve a stored response"""
    if response_id not in response_history:
        raise HTTPException(status_code=404, detail="Response not found")
    return response_history[response_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)