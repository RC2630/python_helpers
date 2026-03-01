import pandas as pd
from typing import Any

def resolve_merged_cells(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    last_values: dict[str, Any] = {col: None for col in df.columns}
    for i in range(len(df)):
        for col in df.columns:
            if pd.isna(df.loc[i, col]):
                df.loc[i, col] = last_values[col]
            last_values[col] = df.loc[i, col]
    return df