from fastmcp import FastMCP
import pandas as pd

mcp = FastMCP("GovernanceMCP")

@mcp.tool()
def get_metadata(file_path: str):

    df = pd.read_csv(file_path)

    return {
        "rows": len(df),
        "columns": list(df.columns)
    }

@mcp.tool()
def quality_check(file_path: str):

    df = pd.read_csv(file_path)

    return {
        "missing": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum())
    }

if __name__ == "__main__":
    mcp.run()