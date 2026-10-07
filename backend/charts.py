"""
backend/charts.py
=================
All matplotlib chart-building logic.
Each function takes a (filtered) DataFrame and returns a plt.Figure.
No Streamlit calls in here — only data → figure transformations.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ── Colour palette ────────────────────────────────────────────────────────────
ACCENT = ["#38bdf8", "#818cf8", "#f472b6", "#34d399", "#fb923c", "#facc15", "#a78bfa"]
BODY_C = {
    "convertible": "#f472b6",
    "hardtop":     "#fb923c",
    "hatchback":   "#38bdf8",
    "sedan":       "#818cf8",
    "wagon":       "#34d399",
}

# Apply the dark theme once at import time
plt.rcParams.update({
    "figure.facecolor":  "#0f172a",
    "axes.facecolor":    "#111827",
    "axes.edgecolor":    "#1e293b",
    "axes.labelcolor":   "#94a3b8",
    "axes.titlecolor":   "#e2e8f0",
    "xtick.color":       "#64748b",
    "ytick.color":       "#64748b",
    "grid.color":        "#1e293b",
    "grid.linewidth":    0.6,
    "text.color":        "#e2e8f0",
    "font.family":       "monospace",
    "legend.facecolor":  "#111827",
    "legend.edgecolor":  "#1e293b",
    "legend.labelcolor": "#94a3b8",
})


def fig_distributions(dff: pd.DataFrame) -> plt.Figure:
    """4-panel histogram of key numeric features."""
    HCOLS = [
        ("price",       "Price ($)",         "#38bdf8"),
        ("horsepower",  "Horsepower (hp)",   "#f472b6"),
        ("avg-mpg",     "Avg MPG",           "#34d399"),
        ("engine-size", "Engine Size (cc)",  "#fb923c"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.2))
    for ax, (col, label, color) in zip(axes, HCOLS):
        data = dff[col].dropna()
        if len(data) > 1:
            ax.hist(data, bins=20, color=color, alpha=0.82,
                    edgecolor=color, linewidth=0.4)
            ax.axvline(data.mean(),   color="#ffffff", lw=1.2, ls="--",
                       alpha=0.7, label=f"μ={data.mean():,.0f}")
            ax.axvline(data.median(), color="#facc15", lw=1.2, ls=":",
                       alpha=0.9, label=f"M={data.median():,.0f}")
            ax.legend(fontsize=6.5, loc="upper right")
        ax.set_title(label, fontsize=8, fontweight="bold", pad=4)
        ax.set_ylabel("Count", fontsize=7)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=4))
        ax.tick_params(labelsize=6.5)
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(pad=1.1)
    return fig


def fig_price_by_body(df: pd.DataFrame) -> plt.Figure:
    """Bar chart: average price by body style."""
    bodies = list(BODY_C.keys())
    means  = [df[df["body-style"] == b]["price"].mean() for b in bodies]
    fig, ax = plt.subplots(figsize=(6, 3.4))
    bars = ax.bar(
        [b.title() for b in bodies], means,
        color=[BODY_C[b] + "99" for b in bodies],
        edgecolor=list(BODY_C.values()), linewidth=1.4, width=0.55,
    )
    for bar, v in zip(bars, means):
        if not np.isnan(v):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 200,
                    f"${v:,.0f}", ha="center", va="bottom",
                    fontsize=7, color="#94a3b8")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.tick_params(labelsize=7.5)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def fig_hp_mpg_by_engine(df: pd.DataFrame, dff: pd.DataFrame) -> plt.Figure:
    """Grouped bar: avg HP and avg MPG×4 by engine type."""
    eng_keys = sorted(df["engine-type"].dropna().unique())
    hp_vals  = [dff[dff["engine-type"] == e]["horsepower"].mean() for e in eng_keys]
    mpg_vals = [dff[dff["engine-type"] == e]["avg-mpg"].mean() * 4 for e in eng_keys]
    x, w = np.arange(len(eng_keys)), 0.38
    fig, ax = plt.subplots(figsize=(6, 3.4))
    b1 = ax.bar(x - w / 2, hp_vals,  w, color="#f472b699",
                edgecolor="#f472b6", lw=1.4, label="Avg HP")
    b2 = ax.bar(x + w / 2, mpg_vals, w, color="#34d39999",
                edgecolor="#34d399", lw=1.4, label="Avg MPG ×4")
    ax.set_xticks(x)
    ax.set_xticklabels([e.upper() for e in eng_keys], fontsize=8)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    raw_mpg = [dff[dff["engine-type"] == e]["avg-mpg"].mean() for e in eng_keys]
    for bar, mpg in zip(b2, raw_mpg):
        if not np.isnan(mpg):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{mpg:.0f}", ha="center", va="bottom",
                    fontsize=6.5, color="#34d399")
    fig.tight_layout()
    return fig


def fig_price_vs_hp(dff: pd.DataFrame) -> plt.Figure:
    """Scatter: price vs horsepower, coloured by body style."""
    sc = dff[["price", "horsepower", "body-style"]].dropna()
    cmap = {b: ACCENT[i % len(ACCENT)] for i, b in enumerate(sorted(sc["body-style"].unique()))}
    fig, ax = plt.subplots(figsize=(6, 3.8))
    for bname, grp in sc.groupby("body-style"):
        ax.scatter(grp["horsepower"], grp["price"], c=cmap[bname],
                   alpha=0.72, s=28, label=bname.title(), edgecolors="none")
    if len(sc) > 2:
        z  = np.polyfit(sc["horsepower"], sc["price"], 1)
        xp = np.linspace(sc["horsepower"].min(), sc["horsepower"].max(), 100)
        ax.plot(xp, np.poly1d(z)(xp), "--", color="#ffffff",
                lw=1.2, alpha=0.45, label="Trend")
    ax.set_xlabel("Horsepower (hp)", fontsize=8)
    ax.set_ylabel("Price ($)",       fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def fig_correlation(dff: pd.DataFrame) -> plt.Figure:
    """Horizontal bar: Pearson r of numeric features with price."""
    corr_feats = [
        ("HP",         "horsepower"),
        ("Eng.Sz",     "engine-size"),
        ("Weight",     "curb-weight"),
        ("Width",      "width"),
        ("Length",     "length"),
        ("WheelBase",  "wheel-base"),
        ("Avg MPG",    "avg-mpg"),
        ("Peak RPM",   "peak-rpm"),
        ("Comp.R",     "compression-ratio"),
    ]
    vals = []
    for _, col in corr_feats:
        pairs = dff[["price", col]].dropna()
        vals.append(pairs.corr().iloc[0, 1] if len(pairs) > 4 else 0)
    sorted_pairs = sorted(zip([l for l, _ in corr_feats], vals),
                          key=lambda x: x[1], reverse=True)
    slabels, svals = zip(*sorted_pairs)
    colors = ["#38bdf8" if v >= 0 else "#f472b6" for v in svals]
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.barh(slabels, svals, color=[c + "99" for c in colors],
            edgecolor=colors, linewidth=1.3, height=0.55)
    ax.axvline(0, color="#475569", lw=0.8)
    ax.set_xlim(-1, 1)
    ax.tick_params(labelsize=7.5)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def fig_makes(dff: pd.DataFrame) -> plt.Figure:
    """Horizontal bar: top-15 makes by count."""
    mc = dff["make"].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.barh(mc.index[::-1], mc.values[::-1],
                   color=ACCENT[0] + "99", edgecolor=ACCENT[0],
                   linewidth=1.2, height=0.6)
    for bar, v in zip(bars, mc.values[::-1]):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", fontsize=7, color="#94a3b8")
    ax.set_xlim(right=mc.max() * 1.2)
    ax.tick_params(labelsize=7.5)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


def fig_drive_wheel(dff: pd.DataFrame) -> plt.Figure:
    """Pie chart: drive-wheel distribution."""
    dw = dff["drive-wheels"].value_counts()
    fig, ax = plt.subplots(figsize=(4.5, 4))
    wedges, texts, autotexts = ax.pie(
        dw.values,
        labels=[d.upper() for d in dw.index],
        autopct="%1.1f%%",
        colors=ACCENT[: len(dw)],
        startangle=140,
        pctdistance=0.78,
        wedgeprops=dict(linewidth=1.5, edgecolor="#0f172a"),
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color("#e2e8f0")
    for t in texts:
        t.set_fontsize(9)
    fig.tight_layout()
    return fig
