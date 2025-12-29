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

def generate_recommendations(profile: dict, analysis: dict) -> list:
    """
    Generate cost optimization recommendations via LLM.
    """
    project_name = profile.get("name", "Project")
    total_cost = analysis.get("total_monthly_cost", 0)
    budget = analysis.get("budget", 0)
    service_costs = analysis.get("service_costs", {})

    # Updated Prompt:
    # 1. Stricter JSON instructions.
    # 2. Reduced count to 3-5 to prevent token cut-off (incomplete JSON).
    prompt = (
        f"You are a Cloud Architect. Project '{project_name}' has a total monthly cost of {total_cost} INR "
        f"(Budget: {budget} INR). The costs by service are: {service_costs}.\n\n"
        f"Generate 3 to 5 actionable cost optimization recommendations.\n"
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

    # Use a higher token limit (3000) because recommendations are verbose
    raw = call_llm(prompt, max_tokens=3000)
    cleaned_json_str = clean_llm_json_output(raw)

    try:
        recs = json.loads(cleaned_json_str)
        
        # Load schema for validation
        with open("schemas/cost_report_schema.json") as f:
            full_schema = json.load(f)
            
        # Validate against the 'items' definition in your schema
        # (We validate the list 'recs', ensuring every item matches the recommendation schema)
        item_schema = full_schema["properties"]["recommendations"]["items"]
        jsonschema.validate(recs, {"type": "array", "items": item_schema})
        
        return recs

    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Failed in Recommendations.")
        print(f"Raw LLM Output:\n{raw}\n")
        raise e
    except jsonschema.ValidationError as e:
        print(f"❌ Schema Validation Failed for Recommendations.")
        print(f"Error: {e.message}")
        raise e
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise e