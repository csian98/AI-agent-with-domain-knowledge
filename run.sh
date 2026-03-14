#!/bin/zsh
uv run -m uvicorn app:app --reload --host 0.0.0.0 --port 4444
