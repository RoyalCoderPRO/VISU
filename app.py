"""
app.py — Automobile Engine & Body Explorer
==========================================
Section 1 : Interactive HTML explorer (served via a background HTTP server
            and embedded with st.iframe so full JS/CSS runs intact)
Section 2 : Descriptive statistics — pure Streamlit + matplotlib/pandas
"""

import http.server
import socketserver
import threading
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 1. Background HTTP file server (serves the whole workspace dir on port 8502)
#    This lets the HTML page load its images and Chart.js from the filesystem
#    without any Streamlit serving complexity.
# ─────────────────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).parent.resolve()
FILE_SERVER_PORT = 8502

class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler that serves WORKSPACE silently."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORKSPACE), **kwargs)
    def log_message(self, *_):
        pass  # suppress stdout noise

def _start_file_server() -> None:
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("0.0.0.0", FILE_SERVER_PORT), _SilentHandler) as httpd:
            httpd.serve_forever()
    except OSError:
        pass  # already running from a previous hot-reload

# Start once; daemon=True means it dies when the main process exits.
_server_thread = threading.Thread(target=_start_file_server, daemon=True)
_server_thread.start()

HTML_URL = "app/static/engine_explorer.html"

# ─────────────────────────────────────────────────────────────────────────────
# 2. Streamlit page setup
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# 3. Matplotlib dark theme
# ─────────────────────────────────────────────────────────────────────────────
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

ACCENT  = ["#38bdf8","#818cf8","#f472b6","#34d399","#fb923c","#facc15","#a78bfa"]
BODY_C  = {"convertible":"#f472b6","hardtop":"#fb923c",
           "hatchback":"#38bdf8","sedan":"#818cf8","wagon":"#34d399"}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Data loader (cached)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    csv = WORKSPACE / "Automobile_data.csv"
    df = pd.read_csv(csv, na_values=["?"])
    df.columns = df.columns.str.strip()
    for c in ["normalized-losses","wheel-base","length","width","height",
              "curb-weight","engine-size","bore","stroke","compression-ratio",
              "horsepower","peak-rpm","city-mpg","highway-mpg","price"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["avg-mpg"] = (df["city-mpg"] + df["highway-mpg"]) / 2
    return df

def fmt(v):
    if pd.isna(v): return "—"
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.2f}"

