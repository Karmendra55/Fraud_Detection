import pandas as pd
import numpy as np
import os
import warnings
from tqdm import tqdm

warnings.filterwarnings("ignore")

DATA_FOLDER = "data"
OUTPUT_FILE = "processed/feature_engineered_df.pkl"
START_DATE = "2018-04-01"
END_DATE = "2018-09-30"

def read_and_merge_pickles(data_folder: str, start_date: str, end_date: str) -> pd.DataFrame:
    print("📂 Reading pickle files...")
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    df_list = []

    for date in tqdm(date_range, desc="Loading files"):
        file_path = os.path.join(data_folder, f"{date.strftime('%Y-%m-%d')}.pkl")
        if os.path.exists(file_path):
            try:
                df = pd.read_pickle(file_path)
                df_list.append(df)
            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
        else:
            print(f"❌ Missing file: {file_path}")

    if not df_list:
        raise FileNotFoundError("No pickle files were found in the specified range.")

    combined_df = pd.concat(df_list, ignore_index=True)
    print(f"\n✅ Loaded {len(df_list)} files. Combined shape: {combined_df.shape}")
    return combined_df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    print("⚙️ Adding new features...")

    df["TX_DATETIME"] = pd.to_datetime(df["TX_DATETIME"])

    # --- Time features ---
    df["TX_HOUR"] = df["TX_DATETIME"].dt.hour
    df["TX_WEEKDAY"] = df["TX_DATETIME"].dt.weekday
    df["TX_MONTH"] = df["TX_DATETIME"].dt.month
    df["IS_WEEKEND"] = df["TX_WEEKDAY"].isin([5, 6]).astype(int)

    # --- Amount bins ---
    amount_bins = [-1, 10, 50, 100, 500, 1000, 5000, np.inf]
    amount_labels = ["0-10", "10-50", "50-100", "100-500", "500-1000", "1000-5000", "5000+"]
    df["TX_AMOUNT_BIN"] = pd.cut(df["TX_AMOUNT"], bins=amount_bins, labels=amount_labels)

    # --- Customer transaction counts ---
    tx_counts = (
        df.groupby("CUSTOMER_ID")["TRANSACTION_ID"]
        .count()
        .reset_index()
        .rename(columns={"TRANSACTION_ID": "TX_COUNT"})
    )
    df = df.merge(tx_counts, on="CUSTOMER_ID", how="left")

    return df

def save_processed_data(df: pd.DataFrame, output_file: str):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_pickle(output_file)
    print(f"💾 Processed data saved to: {output_file}")


def load_processed_data(path: str) -> pd.DataFrame:
    return pd.read_pickle(path)

def main():
    df = read_and_merge_pickles(DATA_FOLDER, START_DATE, END_DATE)
    df = add_features(df)
    save_processed_data(df, OUTPUT_FILE)

    print("\n📋 Feature Summary:")
    with pd.option_context("display.max_columns", None, "display.width", 120):
        print(df.describe(include="all").T[["count", "unique", "top", "freq", "mean", "std", "min", "25%", "50%", "75%", "max"]])

    class_dist = df["TX_FRAUD"].value_counts(normalize=True) * 100
    print("\n🎯 Fraud Distribution (%):\n", class_dist.round(2))
