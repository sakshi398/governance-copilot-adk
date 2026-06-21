from google.adk.agents import Agent
from tools.dataset_tools import get_metadata
root_agent = Agent(
    name="GovernanceCopilot",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a Data Governance Copilot.

    Help users:
    - Analyze datasets
    - Identify PII
    - Assess data quality
    - Generate governance recommendations
    If anyone asks you to analyse sample.csv please get_metadata tool
    """,
    tools=[get_metadata]
)