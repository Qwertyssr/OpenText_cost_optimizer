Setup and Usage Instructions (README)
Requirements:
Python 3.10+
Install dependencies: pip install huggingface_hub python-dotenv jsonschema
Hugging Face API Key:
Create a .env file in the project root (add .env to .gitignore) with:
HF_API_TOKEN=<your_huggingface_api_token>
for obtaining an API token
huggingface.co
.
JSON Schemas:
The schemas/ directory contains the JSON Schema files used for validation.

Running the CLI:
Run python cost_optimizer.py.
Follow the menu prompts (enter description, run analysis, etc.).

Example: 


$ python cost_optimizer.py

=== AI-Powered Cloud Cost Optimizer ===
1. Enter new project description
2. Run Complete Cost Analysis
3. View Recommendations
4. Export Report
0. Exit
Select an option: 1

Enter project description (finish with an empty line):
Hi, I want to build a market analysis tool for e-commerce. ...
<blank line>
Project description saved.

=== AI-Powered Cloud Cost Optimizer ===
...
Select an option: 2
Extracting project profile...
Profile saved as project_profile.json.
Generating synthetic billing...
Billing data saved as mock_billing.json.
Analyzing costs...
Generating recommendations...
Cost optimization report saved as cost_optimization_report.json.

=== AI-Powered Cloud Cost Optimizer ===
...
Select an option: 3

Cost Optimization Recommendations:
1. Migrate MongoDB to Open-Source MongoDB (Type: open_source, Savings: ₹450)
2. Utilize AWS Free Tier for EC2 (Type: free_tier, Savings: ₹825)
...

=== AI-Powered Cloud Cost Optimizer ===
...
Select an option: 4
Report is available in 'data/cost_optimization_report.json'.
HTML report saved as 'data/cost_report.html'.




Example Flow:
Paste your project description.
Run the full pipeline to generate:
project_profile.json
mock_billing.json
cost_optimization_report.json
View a summary of savings and recommendations.
Export the final report (HTML + JSON).

Output Files:
project_profile.json: structured budget, tech stack, and requirements
mock_billing.json: ~15 realistic cloud usage entries
cost_optimization_report.json: total cost, savings, suggestions
