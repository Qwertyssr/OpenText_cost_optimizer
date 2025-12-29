import json
import jsonschema
import re
from llm_utils import call_llm

def clean_llm_json_output(raw_text: str) -> str:
    """
    Cleans common LLM artifacts to extract just the JSON string.
    """
    match = re.search(r"```(?:json)?(.*?)```", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def extract_project_profile(description_text: str) -> dict:
    """
    Use the LLM to parse the project description and output a structured profile JSON.
    """
    # UPDATED PROMPT: Specific instructions for the 'tech_stack' object structure
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
    
    raw = call_llm(prompt)
    cleaned_json_str = clean_llm_json_output(raw)

    try:
        profile = json.loads(cleaned_json_str)
        
        # Load schema and validate
        with open("schemas/project_profile_schema.json") as f:
            schema = json.load(f)
        jsonschema.validate(profile, schema)
        
        return profile

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Failed.\nRaw LLM Output:\n{raw}\n")
        raise e
    except jsonschema.ValidationError as e:
        # Improved error logging to see exactly what failed validation
        print(f"❌ Schema Validation Failed.\nLLM Output: {json.dumps(profile, indent=2)}\nError: {e.message}")
        raise e
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise e


