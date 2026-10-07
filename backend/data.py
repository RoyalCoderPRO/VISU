"""
backend/data.py
===============
Data loading and caching.
All data access goes through functions defined here — no CSV reads elsewhere.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

_DATA_DIR = Path(__file__).parent.parent  # repo root


@st.cache_data
def load_automobiles() -> pd.DataFrame:
    """Load and clean the Automobile dataset. Result is cached by Streamlit."""
    csv = _DATA_DIR / "Automobile_data.csv"
    df = pd.read_csv(csv, na_values=["?"])
    df.columns = df.columns.str.strip()
    numeric_cols = [
        "normalized-losses", "wheel-base", "length", "width", "height",
        "curb-weight", "engine-size", "bore", "stroke", "compression-ratio",
        "horsepower", "peak-rpm", "city-mpg", "highway-mpg", "price",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["avg-mpg"] = (df["city-mpg"] + df["highway-mpg"]) / 2
    return df


def filter_df(
    df: pd.DataFrame,
    body: str = "All",
    engine: str = "All",
    fuel: str = "All",
) -> pd.DataFrame:
    """Apply dropdown filters to the dataframe."""
    out = df.copy()
    if body   != "All": out = out[out["body-style"]   == body]
    if engine != "All": out = out[out["engine-type"]  == engine]
    if fuel   != "All": out = out[out["fuel-type"]    == fuel]
    return out


def fmt_value(v) -> str:
    """Format a numeric cell for display in the stats table."""
    if pd.isna(v):
        return "—"
    return f"{v:,.0f}" if abs(v) >= 1_000 else f"{v:.2f}"
