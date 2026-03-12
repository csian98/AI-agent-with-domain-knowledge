import os, sys
sys.path.append("pylib/")

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from qdrant_engine import QdrantEngine
from llm_engine import OllamaLLMEngine, OpenAILLMEngine

app = FastAPI()
qdrant = QdrantEngine(db_path="qdrant",
                      collection_name="chunks",
                      embedding_model="BAAI/bge-small-en-v1.5")
llm_engine = OllamaLLMEngine(model="gpt-oss:20b", stream=False)

class ChatRequest(BaseModel):
    model: str = "gpt-oss:20b"
    prompt: str

@app.post("/api/generate")
def generate(request: ChatRequest):
    domain_knowledge = qdrant.search(request.prompt, 10)
    prompt = (
        "You are an LLM agent created to assist users.\n"
        "Actively utilize your prio knowledge to appropriately answer user queries.\n"
        "Given Domain Knowledge:\n"
    )

    prompt += '\n'.join(domain_knowledge)
    prompt += f"\nUser Query: {request.prompt}"

    text = llm_engine.generate(prompt)

    return {"response": text}

# curl -X POST http://127.0.0.1:8000/api/generate -H "Content-Type: application/json" -d '{"model": "gpt-oss:20b", "prompt": "hello"}'
