import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
assert API_KEY, "⚠️ OPENROUTER_API_KEY is missing from .env"

#  Classify question as SQL, IMAGE, GENERAL, or INVALID
def classify_question(nl: str) -> str:
    prompt = f"""
Classify the question into one of: SQL, IMAGE, GENERAL, or INVALID.

SQL = exoplanet archive queries (e.g. discovery year, radius).
IMAGE = requests for images of planets/stars (e.g. Mars, Saturn).
GENERAL = space knowledge questions (e.g. What is a pulsar?).
INVALID = not astronomy related.

Question: "{nl}"
Respond with exactly one word only.
"""
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 5,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip().upper().replace(".", "")

#  Convert question to clean SQL query
def get_sql(nl: str) -> str:
    prompt = f"""
You are a SQL assistant for NASA's Exoplanet Archive (table: ps).

Use ONLY these fields:
- pl_name
- disc_year
- pl_rade
- pl_bmasse
- discoverymethod

Rules:
- Output ONLY valid SQL.
- No explanations, no markdown, no extra words.
- Use correct column names.
- Must start with SELECT and use FROM ps.

Example:
Input: List planets discovered after 2018 using transit
Output: SELECT pl_name FROM ps WHERE disc_year > 2018 AND discoverymethod = 'Transit'

Convert:
"{nl}"
"""
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )
    r.raise_for_status()
    raw_output = r.json()["choices"][0]["message"]["content"].strip()

    #  Clean Claude's output
    sql = raw_output.splitlines()[0].strip()
    if ";" in sql:
        sql = sql.split(";")[0].strip()

    if not sql.lower().startswith("select") or "from ps" not in sql.lower():
        raise ValueError(f" Invalid SQL from Claude: {sql}")

    return sql

#  General explanation logic for astronomy Q&A
def answer_general(nl: str) -> str:
    prompt = f"""
You're a helpful astronomy tutor. Answer clearly for beginners:

"{nl}"
"""
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()
