# analysis.py

import json

def analyze_costs(profile: dict, billing: list) -> dict:
    """
    Compute cost analysis given profile and billing data.
    Returns a dict with total cost, breakdown, variance, etc.
    """
    budget = profile["budget_inr_per_month"]
    total_cost = sum(item["cost_inr"] for item in billing)
    service_costs = {}
    for item in billing:
        service = item["service"]
        service_costs[service] = service_costs.get(service, 0) + item["cost_inr"]
    # Identify highest-cost service(s)
    if service_costs:
        max_cost = max(service_costs.values())
        high_cost_services = {s: c for s, c in service_costs.items() if c == max_cost}
    else:
        high_cost_services = {}
    analysis = {
        "total_monthly_cost": total_cost,
        "budget": budget,
        "budget_variance": total_cost - budget,
        "service_costs": service_costs,
        "high_cost_services": high_cost_services
    }
    analysis["is_over_budget"] = total_cost > budget
    return analysis

# Example usage:
# profile = json.load(open("data/project_profile.json"))
# billing = json.load(open("data/mock_billing.json"))
# analysis = analyze_costs(profile, billing)
# Then integrate 'analysis' into the final report JSON.
