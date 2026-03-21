#!/bin/bash
# Railway uses the $PORT env var automatically
uvicorn vaas.main:app --host 0.0.0.0 --port ${PORT:-8000}