# ─────────────────────────────────────────────────────────────────────────────
# 5. Stats section
# ─────────────────────────────────────────────────────────────────────────────
def stats_section(df: pd.DataFrame) -> None:
    st.markdown("""
    <div style="text-align:center;padding:12px 0 4px">
      <h2 style="font-size:1.5rem;font-weight:700;
                 background:linear-gradient(90deg,#38bdf8,#818cf8,#f472b6);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0">
        📊 Descriptive Statistics
      </h2>
      <p style="color:#475569;font-family:monospace;font-size:.72rem;
                letter-spacing:2px;margin-top:4px">
        1985 WARD'S AUTOMOTIVE YEARBOOK · 205 RECORDS
      </p>
    </div>
    """, unsafe_allow_html=True)

    NUMERIC = {
        "price": "Price ($)", "horsepower": "Horsepower (hp)",
        "avg-mpg": "Avg MPG", "engine-size": "Engine Size (cc)",
        "curb-weight": "Curb Weight (lbs)", "length": "Length (in)",
        "width": "Width (in)", "compression-ratio": "Compression Ratio",
        "peak-rpm": "Peak RPM",
    }

    # ── Filters ──────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns(3)
    body_f = fc1.selectbox("Body Style", ["All"] + sorted(df["body-style"].dropna().unique()), key="fs_body")
    eng_f  = fc2.selectbox("Engine Type", ["All"] + sorted(df["engine-type"].dropna().unique()), key="fs_eng")
    fuel_f = fc3.selectbox("Fuel Type", ["All"] + sorted(df["fuel-type"].dropna().unique()), key="fs_fuel")

    dff = df.copy()
    if body_f != "All": dff = dff[dff["body-style"] == body_f]
    if eng_f  != "All": dff = dff[dff["engine-type"] == eng_f]
    if fuel_f != "All": dff = dff[dff["fuel-type"] == fuel_f]

    st.caption(f"Showing **{len(dff)}** of {len(df)} records")

    # ── KPI cards ────────────────────────────────────────────────────────────
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

    # ── Full describe table ───────────────────────────────────────────────────
    with st.expander("📋 Full Descriptive Statistics Table", expanded=True):
        valid = [c for c in NUMERIC if c in dff.columns]
        desc = dff[valid].describe().T
        desc.index = [NUMERIC[i] for i in desc.index]
        desc = desc.map(lambda x: fmt(x) if isinstance(x, float) else x)
        desc.columns = ["Count","Mean","Std Dev","Min","25%","Median","75%","Max"]
        st.dataframe(desc, use_container_width=True, height=min(38*(len(desc)+2), 420))

    st.markdown("---")

    # ── Row 1: Histograms ─────────────────────────────────────────────────────
    st.markdown("#### Distribution Plots")
    HCOLS = [("price","Price ($)","#38bdf8"), ("horsepower","Horsepower (hp)","#f472b6"),
             ("avg-mpg","Avg MPG","#34d399"),  ("engine-size","Engine Size (cc)","#fb923c")]

    fig, axes = plt.subplots(1, 4, figsize=(16, 3.2))
    for ax, (col, label, color) in zip(axes, HCOLS):
        data = dff[col].dropna()
        if len(data) > 1:
            ax.hist(data, bins=20, color=color, alpha=0.82, edgecolor=color, linewidth=0.4)
            ax.axvline(data.mean(),   color="#ffffff", lw=1.2, ls="--", alpha=0.7,
                       label=f"μ={data.mean():,.0f}")
            ax.axvline(data.median(), color="#facc15", lw=1.2, ls=":",  alpha=0.9,
                       label=f"M={data.median():,.0f}")
            ax.legend(fontsize=6.5, loc="upper right")
        ax.set_title(label, fontsize=8, fontweight="bold", pad=4)
        ax.set_ylabel("Count", fontsize=7)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=4))
        ax.tick_params(labelsize=6.5)
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(pad=1.1)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.markdown("---")

    # ── Row 2: Body price bar | Engine HP/MPG bar ─────────────────────────────
    col2a, col2b = st.columns(2)

    with col2a:
        st.markdown("#### Avg Price by Body Style")
        bodies = list(BODY_C.keys())
        means  = [df[df["body-style"] == b]["price"].mean() for b in bodies]
        fig2, ax2 = plt.subplots(figsize=(6, 3.4))
        bars = ax2.bar([b.title() for b in bodies], means,
                       color=[BODY_C[b]+"99" for b in bodies],
                       edgecolor=list(BODY_C.values()), linewidth=1.4, width=0.55)
        for bar, v in zip(bars, means):
            if not np.isnan(v):
                ax2.text(bar.get_x() + bar.get_width()/2, v + 200,
                         f"${v:,.0f}", ha="center", va="bottom", fontsize=7, color="#94a3b8")
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax2.tick_params(labelsize=7.5); ax2.grid(axis="y", alpha=0.3)
        fig2.tight_layout()
        st.pyplot(fig2, use_container_width=True); plt.close(fig2)

    with col2b:
        st.markdown("#### Avg HP & MPG by Engine Type")
        eng_keys = sorted(df["engine-type"].dropna().unique())
        hp_vals  = [dff[dff["engine-type"]==e]["horsepower"].mean() for e in eng_keys]
        mpg_vals = [dff[dff["engine-type"]==e]["avg-mpg"].mean() * 4  for e in eng_keys]
        x = np.arange(len(eng_keys)); w = 0.38
        fig3, ax3 = plt.subplots(figsize=(6, 3.4))
        b1 = ax3.bar(x - w/2, hp_vals,  w, color="#f472b699", edgecolor="#f472b6", lw=1.4, label="Avg HP")
        b2 = ax3.bar(x + w/2, mpg_vals, w, color="#34d39999", edgecolor="#34d399", lw=1.4, label="Avg MPG ×4")
        ax3.set_xticks(x)
        ax3.set_xticklabels([e.upper() for e in eng_keys], fontsize=8)
        ax3.tick_params(labelsize=7); ax3.legend(fontsize=8); ax3.grid(axis="y", alpha=0.3)
        for bar, mpg in zip(b2, [dff[dff["engine-type"]==e]["avg-mpg"].mean() for e in eng_keys]):
            if not np.isnan(mpg):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                         f"{mpg:.0f}", ha="center", va="bottom", fontsize=6.5, color="#34d399")
        fig3.tight_layout()
        st.pyplot(fig3, use_container_width=True); plt.close(fig3)

    st.markdown("---")

    # ── Row 3: Scatter | Correlation bar ─────────────────────────────────────
    col3a, col3b = st.columns(2)

    with col3a:
        st.markdown("#### Price vs. Horsepower")
        sc = dff[["price","horsepower","body-style"]].dropna()
        cmap = {b: ACCENT[i % len(ACCENT)] for i, b in enumerate(sorted(sc["body-style"].unique()))}
        fig4, ax4 = plt.subplots(figsize=(6, 3.8))
        for bname, grp in sc.groupby("body-style"):
            ax4.scatter(grp["horsepower"], grp["price"], c=cmap[bname],
                        alpha=0.72, s=28, label=bname.title(), edgecolors="none")
        if len(sc) > 2:
            z  = np.polyfit(sc["horsepower"], sc["price"], 1)
            xp = np.linspace(sc["horsepower"].min(), sc["horsepower"].max(), 100)
            ax4.plot(xp, np.poly1d(z)(xp), "--", color="#ffffff", lw=1.2, alpha=0.45, label="Trend")
        ax4.set_xlabel("Horsepower (hp)", fontsize=8)
        ax4.set_ylabel("Price ($)", fontsize=8)
        ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax4.tick_params(labelsize=7); ax4.legend(fontsize=6.5, ncol=2); ax4.grid(alpha=0.3)
        fig4.tight_layout()
        st.pyplot(fig4, use_container_width=True); plt.close(fig4)

    with col3b:
        st.markdown("#### Correlation with Price")
        corr_feats = [("HP","horsepower"),("Eng.Sz","engine-size"),("Weight","curb-weight"),
                      ("Width","width"),("Length","length"),("WheelBase","wheel-base"),
                      ("Avg MPG","avg-mpg"),("Peak RPM","peak-rpm"),("Comp.R","compression-ratio")]
        corr_vals = []
        for label, col in corr_feats:
            pairs = dff[["price", col]].dropna()
            corr_vals.append(pairs.corr().iloc[0, 1] if len(pairs) > 4 else 0)
        sorted_pairs = sorted(zip([l for l,_ in corr_feats], corr_vals), key=lambda x: x[1], reverse=True)
        slabels, svals = zip(*sorted_pairs)
        colors5 = ["#38bdf8" if v >= 0 else "#f472b6" for v in svals]
        fig5, ax5 = plt.subplots(figsize=(6, 3.8))
        ax5.barh(slabels, svals, color=[c+"99" for c in colors5],
                 edgecolor=colors5, linewidth=1.3, height=0.55)
        ax5.axvline(0, color="#475569", lw=0.8)
        ax5.set_xlim(-1, 1); ax5.tick_params(labelsize=7.5); ax5.grid(axis="x", alpha=0.3)
        fig5.tight_layout()
        st.pyplot(fig5, use_container_width=True); plt.close(fig5)

    st.markdown("---")

    # ── Row 4: Make counts | Drive-wheel ─────────────────────────────────────
    col4a, col4b = st.columns([1.5, 1])

    with col4a:
        st.markdown("#### Cars by Make (Top 15)")
        mc = dff["make"].value_counts().head(15)
        fig6, ax6 = plt.subplots(figsize=(6.5, 4))
        bars6 = ax6.barh(mc.index[::-1], mc.values[::-1],
                         color=ACCENT[0]+"99", edgecolor=ACCENT[0], linewidth=1.2, height=0.6)
        for bar6, v6 in zip(bars6, mc.values[::-1]):
            ax6.text(bar6.get_width() + 0.15, bar6.get_y() + bar6.get_height()/2,
                     str(v6), va="center", fontsize=7, color="#94a3b8")
        ax6.set_xlim(right=mc.max() * 1.2)
        ax6.tick_params(labelsize=7.5); ax6.grid(axis="x", alpha=0.3)
        fig6.tight_layout()
        st.pyplot(fig6, use_container_width=True); plt.close(fig6)

    with col4b:
        st.markdown("#### Drive-Wheel Distribution")
        dw = dff["drive-wheels"].value_counts()
        fig7, ax7 = plt.subplots(figsize=(4.5, 4))
        wedges, texts, autotexts = ax7.pie(
            dw.values, labels=[d.upper() for d in dw.index],
            autopct="%1.1f%%", colors=ACCENT[:len(dw)],
            startangle=140, pctdistance=0.78,
            wedgeprops=dict(linewidth=1.5, edgecolor="#0f172a"))
        for t in autotexts: t.set_fontsize(8); t.set_color("#e2e8f0")
        for t in texts:     t.set_fontsize(9)
        fig7.tight_layout()
        st.pyplot(fig7, use_container_width=True); plt.close(fig7)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    # ── Section 1: HTML Explorer ─────────────────────────────────────────────
    st.markdown("### 🏎️ Automobile Engine & Body Explorer")
    st.iframe(HTML_URL, height=3000)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()


    # ── Section 2: Descriptive Stats ─────────────────────────────────────────
    df = load_data()
    stats_section(df)


if __name__ == "__main__":
    main()
