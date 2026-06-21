import pandas as pd

def get_metadata():

    df = pd.read_csv("data/sample.csv")

    return {
        "rows": len(df),
        "columns": list(df.columns)
    }

def quality_check():

    df = pd.read_csv("data/sample.csv")

    return {
        "missing": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum())
    }