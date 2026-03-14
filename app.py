import os, sys
sys.path.append("pylib/")

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from qdrant_engine import QdrantEngine
from llm_engine import OllamaLLMEngine, OpenAILLMEngine, AnthropicLLMEngine

from snowflake_util import *

app = FastAPI()
qdrant = QdrantEngine(db_path="qdrant",
                      collection_name="chunks",
                      embedding_model="BAAI/bge-small-en-v1.5")

ollama_llm_engine = OllamaLLMEngine(model="gpt-oss:20b", stream=False)
openai_llm_engine = OpenAILLMEngine(model="gpt-5-nano", stream=False)
anthropic_llm_engine = AnthropicLLMEngine(model="claude-haiku-4-5", stream=False)

def chunk_format(chunk_info: dict) -> str:
    return f"[{chunk_info['source']}] {chunk_info['content']}"

class ChatRequest(BaseModel):
    model: str = "gpt-oss:20b"
    # "gpt-oss:20b", "gpt-5-nano", "calude-haiku-4-5"
    embed: str = "qdrant"
    # "qdrant", "snowflake"
    prompt: str

@app.post("/api/generate")
def generate(request: ChatRequest):
    if request.embed == "qdrant":
        domain_knowledge = qdrant.search(request.prompt, 10)
    elif request.embed == "snowflake":
        conn = get_connection()
        domain_knowledge = similarity_search(
            conn, request.prompt, 10)

    domain_knowledge = list(map(chunk_format, domain_knowledge))
    
    prompt = (
        "You are an LLM agent created to assist users.\n"
        "Actively utilize your prio knowledge to appropriately answer user queries.\n"
        "Given Domain Knowledge:\n"
    )

    prompt += '\n'.join(domain_knowledge)
    prompt += f"\nUser Query: {request.prompt}"

    if request.model == "gpt-oss:20b":
        text = ollama_llm_engine.generate(prompt)
    elif request.model == "gpt-5-nano":
        text = openai_llm_engine.generate(prompt)
    elif request.model == "claude-haiku-4-5":
        text = anthropic_llm_engine.generate(prompt)
    else:
        return {"response": f"{request.model} not supported"}

    return {"response": text}

# curl -X POST http://10.10.50.5:4444/api/generate -H "Content-Type: application/json" -d '{"model": "gpt-oss:20b", "embed": "qdrant","prompt": "hello"}'
