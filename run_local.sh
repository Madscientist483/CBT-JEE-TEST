#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo 'Set DATABASE_URL and GROQ_API_KEY, then run: uvicorn backend.main:app --reload'
