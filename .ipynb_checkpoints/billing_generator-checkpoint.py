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

def generate_synthetic_billing(profile: dict) -> list:
    """
    Generate synthetic cloud billing entries (JSON list) using the LLM.
    """
    project_name = profile.get("name", "Project")
    budget = profile.get("budget_inr_per_month", 5000)
    
    # Updated Prompt: Requesting fewer records (3-5) to ensure valid JSON syntax
    prompt = (
        f"Act as a cloud billing system. Generate a JSON array of 3 to 5 billing records for project '{project_name}'.\n"
        f"The total cost must sum up to approximately {budget} INR.\n\n"
        f"Each record object must have these exact fields:\n"
        f"- month (string, e.g., '2023-10')\n"
        f"- service (string, e.g., 'AWS EC2', 'S3')\n"
        f"- resource_id (string)\n"
        f"- region (string)\n"
        f"- usage_type (string)\n"
        f"- usage_quantity (number)\n"
        f"- unit (string)\n"
        f"- cost_inr (number)\n"
        f"- desc (string)\n\n"
        f"Response Requirements:\n"
        f"1. Output ONLY the JSON array.\n"
        f"2. Do NOT include markdown code blocks or conversational text."
    )
    
    # We pass the higher token limit here
    raw = call_llm(prompt, max_tokens=2500)
    cleaned_json_str = clean_llm_json_output(raw)

    try:
        billing = json.loads(cleaned_json_str)
        
        # Load schema and validate
        with open("schemas/billing_schema.json") as f:
            schema = json.load(f)
        jsonschema.validate(billing, schema)
        
        return billing

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Failed in Billing Generator.")
        print(f"Raw LLM Output:\n{raw}\n")
        raise e
    except jsonschema.ValidationError as e:
        print(f"❌ Schema Validation Failed for Billing Data.")
        print(f"Error: {e.message}")
        raise e
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise e
