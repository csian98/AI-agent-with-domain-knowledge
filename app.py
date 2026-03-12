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



class ChatRequest(BaseModel):
    model: str = "gpt-oss:20b"
    prompt: str

@app.post("/api/generate")
def generate(request: ChatRequest):
    # RUN
