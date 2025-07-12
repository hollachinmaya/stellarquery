import os
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
assert API_KEY, "⚠️ OPENROUTER_API_KEY is missing from .env"


def classify_question(nl: str, history: list) -> str:
    """
    Classify a user query into one of:
    SQL, GAIA, IMAGE, GENERAL, or INVALID.
    Uses history for context but focuses on latest user message.
    """
    # Append current user query to history
    full_history = history + [{"role": "user", "content": nl}]

    # Add explicit classification instruction
    classification_prompt = """
You are a classifier for astronomy-related queries.

Classify ONLY the MOST RECENT user message into one of these types:
- SQL: NASA Exoplanet Archive queries (e.g., discovery year, planet radius).
- GAIA: Gaia DR3 catalog queries (e.g., star brightness, ADQL queries).
- IMAGE: Image requests (e.g., pictures of Mars, galaxies, planets).
- GENERAL: Astronomy Q&A (e.g., What is a pulsar?).
- INVALID: Anything not astronomy-related.

⚠️ Use the previous conversation for context if needed, 
but focus on the LAST user message.

Respond with EXACTLY one word: SQL, GAIA, IMAGE, GENERAL, or INVALID.
No explanations.
"""

    # Append classification prompt
    full_history.append({"role": "user", "content": classification_prompt})

    # Call LLM API
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "temperature": 0,  # 🔥 deterministic
            "max_tokens": 5,
            "messages": full_history
        },
        timeout=30
    )
    response.raise_for_status()
    result = response.json()["choices"][0]["message"]["content"].strip().upper().replace(".", "")

    print("📥 Classification result:", result)

    # Validate result
    if result not in {"SQL", "GAIA", "IMAGE", "GENERAL", "INVALID"}:
        raise ValueError(f"Unexpected classification: {result}")

    # Save LLM response to history
    history.append({"role": "assistant", "content": result})
    return result


# ✅ Convert natural language to SQL for NASA Exoplanet Archive
def get_sql(nl: str, history: list) -> str:
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
- If the user asks for a specific number of results (e.g., 'list 5 ...'), add LIMIT N at the end.

Example 1:
Input: List planets discovered after 2018 using transit
Output: SELECT pl_name FROM ps WHERE disc_year > 2018 AND discoverymethod = 'Transit'

Example 2:
Input: List 5 exoplanets discovered in 2020
Output: SELECT pl_name FROM ps WHERE disc_year = 2020 LIMIT 5

Convert:
"{nl}"
"""

    conversation = history + [{"role": "user", "content": prompt}]
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 150,
            "messages": conversation
        },
        timeout=30
    )
    response.raise_for_status()
    raw_output = response.json()["choices"][0]["message"]["content"].strip()

    # Clean up
    sql = raw_output.splitlines()[0].strip()
    if ";" in sql:
        sql = sql.split(";")[0].strip()

    if not sql.lower().startswith("select") or "from ps" not in sql.lower():
        raise ValueError(f"Invalid SQL from Claude: {sql}")

    history.append({"role": "assistant", "content": sql})
    return sql


# ✅ Convert natural language to ADQL for Gaia TAP+
def get_adql(nl: str, history: list) -> str:
    prompt = f"""
You are an ADQL assistant for the ESA Gaia Archive (main table: gaiadr3.gaia_source).

Use ONLY these fields:
- source_id
- ra
- dec
- parallax
- pmra
- pmdec
- phot_g_mean_mag
- bp_rp

Rules:
- Output ONLY valid ADQL.
- No explanations, no markdown, no extra words.
- Use correct column names.
- Must start with SELECT and use FROM gaiadr3.gaia_source.

Example:
Input: List stars brighter than magnitude 10 within 5 degrees of RA=120, DEC=22
Output: SELECT source_id, ra, dec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE phot_g_mean_mag < 10 AND 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', 120.0, 22.0, 5.0))

Convert:
"{nl}"
"""
    conversation = history + [{"role": "user", "content": prompt}]
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 200,
            "messages": conversation
        },
        timeout=30
    )
    response.raise_for_status()
    raw_output = response.json()["choices"][0]["message"]["content"].strip()

    # Clean up
    adql = raw_output.splitlines()[0].strip()
    if ";" in adql:
        adql = adql.split(";")[0].strip()

    if not adql.lower().startswith("select") or "from gaiadr3.gaia_source" not in adql.lower():
        raise ValueError(f"Invalid ADQL from Claude: {adql}")

    history.append({"role": "assistant", "content": adql})
    return adql


# ✅ General explanation logic for astronomy Q&A
def answer_general(nl: str, history: list) -> str:
    prompt = f"""
You're a helpful astronomy tutor. Answer clearly for beginners:

"{nl}"
"""
    conversation = history + [{"role": "user", "content": prompt}]
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "anthropic/claude-3-sonnet",
            "max_tokens": 300,
            "messages": conversation
        },
        timeout=30
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"].strip()
    history.append({"role": "assistant", "content": answer})
    return answer
