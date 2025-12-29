import json
import jsonschema
import re
import time
from llm_utils import call_llm

def clean_llm_json_output(raw_text: str) -> str:
    """
    Cleans common LLM artifacts to extract just the JSON string.
    """
    match = re.search(r"```(?:json)?(.*?)```", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def extract_project_profile(description_text: str, attempts: int = 3) -> dict:
    """
    Use the LLM to parse the project description and output a structured profile JSON.
    Retries up to `attempts` times on parse/validation failures.
    """

    prompt = (
        f"You are a strict data extraction assistant. "
        f"Extract a JSON object from the text below with these exact fields:\n"
        f"1. name (string)\n"
        f"2. budget_inr_per_month (integer)\n"
        f"3. description (string)\n"
        f"4. tech_stack (OBJECT with keys: 'frontend', 'backend', 'database', 'proxy', 'hosting')\n"
        f"   - If a specific tech isn't mentioned, infer a standard open-source choice (e.g., Nginx for proxy).\n"
        f"5. non_functional_requirements (list of strings)\n\n"
        f"Input Text:\n{description_text}\n\n"
        f"Response Requirements:\n"
        f"1. Output ONLY valid JSON.\n"
        f"2. Do NOT include markdown formatting.\n"
    )

    last_exc = None
    for attempt in range(1, attempts + 1):
        raw = call_llm(prompt)
        cleaned_json_str = clean_llm_json_output(raw)

        try:
            profile = json.loads(cleaned_json_str)

            # Load schema and validate (keeps original behavior)
            with open("schemas/project_profile_schema.json") as f:
                schema = json.load(f)
            jsonschema.validate(profile, schema)

            return profile

        except json.JSONDecodeError as e:
            last_exc = e
            print(f"❌ JSON Parsing Failed (attempt {attempt}/{attempts}).")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:1500]}\n")
        except jsonschema.ValidationError as e:
            last_exc = e
            print(f"❌ Schema Validation Failed (attempt {attempt}/{attempts}).")
            print(f"LLM Output Parsed (truncated):\n{parsed_preview[:1500]}\n")
            print(f"Error: {e.message}")
        except Exception as e:
            last_exc = e
            print(f"❌ Unexpected Error (attempt {attempt}/{attempts}): {e}")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:1500]}\n")

        if attempt < attempts:
            wait = 0.8 * attempt
            print(f"Retrying in {wait:.1f}s...")
            time.sleep(wait)
        else:
            print("All profile-extraction attempts failed.")

    # If all attempts fail, raise the last exception
    raise last_exc
