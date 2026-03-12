import os, sys
from abc import ABC, abstractmethod
from dotenv import load_dotenv

import json
import ollama
from openai import OpenAI

class LLMEngine:
    def __init__(self, model: str, stream: bool=False):
        self.model = model
        self.stream = stream

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OllamaLLMEngine(LLMEngine):
    def __init__(self, model: str="gpt-oss:20b", stream: bool=False):
        super().__init__(model, stream)
        # OPENAI_API_KEY environment variable require

    def generate(self, prompt: str) -> str:
        response = ollama.generate(self.model, prompt=prompt, stream=False)
        return response["response"]

load_dotenv(".env")
    
class OpenAILLMEngine(LLMEngine):
    def __init__(self, model: str="gpt-5-nano", stream: bool=False):
        super().__init__(model, stream)
        self.client = OpenAI()

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt)
