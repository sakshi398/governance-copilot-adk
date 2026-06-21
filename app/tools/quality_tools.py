import pandas as pd

def quality_check(file_path):

    df = pd.read_csv(file_path)

    return {
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum())
    }