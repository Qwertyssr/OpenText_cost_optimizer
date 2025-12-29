# cost_optimizer.py

import json
import sys
from project_profile import extract_project_profile
from billing_generator import generate_synthetic_billing
from analysis import analyze_costs
from recommendations import generate_recommendations

def main_menu():
    print("=== AI-Powered Cloud Cost Optimizer ===")
    print("1. Enter new project description")
    print("2. Run Complete Cost Analysis")
    print("3. View Recommendations")
    print("4. Export Report")
    print("0. Exit")
    choice = input("Select an option: ")
    return choice

while True:
    choice = main_menu()
    if choice == "1":
        print("Enter project description (finish with an empty line):")
        lines = []
        while True:
            line = input()
            if not line.strip(): break
            lines.append(line)
        desc = "\n".join(lines).strip()
        if not desc:
            print("No description entered.")
        else:
            with open("data/project_description.txt", "w") as f:
                f.write(desc)
            print("Project description saved.")
    elif choice == "2":
        try:
            desc = open("data/project_description.txt").read()
        except FileNotFoundError:
            print("Error: 'project_description.txt' not found. Please enter a description first.")
            continue
        print("Extracting project profile...")
        profile = extract_project_profile(desc)
        with open("data/project_profile.json","w") as f:
            json.dump(profile, f, indent=2)
        print("Profile saved as project_profile.json.")

        print("Generating synthetic billing...")
        billing = generate_synthetic_billing(profile)
        with open("data/mock_billing.json","w") as f:
            json.dump(billing, f, indent=2)
        print("Billing data saved as mock_billing.json.")

        print("Analyzing costs...")
        analysis = analyze_costs(profile, billing)
        project_name = profile["name"]
        report = {
            "project_name": project_name,
            "analysis": analysis,
            "is_over_budget": analysis["is_over_budget"],
            "recommendations": []
        }

        print("Generating recommendations...")
        recs = generate_recommendations(profile, analysis)
        report["recommendations"] = recs
        # Compute summary fields
        total_savings = sum(rec["potential_savings"] for rec in recs)
        report["total_potential_savings"] = total_savings
        report["savings_percentage"] = round((total_savings / analysis["total_monthly_cost"] * 100), 2) if analysis["total_monthly_cost"] else 0
        report["recommendations_count"] = len(recs)

        with open("data/cost_optimization_report.json","w") as f:
            json.dump(report, f, indent=2)
        print("Cost optimization report saved as cost_optimization_report.json.")
    elif choice == "3":
        # View recommendations from the report
        try:
            report = json.load(open("data/cost_optimization_report.json"))
        except Exception:
            print("No report found. Run analysis first.")
            continue
        recs = report.get("recommendations", [])
        if not recs:
            print("No recommendations available.")
        else:
            print("\nCost Optimization Recommendations:")
            for i, rec in enumerate(recs, start=1):
                print(f"{i}. {rec['title']} (Type: {rec['recommendation_type']}, Savings: ₹{rec['potential_savings']})")
            print()
    elif choice == "4":
        # Export report as JSON (and optionally HTML)
        try:
            report = json.load(open("data/cost_optimization_report.json"))
        except Exception:
            print("No report to export.")
            continue
        # Already in JSON; can mention this file
        print("Report is available in 'data/cost_optimization_report.json'.")
        # Optional HTML export:
        html_content = f"<html><body><pre>{json.dumps(report, indent=2)}</pre></body></html>"
        with open("data/cost_report.html","w") as f:
            f.write(html_content)
        print("HTML report saved as 'data/cost_report.html'.")
    elif choice == "0":
        print("Exiting.")
        break
    else:
        print("Invalid choice. Please select 1-4 or 0.")
