#!/usr/bin/env python3
"""
Simple test harness to simulate ADK agent prompts and invoke MCP-backed tools.

Usage:
  python3 app/scripts/test_agent.py "show metadata"
  python3 app/scripts/test_agent.py --interactive

This script maps simple natural-language prompts to the underlying tools:
  - metadata -> get_metadata
  - quality  -> quality_check
  - pii      -> pii_check
  - all      -> runs all three and prints combined output
"""
import sys
import json
from typing import Any

sys.path.insert(0, "/workspaces/governance-copilot-adk")
from app.tools import mcp_tools


def _unwrap(result: Any):
    # CallToolResult has .data or .structured_content; show whichever exists
    if hasattr(result, "data") and result.data is not None:
        return result.data
    if hasattr(result, "structured_content") and result.structured_content is not None:
        return result.structured_content
    return result


def run_prompt(prompt: str):
    p = prompt.lower()
    if "metadata" in p or "rows" in p or "columns" in p:
        res = mcp_tools.get_metadata()
        print(json.dumps(_unwrap(res), indent=2))
    elif "quality" in p or "missing" in p or "duplicates" in p:
        res = mcp_tools.quality_check()
        print(json.dumps(_unwrap(res), indent=2))
    elif "pii" in p or "email" in p or "phone" in p:
        res = mcp_tools.pii_check()
        print(json.dumps(_unwrap(res), indent=2))
    elif "all" in p or ("analyze" in p and "sample" in p):
        print("--- METADATA ---")
        print(json.dumps(_unwrap(mcp_tools.get_metadata()), indent=2))
        print("\n--- QUALITY ---")
        print(json.dumps(_unwrap(mcp_tools.quality_check()), indent=2))
        print("\n--- PII ---")
        print(json.dumps(_unwrap(mcp_tools.pii_check()), indent=2))
    else:
        print("Prompt not recognized. Try one of these examples:")
        for ex in EXAMPLES:
            print("  - ", ex)


EXAMPLES = [
    "Show me the dataset metadata (rows and columns)",
    "Run a data quality check and list missing values and duplicates",
    "Scan the dataset for PII and give counts per column",
    "Analyze sample.csv and give metadata, quality, and PII counts",
]


def interactive():
    print("ADK agent simulator — type a prompt or 'quit'")
    while True:
        try:
            p = input('> ').strip()
        except EOFError:
            break
        if not p:
            continue
        if p.lower() in {"quit", "exit"}:
            break
        run_prompt(p)


def main():
    if len(sys.argv) <= 1 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        print("\nExample prompts:")
        for ex in EXAMPLES:
            print("  ", ex)
        return
    if sys.argv[1] in {"--interactive", "-i"}:
        interactive()
        return
    prompt = " ".join(sys.argv[1:])
    run_prompt(prompt)


if __name__ == "__main__":
    main()