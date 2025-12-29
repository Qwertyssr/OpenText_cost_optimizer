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

def generate_synthetic_billing(profile: dict, attempts: int = 3) -> list:
    """
    Generate synthetic cloud billing entries (JSON list) using the LLM.
    Retries up to `attempts` times on parse/validation failures.
    """

    project_name = profile.get("name", "Project")
    budget = profile.get("budget_inr_per_month", 5000)
    
    prompt = (
        f"Act as a cloud billing system. Generate a JSON array of 12 to 20 billing records for project '{project_name}'.\n"
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

    last_exc = None
    for attempt in range(1, attempts + 1):
        raw = call_llm(prompt, max_tokens=3500)
        cleaned_json_str = clean_llm_json_output(raw)

        try:
            billing = json.loads(cleaned_json_str)
            
            # Load schema and validate
            try:
                with open("schemas/billing_schema.json") as f:
                    schema = json.load(f)
                jsonschema.validate(billing, schema)
            except FileNotFoundError:
                # If schema missing, proceed without validation 
                pass

            return billing

        except json.JSONDecodeError as e:
            last_exc = e
            print(f"❌ JSON Parsing Failed in Billing Generator (attempt {attempt}/{attempts}).")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:1500]}\n")
        except jsonschema.ValidationError as e:
            last_exc = e
            print(f"❌ Schema Validation Failed for Billing Data (attempt {attempt}/{attempts}).")
            print(f"Validation error: {e.message}")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:1500]}\n")
        except Exception as e:
            last_exc = e
            print(f"❌ Unexpected Error (attempt {attempt}/{attempts}): {e}")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:1500]}\n")

        if attempt < attempts:
            wait = 0.8 * attempt
            print(f"Retrying in {wait:.1f}s...")
            time.sleep(wait)
        else:
            print("All billing-generation attempts failed.")

    # If all attempts fail, raise the last exception
    raise last_exc
