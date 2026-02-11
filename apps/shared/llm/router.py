# import json
# import os
# import requests
# from pydantic import ValidationError

# from apps.shared.schemas import TaskExtractionSchema
# from apps.shared.llm.prompts import TASK_EXTRACTION_SYSTEM_PROMPT

# # Ollama local server
# OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# # Make sure this model EXISTS in `ollama list`
# OLLAMA_MODEL = "llama3.2"


# def extract_tasks(transcript: str) -> dict:
#     """
#     Extract structured tasks from a meeting transcript using local LLaMA (Ollama).
#     Returns a dict validated against TaskExtractionSchema.
#     """

#     if not transcript or not transcript.strip():
#         raise RuntimeError("Empty transcript received by LLM router")

#     prompt = f"""{TASK_EXTRACTION_SYSTEM_PROMPT}

# Transcript:
# \"\"\"
# {transcript}
# \"\"\"
# """

#     # Call Ollama via HTTP (NON-interactive, safe for workers)
#     response = requests.post(
#         OLLAMA_URL,
#         json={
#             "model": OLLAMA_MODEL,
#             "prompt": prompt,
#             "stream": False
#         },
#         timeout=120
#     )

#     response.raise_for_status()

#     # Ollama returns: { "response": "...", "done": true, ... }
#     raw_output = response.json().get("response", "").strip()

#     if not raw_output:
#         raise RuntimeError("LLM returned empty response")

#     # ---- DEBUG (leave this for now, very useful) ----
#     print("\n🧠 RAW LLM OUTPUT:\n", raw_output, "\n")

#     # Extract JSON block safely
#     start = raw_output.find("{")
#     end = raw_output.rfind("}") + 1

#     if start == -1 or end == -1:
#         raise RuntimeError(f"LLM did not return JSON:\n{raw_output}")

#     json_str = raw_output[start:end]

#     try:
#         data = json.loads(json_str)
#     except json.JSONDecodeError as e:
#         raise RuntimeError(f"Invalid JSON from LLM:\n{json_str}") from e

#     try:
#         validated = TaskExtractionSchema(**data)
#         for task in validated.tasks:
#             if not task.title:
#                 task.title = f"Task due {task.due_date or 'TBD'}"
#     except ValidationError as ve:
#         raise RuntimeError(
#             f"LLM returned JSON but structure is invalid:\n{data}\n\nError:\n{ve}"
#         )

#     return validated.model_dump()

import os
import requests
from apps.shared.schemas import TaskExtractionSchema
from apps.shared.llm.prompts import TASK_EXTRACTION_SYSTEM_PROMPT

OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://ollama:11434"
) + "/api/generate"

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def extract_tasks(transcript: str) -> dict:
    prompt = f"""
{TASK_EXTRACTION_SYSTEM_PROMPT}

Transcript:
{transcript}

Return ONLY valid JSON matching this schema:
{TaskExtractionSchema.model_json_schema()}
"""

    resp = requests.post(
        f"{OLLAMA_URL}",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    resp.raise_for_status()

    data = resp.json()

    # Ollama returns text in `response`
    raw_output = data.get("response", "").strip()

    # Extract JSON safely
    json_start = raw_output.find("{")
    json_end = raw_output.rfind("}") + 1
    json_str = raw_output[json_start:json_end]

    parsed = TaskExtractionSchema.model_validate_json(json_str)
    return parsed.model_dump()
