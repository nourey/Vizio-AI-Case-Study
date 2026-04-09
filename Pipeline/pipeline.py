"""
Builds the final canonical DataFrame by running all three provider
transformers and concatenating their outputs.

Usage:
    python pipeline.py
"""

import pandas as pd

from dice import load_and_transform as load_dice
from naukri import load_and_transform as load_naukri
from reed import load_and_transform as load_reed


def build_canonical(
    dice_csv: str = "csv/dataset_dice_jobs.csv",
    naukri_csv: str = "csv/dataset_naukri_jobs.csv",
    reed_csv: str = "csv/dataset_reed_jobs.csv",
) -> pd.DataFrame:
    dice_df = load_dice(dice_csv)
    naukri_df = load_naukri(naukri_csv)
    reed_df = load_reed(reed_csv)

    canonical_df = pd.concat([dice_df, naukri_df, reed_df], ignore_index=True)
    return canonical_df


if __name__ == "__main__":
    df = build_canonical()
    print(f"Shape: {df.shape}")
    print(f"Sources: {df['source'].value_counts().to_dict()}")
    print(df.head(3).to_string())
