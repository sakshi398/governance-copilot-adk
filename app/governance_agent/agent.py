from google.adk.agents import Agent

from tools.mcp_tools import (
    get_metadata,
    quality_check,
    pii_check,
)

root_agent = Agent(
    name="GovernanceCopilot",

    model="gemini-2.5-flash",

    instruction="""
    You are a Data Governance Copilot.

    For:
    - analyze sample.csv
    - metadata analysis

    call get_metadata.

    For:
    - quality assessment
    - data quality

    call quality_check.

    The dataset already exists locally.
    Do not ask users to upload files.
    """,

    tools=[
        get_metadata,
        quality_check,
        pii_check,
    ]
)