import pandas as pd

def get_metadata():

    df = pd.read_csv("data/sample.csv")

    return {
        "rows": len(df),
        "columns": list(df.columns)
    }