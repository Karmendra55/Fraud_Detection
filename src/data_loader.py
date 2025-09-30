import pandas as pd
import os
from glob import glob
from typing import List

def load_all_transaction_data(data_dir: str) -> pd.DataFrame:
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    all_files: List[str] = sorted(glob(os.path.join(data_dir, "*.pkl")))

    if not all_files:
        raise ValueError(f"No .pkl files found in directory: {data_dir}")

    df_list: List[pd.DataFrame] = []

    for file in all_files:
        df = pd.read_pickle(file)
        if "TX_DATETIME" not in df.columns:
            raise KeyError(f"'TX_DATETIME' column missing in file: {file}")
        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.sort_values("TX_DATETIME", inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    return combined_df

def list_raw_files(folder):
    return sorted([f for f in os.listdir(folder) if f.endswith(".pkl")])

def load_raw_data(path):
    return pd.read_pickle(path)