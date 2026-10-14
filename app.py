"""
app.py — Automobile Engine & Body Explorer
==========================================
UI orchestration only. Serves the interactive HTML explorer.
"""
from pathlib import Path
import streamlit as st

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
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── HTML Explorer ─────────────────────────────────────────────────────────────
_html = (Path(__file__).parent / "frontend" / "explorer.html").read_text(encoding="utf-8")

# Inject auto-resize so iframe shrinks to fit content — no empty space below
_resize_script = """
<script>
  // Remove min-height:100vh so scrollHeight = actual content height
  document.addEventListener("DOMContentLoaded", function() {
    document.body.style.minHeight = "0";
  });
  function _sendHeight() {
    document.body.style.minHeight = "0";
    const h = document.documentElement.scrollHeight || document.body.scrollHeight;
    window.parent.postMessage(
      { isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: h }, "*"
    );
  }
  window.addEventListener("load", _sendHeight);
  [500, 1000, 2000].forEach(t => setTimeout(_sendHeight, t));
</script>
"""
_html = _html.replace("</body>", _resize_script + "</body>")
st.components.v1.html(_html, height=6000, scrolling=False)
