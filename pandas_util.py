import pandas as pd
from typing import Any, NamedTuple, cast
from collections.abc import Sequence

def resolve_merged_cells(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    last_values: dict[str, Any] = {col: None for col in df.columns}
    for i in range(len(df)):
        for col in df.columns:
            if pd.isna(df.loc[i, col]):
                df.loc[i, col] = last_values[col]
            last_values[col] = df.loc[i, col]
    return df

# ---------------------------------------------------------------

def clean_aggregation(
    df: pd.DataFrame,
    group_by_cols: str | list[str],
    agg_func: str,
    agg_col: str | None = None,
    agg_result_colname: str | None = None
) -> pd.DataFrame:
    
    group_by_cols_: list[str] = \
        group_by_cols if isinstance(group_by_cols, list) else [group_by_cols]
    agg_col_: str = \
        agg_col if agg_col is not None else group_by_cols_[0]
    agg_result_colname_: str = \
        agg_result_colname if agg_result_colname is not None else \
        (f"{agg_func}_{agg_col}" if agg_col is not None else agg_func)
    
    return (df
        .groupby(group_by_cols_)
        .agg(**{agg_result_colname_: (agg_col_, agg_func)})
        .reset_index())

# ---------------------------------------------------------------

class AggSpec(NamedTuple):

    agg_col: str
    agg_func: str
    agg_result_colname: str = ""

    def get_agg_result_colname(self) -> str:
        if self.agg_result_colname != "":
            return self.agg_result_colname
        else:
            return f"{self.agg_func}_{self.agg_col}"

# ---------------------------------------------------------------
        
def clean_multiple_aggregation(
    df: pd.DataFrame,
    group_by_cols: str | list[str],
    *agg_specs: AggSpec
) -> pd.DataFrame:
    
    agg_dict: dict[str, tuple[str, str]] = \
        {agg_spec.get_agg_result_colname(): (agg_spec.agg_col, agg_spec.agg_func)
         for agg_spec in agg_specs}
    
    return (df
        .groupby(group_by_cols)
        .agg(**agg_dict)
        .reset_index())

# ---------------------------------------------------------------

def build_df_from_named_tuples(named_tuples: Sequence[NamedTuple]) -> pd.DataFrame:
    if len(named_tuples) == 0:
        return pd.DataFrame()
    return pd.DataFrame(named_tuples, columns = named_tuples[0]._fields)

def extract_named_tuples_from_df[T](
    df: pd.DataFrame, named_tuple_class: type[T]
) -> list[T]:
    return [
        named_tuple_class(*row) for row in
        df[list(cast(type[NamedTuple], named_tuple_class)._fields)]
        .itertuples(index = False, name = None)
    ]

def extract_named_tuple_from_df_row_pos[T](
    df: pd.DataFrame, row_pos: int, named_tuple_class: type[T]
) -> T:
    return extract_named_tuples_from_df(df.iloc[[row_pos]], named_tuple_class)[0]

def extract_named_tuple_from_df_row_index[T](
    df: pd.DataFrame, row_index: Any, named_tuple_class: type[T]
) -> T:
    return extract_named_tuples_from_df(df.loc[[row_index]], named_tuple_class)[0]