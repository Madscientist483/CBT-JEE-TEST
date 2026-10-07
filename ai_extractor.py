import json
import httpx
from config import settings

SYSTEM_PROMPT = """You are an expert JEE Main and JEE Advanced question setter.
Generate rigorous MCQs. Return only JSON with a top-level 'questions' array.
Each question must have exactly four options A-D, valid correct_answer values,
and a concise explanation. Never invent facts, units, constants, or answer choices.
"""

async def generate_questions(topic: str, subject: str, difficulty: str, count: int):
    prompt = f'''Generate exactly {count} JEE questions.
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Schema:
{{"questions":[{{"question_text":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},
"correct_answer":["A"],"explanation":"...","question_type":"single"}}]}}'''
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json=payload,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]

    data = json.loads(content)
    questions = data.get("questions", [])
    if len(questions) != count:
        raise ValueError(f"Expected {count} questions, got {len(questions)}")

    valid = []
    for q in questions:
        if set(q.get("options", {})) != {"A", "B", "C", "D"}:
            continue
        answers = q.get("correct_answer", [])
        if not answers or any(a not in {"A","B","C","D"} for a in answers):
            continue
        valid.append(q)
    if len(valid) != count:
        raise ValueError("Groq returned invalid question data")
    return valid
