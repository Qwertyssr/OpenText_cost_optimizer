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

def generate_recommendations(profile: dict, analysis: dict, attempts: int = 3) -> list:
    """
    Generate cost optimization recommendations via LLM.
    Retries up to `attempts` times on parse/validation failures.
    """

    project_name = profile.get("name", "Project")
    total_cost = analysis.get("total_monthly_cost", 0)
    budget = analysis.get("budget", 0)
    service_costs = analysis.get("service_costs", {})

    prompt = (
        f"You are a Cloud Architect. Project '{project_name}' has a total monthly cost of {total_cost} INR "
        f"(Budget: {budget} INR). The costs by service are: {service_costs}.\n\n"
        f"Generate 6 to 10 actionable cost optimization recommendations.\n"
        f"Consider multi-cloud (AWS, Azure, GCP), open-source alternatives, and free tiers.\n\n"
        f"Output MUST be a JSON array where each object has these exact fields:\n"
        f"- title (string)\n"
        f"- service (string)\n"
        f"- current_cost (number)\n"
        f"- potential_savings (number)\n"
        f"- recommendation_type (string, e.g., 'Rightsizing', 'Spot Instances')\n"
        f"- description (string)\n"
        f"- implementation_effort (string: 'Low', 'Medium', 'High')\n"
        f"- risk_level (string: 'Low', 'Medium', 'High')\n"
        f"- steps (list of strings)\n"
        f"- cloud_providers (list of strings)\n\n"
        f"Response Requirements:\n"
        f"1. Output ONLY the JSON array.\n"
        f"2. Do NOT include markdown code blocks or intro text."
    )

    last_exc = None
    for attempt in range(1, attempts + 1):
        raw = call_llm(prompt, max_tokens=3500)
        cleaned_json_str = clean_llm_json_output(raw)

        try:
            recs = json.loads(cleaned_json_str)
            
            # Load schema for validation 
            with open("schemas/cost_report_schema.json") as f:
                full_schema = json.load(f)
                
            # Validate against the 'items' definition in your schema
            item_schema = full_schema["properties"]["recommendations"]["items"]
            jsonschema.validate(recs, {"type": "array", "items": item_schema})
            
            return recs

        except json.JSONDecodeError as e:
            last_exc = e
            print(f"❌ JSON Parsing Failed in Recommendations (attempt {attempt}/{attempts}).")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:2000]}\n")
        except jsonschema.ValidationError as e:
            last_exc = e
            print(f"❌ Schema Validation Failed for Recommendations (attempt {attempt}/{attempts}).")
            print(f"Error: {e.message}")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:2000]}\n")
        except Exception as e:
            last_exc = e
            print(f"❌ Unexpected Error (attempt {attempt}/{attempts}): {e}")
            print(f"Raw LLM Output (truncated):\n{(raw or '')[:2000]}\n")

        if attempt < attempts:
            wait = 0.8 * attempt
            print(f"Retrying in {wait:.1f}s...")
            time.sleep(wait)
        else:
            print("All recommendation-generation attempts failed.")

    # If all attempts fail, raise the last exception
    raise last_exc
