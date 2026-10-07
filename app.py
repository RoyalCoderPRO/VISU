"""
app.py — Automobile Engine & Body Explorer
==========================================
UI orchestration only. Data/chart logic lives in backend/.
"""
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt

from backend.data import load_automobiles, filter_df, fmt_value
from backend.charts import (
    fig_distributions, fig_price_by_body, fig_hp_mpg_by_engine,
    fig_price_vs_hp, fig_correlation, fig_makes, fig_drive_wheel,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Automobile Engine & Body Explorer",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 0.25rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Section 1: HTML Explorer ──────────────────────────────────────────────────
st.markdown("### 🏎️ Automobile Engine & Body Explorer")
_html = (Path(__file__).parent / "frontend" / "explorer.html").read_text(encoding="utf-8")
st.components.v1.html(_html, height=3000, scrolling=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Section 2: Descriptive Statistics ────────────────────────────────────────
NUMERIC = {
    "price": "Price ($)", "horsepower": "Horsepower (hp)",
    "avg-mpg": "Avg MPG", "engine-size": "Engine Size (cc)",
    "curb-weight": "Curb Weight (lbs)", "length": "Length (in)",
    "width": "Width (in)", "compression-ratio": "Compression Ratio",
    "peak-rpm": "Peak RPM",
}

st.markdown("""
<div style="text-align:center;padding:12px 0 4px">
  <h2 style="font-size:1.5rem;font-weight:700;
             background:linear-gradient(90deg,#38bdf8,#818cf8,#f472b6);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0">
    📊 Descriptive Statistics
  </h2>
  <p style="color:#475569;font-family:monospace;font-size:.72rem;letter-spacing:2px;margin-top:4px">
    1985 WARD'S AUTOMOTIVE YEARBOOK · 205 RECORDS
  </p>
</div>
""", unsafe_allow_html=True)

df = load_automobiles()

fc1, fc2, fc3 = st.columns(3)
body_f = fc1.selectbox("Body Style",  ["All"] + sorted(df["body-style"].dropna().unique()),  key="fs_body")
eng_f  = fc2.selectbox("Engine Type", ["All"] + sorted(df["engine-type"].dropna().unique()), key="fs_eng")
fuel_f = fc3.selectbox("Fuel Type",   ["All"] + sorted(df["fuel-type"].dropna().unique()),   key="fs_fuel")

dff = filter_df(df, body_f, eng_f, fuel_f)
st.caption(f"Showing **{len(dff)}** of {len(df)} records")

kpis = [
    ("Total Cars",    f"{len(dff)}"),
    ("Avg Price",     f"${dff['price'].mean():,.0f}"),
    ("Avg HP",        f"{dff['horsepower'].mean():.0f} hp"),
    ("Avg MPG",       f"{dff['avg-mpg'].mean():.1f} mpg"),
    ("Median Price",  f"${dff['price'].median():,.0f}"),
    ("Price Std Dev", f"${dff['price'].std():,.0f}"),
    ("Max HP",        f"{dff['horsepower'].max():.0f} hp"),
    ("Avg Eng. Size", f"{dff['engine-size'].mean():.0f} cc"),
]
for col, (label, val) in zip(st.columns(len(kpis)), kpis):
    col.metric(label, val)

st.markdown("---")

with st.expander("📋 Full Descriptive Statistics Table", expanded=True):
    valid = [c for c in NUMERIC if c in dff.columns]
    desc = dff[valid].describe().T
    desc.index = [NUMERIC[i] for i in desc.index]
    desc = desc.map(lambda x: fmt_value(x) if isinstance(x, float) else x)
    desc.columns = ["Count", "Mean", "Std Dev", "Min", "25%", "Median", "75%", "Max"]
    st.dataframe(desc, use_container_width=True, height=min(38 * (len(desc) + 2), 420))

st.markdown("---")
st.markdown("#### Distribution Plots")
f = fig_distributions(dff); st.pyplot(f, use_container_width=True); plt.close(f)

st.markdown("---")
col2a, col2b = st.columns(2)
with col2a:
    st.markdown("#### Avg Price by Body Style")
    f = fig_price_by_body(df); st.pyplot(f, use_container_width=True); plt.close(f)
with col2b:
    st.markdown("#### Avg HP & MPG by Engine Type")
    f = fig_hp_mpg_by_engine(df, dff); st.pyplot(f, use_container_width=True); plt.close(f)

st.markdown("---")
col3a, col3b = st.columns(2)
with col3a:
    st.markdown("#### Price vs. Horsepower")
    f = fig_price_vs_hp(dff); st.pyplot(f, use_container_width=True); plt.close(f)
with col3b:
    st.markdown("#### Correlation with Price")
    f = fig_correlation(dff); st.pyplot(f, use_container_width=True); plt.close(f)

st.markdown("---")
col4a, col4b = st.columns([1.5, 1])
with col4a:
    st.markdown("#### Cars by Make (Top 15)")
    f = fig_makes(dff); st.pyplot(f, use_container_width=True); plt.close(f)
with col4b:
    st.markdown("#### Drive-Wheel Distribution")
    f = fig_drive_wheel(dff); st.pyplot(f, use_container_width=True); plt.close(f)
