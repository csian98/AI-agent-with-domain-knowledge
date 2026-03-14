<!--
	***
	*   README.md
	*
	*	Author: Jeong Hoon (Sian) Choi
	*	License: MIT
	*
	***
-->

<a name="readme-top"></a>

<br/>
<div align="center">
	<h3 align="center">AI Agent with Domain Knowledge</h3>	
	<p align="center">
		A Retrieval-Augmented Generation (RAG) system that integrates domain-specific knowledge with multiple LLM providers for accurate, context-aware AI responses.
	</p>
	<br/>
	<a href="https://github.com/csian98/ai-agent-with-domain-knowledge">
		<strong>Explore the docs »</strong>
	</a>
	<br/>
	<br/>
	<a href="https://github.com/csian98/ai-agent-with-domain-knowledge/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
	·
	<a href="https://github.com/csian98/ai-agent-with-domain-knowledge/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
</div>

---

## Table of Contents

- [About the Project](#about-the-project)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)

---

## About the Project

**AI Agent with Domain Knowledge** is a RAG (Retrieval-Augmented Generation) system designed to leverage domain-specific knowledge for answering user queries. The system combines:

- **Multiple LLM Engines**: Support for OpenAI API, Anthropic Claude, and local Ollama models
- **Vector Embeddings**: Real-time vector embedding and semantic search capabilities
- **Flexible Storage**: Both cloud-based (Snowflake) and local (Qdrant) vector database options
- **Document Processing**: Automatic PDF conversion and chunk-based indexing
- **Web Interface**: React-based frontend for intuitive user interactions

The system retrieves relevant domain knowledge chunks and uses them to provide LLM agents with contextual information, resulting in more accurate and domain-aware responses.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                  (React/Vite Frontend)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│  /api/generate  │  /api/upload                              │
└────┬────────────┼───────────┬──────────────────────────────┘
     │            │           │
     ▼            ▼           ▼
┌──────────┐ ┌──────────┐ ┌─────────────┐
│   LLM    │ │ PDF to   │ │  Embedding  │
│ Engines  │ │ Text     │ │  & Upload   │
└──────────┘ └──────────┘ └─────────────┘
     │            │           │
     └────────────┴───────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
┌─────────┐  ┌──────────────┐
│ Qdrant  │  │  Snowflake   │
│ (Local) │  │  (Cloud)     │
└─────────┘  └──────────────┘
```

---

## Prerequisites

- **Python 3.9+**
- **Node.js 18+** (for frontend development)
- **uv** package manager (for Python)
- **API Keys**: OpenAI or Anthropic (depending on chosen LLM)
- Optional: **Ollama** installed locally (for local model support)

---

## Installation

### 1. Install Python Dependencies

```bash
uv pip install -r requirements.txt
```

Key dependencies include:
- **FastAPI**: Web framework
- **Qdrant Client**: Local vector DB
- **FastEmbed**: Embedding model
- **OpenAI**: GPT API client
- **Anthropic**: Claude API client
- **Ollama**: Local LLM support
- **Snowflake Connector**: Cloud storage
- **LangChain Text Splitters**: Document chunking

### 2. Set Up Frontend

```bash
cd frontend/vite-project
npm install
cd ../..
```

### 3.. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Snowflake Configuration (Optional)
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Configuration

### LLM Model Selection

In [app.py](app.py), configure which LLM engines to use:

```python
# Currently active engines:
openai_llm_engine = OpenAILLMEngine(model="gpt-5-nano", stream=False)
anthropic_llm_engine = AnthropicLLMEngine(model="claude-haiku-4-5", stream=False)

# To enable Ollama (uncomment):
# ollama_llm_engine = OllamaLLMEngine(model="gpt-oss:20b", stream=False)
```

### Vector Embedding Configuration

The Qdrant engine is initialized with:
- **Database Path**: `qdrant/` (local directory)
- **Collection Name**: `chunks`
- **Embedding Model**: `BAAI/bge-small-en-v1.5` (small, fast, accurate)

### Document Chunking Settings

In [pylib/embedding.py](pylib/embedding.py):
```python
CHUNK_SIZE = 500           # Characters per chunk
CHUNK_OVERLAP = 50         # Overlap between chunks
BATCH_SIZE = 20            # Batch processing size
```

---

## Usage

#### Option 1: Using the Run Script

```bash
./run.sh
```

- This command starts the FastAPI backend on `http://0.0.0.0:4444`

#### Option 2: Manual Command

```bash
uv run -m uvicorn app:app --reload --host 0.0.0.0 --port 4444
```

#### Option 3: Run Frontend in Development

In a separate terminal:

```bash
cd frontend/vite-project
npm run dev
```

The frontend will typically start on `http://localhost:5173`

---

## 🔐 License

Copyright © 2026, All rights reserved. Distributed under the MIT License.
See `LICENSE` for more information.

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
