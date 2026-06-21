"""Minimal FastMCP server exposing simple tools.

Tools:
 - get_metadata(file_path)
 - quality_check(file_path)
 - pii_check(file_path)

Run: python mcp_server/server.py --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import argparse
import pandas as pd
import re
from fastmcp import FastMCP


def make_server(name: str = "GovernanceMCP") -> FastMCP:
    mcp = FastMCP(name)

    @mcp.tool()
    def get_metadata(file_path: str):
        df = pd.read_csv(file_path)
        return {"rows": len(df), "columns": list(df.columns)}

    @mcp.tool()
    def quality_check(file_path: str):
        df = pd.read_csv(file_path)
        return {"missing": df.isnull().sum().to_dict(), "duplicates": int(df.duplicated().sum())}

    @mcp.tool()
    def pii_check(file_path: str):
        df = pd.read_csv(file_path, dtype=str).fillna("")
        email_re = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        phone_re = re.compile(r"\+?\d[\d\-() ]{6,}\d")

        email_counts = {c: int(df[c].str.count(email_re).sum()) for c in df.columns}
        phone_counts = {c: int(df[c].str.count(phone_re).sum()) for c in df.columns}
        return {"email_counts": email_counts, "phone_counts": phone_counts, "total_emails": sum(email_counts.values()), "total_phones": sum(phone_counts.values())}

    return mcp


def main():
    parser = argparse.ArgumentParser(description="Run minimal Governance MCP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--name", default="GovernanceMCP")
    args = parser.parse_args()

    mcp = make_server(args.name)
    # Run HTTP transport so host/port are accepted
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()