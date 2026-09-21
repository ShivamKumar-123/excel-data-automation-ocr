import streamlit as st
import pandas as pd
import io
import zipfile
import os
import time
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAVICON_PATH = os.path.join(BASE_DIR, "assets", "favicon.png")
HERO_ILLUSTRATION_PATH = os.path.join(BASE_DIR, "assets", "hero_illustration.png")


from main import (
    clean_dataframe,
    translate_hindi_df,
    pdf_to_df,
    image_to_df,
    enterprise_dedup_engine,
    ultra_fast_dedup,
    detect_field_types,
    read_any_table,
    INDUSTRY_PRESETS,
    data_quality_report,
    dataframe_to_bytes,
    read_all_sheets_raw,
    build_multi_sheet_excel,
)


def show_detected_fields(df, label="Detected Field Types", industry=None):
    """Displays the auto-detected column -> field-type mapping."""
    field_map = detect_field_types(df, industry=industry)
    with st.expander(f"🔎 {label}"):
        if field_map:
            st.dataframe(
                pd.DataFrame(
                    {"Column": list(field_map.keys()), "Detected As": list(field_map.values())}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recognizable field types detected — generic cleaning still applied.")


def highlight_duplicates(df, duplicate_indices):
    def highlight_row(row):
        if row.name in duplicate_indices:
            return ['background-color: rgba(225, 29, 72, 0.08); color: #9f1239;'] * len(row)
        return [''] * len(row)
    return df.style.apply(highlight_row, axis=1)


# ================= TOOL REGISTRY (drives dashboard cards + sidebar nav) =================
TOOL_SECTIONS = [
    {"key": "sec-1", "num": "01", "icon": "📄", "accent": "tool-blue",
     "title": "Single File Processing", "desc": "Upload and auto-clean any individual file"},
    {"key": "sec-2", "num": "02", "icon": "🗂️", "accent": "tool-violet",
     "title": "Batch Processing", "desc": "Process multiple files together — export as ZIP"},
    {"key": "sec-3", "num": "03", "icon": "🗄️", "accent": "tool-emerald",
     "title": "Data Fusion", "desc": "Merge and combine data from multiple sources"},
    {"key": "sec-4", "num": "04", "icon": "🎯", "accent": "tool-amber",
     "title": "Precision Extract", "desc": "Extract specific data with accuracy"},
    {"key": "sec-5", "num": "05", "icon": "🔍", "accent": "tool-rose",
     "title": "Match & Remove", "desc": "Find and remove rows that exist in a reference file"},
    {"key": "sec-6", "num": "06", "icon": "🧠", "accent": "tool-indigo",
     "title": "AI Smart Dedup", "desc": "ML-powered duplicate detection within a single file"},
    {"key": "sec-7", "num": "07", "icon": "📊", "accent": "tool-blue",
     "title": "Data Quality Report", "desc": "Generate detailed data quality insights"},
    {"key": "sec-8", "num": "08", "icon": "🧩", "accent": "tool-violet",
     "title": "Column Tools", "desc": "Manage, rename, and transform columns"},
    {"key": "sec-9", "num": "09", "icon": "🔄", "accent": "tool-cyan",
     "title": "Format Converter", "desc": "Convert between multiple file formats"},
]
TOOL_BY_KEY = {t["key"]: t for t in TOOL_SECTIONS}


def go_to(view_key):
    st.session_state.view = view_key


def clear_search():
    st.session_state.dash_search = ""


if "view" not in st.session_state:
    st.session_state.view = "dashboard"

view = st.session_state.view


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DataFlow Pro — Smart Data Automation",
    page_icon=FAVICON_PATH if os.path.exists(FAVICON_PATH) else "⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= LIGHT DASHBOARD THEME =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

    :root {
        --bg: #f1f5f9;
        --surface: #ffffff;
        --border: #e2e8f0;
        --text-h: #0f172a;
        --text-b: #475569;
        --text-m: #94a3b8;
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-tint: #eff6ff;
        --shadow-sm: 0 1px 3px rgba(15,23,42,0.06);
        --shadow-md: 0 10px 28px rgba(15,23,42,0.08);
    }

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { background: var(--bg); }

    /* Give the main content comfortable side/top gutters — Streamlit's own
       default block-container padding is too thin, so text and cards were
       sitting flush against the browser edge, especially with the sidebar
       collapsed. */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: clamp(1.5rem, 4vw, 3.5rem) !important;
        padding-right: clamp(1.5rem, 4vw, 3.5rem) !important;
        max-width: 1600px;
    }

    h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif !important; color: var(--text-h) !important; }
    p, span, div, label { color: var(--text-b); }

    /* ===== Top bar ===== */
    .topbar-actions { display: flex; align-items: center; justify-content: flex-end; gap: 0.7rem; }
    .topbar-icon-btn {
        width: 38px; height: 38px; border-radius: 10px; background: var(--surface);
        border: 1px solid var(--border); display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem; position: relative;
    }
    .topbar-dot {
        position: absolute; top: 6px; right: 7px; width: 7px; height: 7px; border-radius: 50%;
        background: #ef4444; border: 1.5px solid var(--surface);
    }
    .topbar-avatar {
        display: flex; align-items: center; gap: 0.55rem; padding: 0.3rem 0.7rem 0.3rem 0.35rem;
        border-radius: 12px; border: 1px solid var(--border); background: var(--surface);
    }
    .avatar-circle {
        width: 32px; height: 32px; border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff !important;
        display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem;
        flex-shrink: 0;
    }
    .avatar-name { font-size: 0.84rem; font-weight: 700; color: var(--text-h) !important; line-height: 1.15; }
    .avatar-plan { font-size: 0.68rem; color: var(--text-m) !important; }
    .topbar-chevron { color: var(--text-m) !important; margin-left: 2px; }
    .topbar-hr { margin: 1rem 0 1.5rem !important; }

    [data-testid="stTextInput"] input {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-h) !important;
        padding: 0.62rem 0.9rem !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    }
    [data-testid="stTextInput"] input::placeholder { color: var(--text-m) !important; }

    /* ===== Hero ===== */
    .hero-container {
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 55%, #ffffff 100%);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 2.6rem 2.8rem;
        margin-bottom: 1.8rem;
        box-shadow: var(--shadow-md);
    }
    .hero-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: var(--surface); border: 1px solid var(--border);
        padding: 0.4rem 1rem; border-radius: 50px;
        font-size: 0.76rem; font-weight: 700; color: var(--primary) !important;
        letter-spacing: 0.5px; margin-bottom: 1.1rem; text-transform: uppercase;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif; font-size: 2.7rem; font-weight: 800;
        color: var(--text-h) !important; margin: 0; letter-spacing: -1px; line-height: 1.15;
    }
    .hero-title .accent { color: var(--primary) !important; }
    .hero-tagline {
        font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 600;
        color: var(--text-h) !important; margin-top: 0.35rem;
    }
    .hero-subtitle { color: var(--text-b); font-size: 0.98rem; margin-top: 0.9rem; max-width: 560px; line-height: 1.65; }

    .feature-pills { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 1.7rem; }
    .pill {
        display: inline-flex; align-items: center; gap: 0.4rem;
        padding: 0.5rem 1rem; border-radius: 10px;
        font-size: 0.8rem; font-weight: 600;
        background: var(--surface); border: 1px solid var(--border); color: var(--text-b) !important;
    }

    /* ===== Dashboard heading row ===== */
    .dashboard-eyebrow {
        font-size: 0.75rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
        color: var(--primary) !important;
    }
    .dashboard-heading-row {
        display: flex; align-items: flex-end; justify-content: space-between;
        margin: 0.3rem 0 1.2rem; flex-wrap: wrap; gap: 0.5rem;
    }
    .dashboard-heading-row h2 { font-size: 1.6rem; margin: 0.15rem 0 0; }
    .dashboard-heading-row p { color: var(--text-m) !important; margin: 0.3rem 0 0; font-size: 0.92rem; }

    /* ===== Tool cards (dashboard grid) ===== */
    .tool-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.7rem; }
    .tool-icon {
        width: 44px; height: 44px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
    }
    .tool-card-heading { font-weight: 700; color: var(--text-h) !important; font-size: 1rem; }
    .tool-card-heading .tool-num {
        color: var(--text-m) !important; font-family: 'JetBrains Mono', monospace;
        font-weight: 600; font-size: 0.82rem; margin-right: 0.35rem;
    }
    .tool-card-desc { color: var(--text-m) !important; font-size: 0.84rem; margin-top: 0.3rem; line-height: 1.4; min-height: 2.6em; }

    .tool-blue { background: #eff6ff; color: #2563eb; }
    .tool-violet { background: #f5f3ff; color: #7c3aed; }
    .tool-emerald { background: #ecfdf5; color: #059669; }
    .tool-amber { background: #fffbeb; color: #d97706; }
    .tool-rose { background: #fff1f2; color: #e11d48; }
    .tool-indigo { background: #eef2ff; color: #4f46e5; }
    .tool-cyan { background: #ecfeff; color: #0891b2; }

    /* Card shadow/radius, scoped via a marker (data-testid="stVerticalBlockBorderWrapper"
       is NOT exclusive to st.container(border=True) — every st.columns() column also
       gets this same testid, so an unscoped rule here shadows every column on every
       page, including columns nested inside this very card). */
    .tool-card-marker { display: none; }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tool-card-marker) {
        border-radius: 18px !important;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        margin-bottom: 0.85rem;
    }
    /* A tighter, more contained lift than --shadow-md: the default row gap
       between card grid rows is only ~16px, so a wider hover shadow bled
       visually into the row below. */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tool-card-marker):hover {
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.10);
        transform: translateY(-2px);
    }
    /* Circular arrow buttons on dashboard tool cards: scoped via an adjacent
       marker element (not the ambient wrapper testid, which isn't exclusive
       to bordered containers and was leaking this style onto other buttons) */
    .arrow-btn-marker { display: none; }
    .arrow-btn-marker + div .stButton > button {
        width: 34px !important; height: 34px !important; min-height: 34px !important;
        padding: 0 !important; border-radius: 50% !important;
        background: #ffffff; color: var(--text-m) !important; border: 1px solid var(--border);
        box-shadow: none; font-size: 0.95rem;
    }
    .arrow-btn-marker + div .stButton > button:hover {
        background: var(--primary); color: #ffffff !important; border-color: var(--primary);
        transform: none;
    }

    /* ===== Tool view header (replaces old dark section-header) ===== */
    .tool-header {
        display: flex; align-items: center; gap: 1.1rem;
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 16px; padding: 1.3rem 1.6rem; margin-bottom: 1.3rem;
        box-shadow: var(--shadow-sm);
    }
    .tool-header .tool-icon { width: 52px; height: 52px; font-size: 1.5rem; flex-shrink: 0; }
    .tool-header-title {
        font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700;
        color: var(--text-h) !important; margin: 0;
    }
    .tool-header-desc { color: var(--text-m) !important; font-size: 0.88rem; margin-top: 0.15rem; }

    /* ===== Cards ===== */
    .glass-card-marker { display: none; }
    [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .glass-card-marker) {
        background: var(--surface); border: 1px solid var(--border); border-radius: 18px;
        padding: 1.7rem; margin-bottom: 1.3rem; box-shadow: var(--shadow-sm);
    }

    /* ===== File uploader ===== */
    [data-testid="stFileUploader"] {
        background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 14px; padding: 1.6rem;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover { border-color: var(--primary); background: var(--primary-tint); }

    /* ===== Buttons ===== */
    .stButton > button {
        background: var(--primary); color: #ffffff !important; border: none;
        padding: 0.7rem 1.5rem; font-size: 0.92rem; font-weight: 700; border-radius: 10px;
        box-shadow: 0 4px 14px rgba(37,99,235,0.25); transition: all 0.2s ease;
        font-family: 'Space Grotesk', sans-serif;
    }
    .stButton > button:hover { background: var(--primary-dark); transform: translateY(-1px); }
    .stButton > button[kind="secondary"] {
        background: var(--surface); color: var(--text-b) !important; border: 1px solid var(--border);
        box-shadow: none;
    }
    .stButton > button[kind="secondary"]:hover { background: #f8fafc; border-color: #cbd5e1; }

    /* The blanket [data-testid="stSidebar"] * color rule below recolors every
       descendant, including the <div> Streamlit wraps button labels in - this
       overrides that specifically for primary (active nav) buttons so their
       label stays readable white-on-blue instead of dark-gray-on-blue. */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] * { color: #ffffff !important; }

    .stDownloadButton > button {
        background: #ffffff; color: var(--primary) !important; border: 1.5px solid var(--primary);
        padding: 0.7rem 1.5rem; font-weight: 700; border-radius: 10px; font-family: 'Space Grotesk', sans-serif;
    }
    .stDownloadButton > button:hover { background: var(--primary-tint); }

    /* Sidebar nav buttons: flat list-row look (explicit resets guard against the
       circular card-arrow-button rule above matching here too on some layouts) */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important; height: auto !important; min-height: 2.5rem !important;
        padding: 0.6rem 0.9rem !important; border-radius: 10px !important;
        text-align: left !important; justify-content: flex-start !important;
        font-weight: 600; font-size: 0.86rem; white-space: normal;
    }

    /* ===== Checkbox / toggle ===== */
    [data-testid="stCheckbox"] {
        background: #f8fafc; padding: 0.8rem 1rem; border-radius: 10px; border: 1px solid var(--border);
    }

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] * { color: var(--text-b) !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--text-h) !important; }

    /* Streamlit reserves a tall header row for an optional logo we don't use
       (stLogoSpacer) plus its own padding, leaving what looks like an empty
       white box above our brand row. Shrink it down to just the collapse
       control instead of hiding it (that control's functionality stays). */
    [data-testid="stSidebarHeader"] { padding: 0.4rem 1rem 0 !important; min-height: 0 !important; }
    [data-testid="stLogoSpacer"] { display: none !important; }

    .sb-brand { display: flex; align-items: center; justify-content: space-between; padding: 0.3rem 0 1rem; border-bottom: 1px solid var(--border); margin-bottom: 0.8rem; }
    .sb-brand-left { display: flex; align-items: center; gap: 0.7rem; }
    .sb-avatar {
        width: 38px; height: 38px; border-radius: 10px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    }
    .sb-brand-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1rem; color: var(--text-h) !important; line-height: 1.15; }
    .sb-brand-sub { font-size: 0.63rem; letter-spacing: 1.4px; color: var(--text-m) !important; text-transform: uppercase; }
    .sb-collapse { color: var(--text-m) !important; font-size: 1.05rem; }

    /* .sidebar-card-marker sits as the first element inside a real st.container();
       :has() lets us style that container itself (not just an isolated empty div —
       a plain open/close <div> split across separate st.markdown calls does NOT
       nest the widgets in between, since Streamlit renders each call as its own
       sibling DOM node). */
    .sidebar-card-marker { display: none; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(> [data-testid="element-container"] .sidebar-card-marker) {
        background: #f8fafc; border: 1px solid var(--border); border-radius: 12px; padding: 1rem; margin: 0.7rem 0;
    }
    .sidebar-card-title {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase;
        color: var(--text-m) !important; margin-bottom: 0.6rem;
    }
    .sb-setting-label { font-size: 0.85rem; font-weight: 600; color: var(--text-h) !important; padding-top: 0.35rem; }

    .sb-chip-row { display: flex; flex-wrap: wrap; gap: 0.35rem; }
    .sb-chip {
        font-size: 0.7rem; font-weight: 600; padding: 0.28rem 0.6rem; border-radius: 20px;
        background: #ffffff; border: 1px solid var(--border); color: var(--text-b) !important;
    }

    .sb-toplink {
        display: flex; align-items: center; gap: 0.55rem; padding: 0.6rem 0.75rem; border-radius: 10px;
        font-weight: 600; font-size: 0.88rem; text-decoration: none !important; color: var(--text-b) !important;
    }
    .sb-toplink:hover { background: #f1f5f9; }

    .sb-upgrade {
        background: linear-gradient(135deg, #1d4ed8, #2563eb); border-radius: 14px; padding: 1rem;
        text-align: center; margin-top: 0.7rem;
    }
    .sb-upgrade, .sb-upgrade * { color: #ffffff !important; }
    .sb-upgrade-title { font-weight: 700; font-size: 0.9rem; }
    .sb-upgrade-sub { font-size: 0.73rem; opacity: 0.88; margin-top: 0.2rem; }

    .sb-footer { text-align: center; padding: 0.8rem 0 0.3rem; border-top: 1px solid var(--border); margin-top: 0.6rem; }
    .sb-version-badge {
        display: inline-block; font-size: 0.66rem; font-weight: 700; padding: 0.22rem 0.7rem; border-radius: 20px;
        background: #ecfdf5; border: 1px solid #a7f3d0; color: #059669 !important; margin-bottom: 0.5rem;
    }
    .sb-footer a { color: var(--text-m) !important; font-size: 0.75rem; text-decoration: none !important; }
    .sb-footer a:hover { color: var(--primary) !important; }

    /* ===== Stat cards ===== */
    .stat-card { padding: 1.25rem; border-radius: 14px; text-align: center; border: 1px solid var(--border); background: #f8fafc; }
    .stat-number { font-size: 1.9rem; font-weight: 800; font-family: 'Space Grotesk', sans-serif; color: var(--text-h) !important; }
    .stat-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: var(--text-m) !important; margin-top: 0.3rem; }

    /* ===== File info badge ===== */
    .file-badge { background: var(--primary-tint); border: 1px solid #bfdbfe; padding: 1rem; border-radius: 12px; text-align: center; }
    .file-badge-title { font-size: 0.68rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: var(--primary) !important; }
    .file-badge-name { font-size: 0.88rem; font-weight: 600; color: var(--text-h) !important; margin-top: 0.4rem; word-wrap: break-word; font-family: 'JetBrains Mono', monospace; }

    /* ===== Alerts ===== */
    .stSuccess { background: #ecfdf5 !important; color: #047857 !important; border: 1px solid #a7f3d0 !important; border-radius: 10px !important; }
    .stError { background: #fff1f2 !important; color: #be123c !important; border: 1px solid #fecdd3 !important; border-radius: 10px !important; }
    .stWarning { background: #fffbeb !important; color: #b45309 !important; border: 1px solid #fde68a !important; border-radius: 10px !important; }
    .stInfo { background: var(--primary-tint) !important; color: var(--primary-dark) !important; border: 1px solid #bfdbfe !important; border-radius: 10px !important; }

    hr { border: none; height: 1px; background: var(--border); margin: 1.8rem 0; }

    .stSpinner > div { border-top-color: var(--primary) !important; }
    .stProgress > div > div { background: var(--primary) !important; }

    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid var(--border) !important; }

    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    .app-footer { text-align: center; padding: 2rem; margin-top: 2rem; background: var(--surface); border: 1px solid var(--border); border-radius: 18px; }

    .streamlit-expanderHeader { background: #f8fafc !important; border: 1px solid var(--border) !important; border-radius: 10px !important; font-weight: 600; }

    [data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif !important; color: var(--text-h) !important; }
    [data-testid="stMetricLabel"] { color: var(--text-m) !important; }

    .back-link-wrap { margin-bottom: 0.8rem; }

    @media (max-width: 768px) {
        .hero-title { font-size: 2rem !important; }
        .glass-card { padding: 1.2rem; }
    }
</style>
""", unsafe_allow_html=True)


# ================= SHARED RENDER HELPERS =================
def render_topbar(show_search):
    tcol1, tcol2 = st.columns([3, 2])
    search_query = ""
    with tcol1:
        if show_search:
            search_query = st.text_input(
                "Search",
                placeholder="🔍  Search tools, features or help...   (Ctrl K)",
                key="dash_search",
                label_visibility="collapsed",
            )
        else:
            st.markdown("&nbsp;", unsafe_allow_html=True)
    with tcol2:
        st.markdown("""
        <div class="topbar-actions">
            <div class="topbar-icon-btn">🔔<span class="topbar-dot"></span></div>
            <div class="topbar-icon-btn">🌙</div>
            <div class="topbar-avatar">
                <div class="avatar-circle">SK</div>
                <div>
                    <div class="avatar-name">Shivam Kumar</div>
                    <div class="avatar-plan">Free Plan</div>
                </div>
                <span class="topbar-chevron">▾</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<hr class="topbar-hr"/>', unsafe_allow_html=True)
    return search_query


def render_footer():
    st.divider()
    st.markdown("""
    <div class="app-footer">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: var(--text-h); margin-bottom: 0.4rem;">
            ⚡ DataFlow Pro
        </div>
        <p style="color: var(--text-m); font-size: 0.88rem; margin-bottom: 1.3rem;">
            Built with Python • Streamlit • EasyOCR • Google Translate • scikit-learn
        </p>
        <div style="display: flex; justify-content: center; gap: 3rem; margin: 1.3rem 0; flex-wrap: wrap;">
            <div style="text-align: center;">
                <div style="font-size: 1.6rem; font-weight: 800; color: var(--primary); font-family: 'Space Grotesk', sans-serif;">80-90%</div>
                <div style="color: var(--text-m); font-weight: 600; font-size: 0.76rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Time Saved</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem; font-weight: 800; color: #0891b2; font-family: 'Space Grotesk', sans-serif;">95%+</div>
                <div style="color: var(--text-m); font-weight: 600; font-size: 0.76rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Accuracy</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.6rem; font-weight: 800; color: #059669; font-family: 'Space Grotesk', sans-serif;">19K+</div>
                <div style="color: var(--text-m); font-weight: 600; font-size: 0.76rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Pincodes</div>
            </div>
        </div>
        <p style="font-size: 0.78rem; opacity: 0.6; margin-top: 1.3rem; color: var(--text-m);">
            © 2025 DataFlow Pro • Version 3.0
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_tool_header(tool):
    st.button("← Back to Dashboard", key="back_to_dashboard", on_click=go_to, args=("dashboard",))
    st.markdown(f"""
    <div class="tool-header">
        <div class="tool-icon {tool['accent']}">{tool['icon']}</div>
        <div>
            <div class="tool-header-title">{tool['num']} · {tool['title']}</div>
            <div class="tool-header-desc">{tool['desc']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(f"""
        <div class="sb-brand">
            <div class="sb-brand-left">
                <div class="sb-avatar">📊</div>
                <div>
                    <div class="sb-brand-title">DataFlow Pro</div>
                    <div class="sb-brand-sub">Control Panel</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.button(
        "🏠  Dashboard",
        key="nav_dashboard",
        use_container_width=True,
        type=("primary" if view == "dashboard" else "secondary"),
        on_click=go_to, args=("dashboard",),
    )

    with st.container():
        st.markdown(
            '<div class="sidebar-card-marker"></div><div class="sidebar-card-title">⚙️ Settings</div>',
            unsafe_allow_html=True,
        )

        translate_on = st.toggle("🌐 Hindi ⇄ English Translation", value=True)

        st.markdown('<div class="sb-setting-label" style="margin-top: 0.6rem;">🏭 Industry Preset</div>', unsafe_allow_html=True)
        industry_choice = st.selectbox(
            "Industry Preset",
            INDUSTRY_PRESETS,
            index=0,
            label_visibility="collapsed",
        )
        selected_industry = None if industry_choice.startswith("Generic") else industry_choice

    st.markdown('<div class="sidebar-card-title" style="margin-top: 0.4rem;">🧭 Quick Navigation</div>', unsafe_allow_html=True)
    for tool in TOOL_SECTIONS:
        st.button(
            f"{tool['num']}  {tool['title']}",
            key=f"nav_{tool['key']}",
            use_container_width=True,
            type=("primary" if view == tool["key"] else "secondary"),
            on_click=go_to, args=(tool["key"],),
        )

    with st.container():
        st.markdown("""
        <div class="sidebar-card-marker"></div>
        <div class="sidebar-card-title">✨ Core Features</div>
        <div class="sb-chip-row">
            <span class="sb-chip">🌐 Hindi Translation</span>
            <span class="sb-chip">📞 Phone Cleanup</span>
            <span class="sb-chip">📍 Pincode Mapping</span>
            <span class="sb-chip">🧠 AI Dedup</span>
            <span class="sb-chip">📋 Data Quality</span>
            <span class="sb-chip">🛠️ Column Tools</span>
            <span class="sb-chip">🔄 Format Convert</span>
            <span class="sb-chip">📦 Batch ZIP</span>
        </div>
        """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="sidebar-card-marker"></div>
        <div class="sidebar-card-title">📁 Supported Formats</div>
        <div class="sb-chip-row">
            <span class="sb-chip">.xlsx</span>
            <span class="sb-chip">.csv</span>
            <span class="sb-chip">.pdf</span>
            <span class="sb-chip">.jpg / .png</span>
            <span class="sb-chip">.json</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <a class="sb-toplink" href="https://github.com/ShivamKumar-123/excel-data-automation-ocr/issues" target="_blank">
        🎧 Help &amp; Support
    </a>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-upgrade">
        <div class="sb-upgrade-title">👑 Upgrade to Pro</div>
        <div class="sb-upgrade-sub">Unlock advanced features</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-footer">
        <div class="sb-version-badge">v3.0 · PRO</div><br>
        <a href="https://github.com/ShivamKumar-123/excel-data-automation-ocr" target="_blank">⭐ View on GitHub</a>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 🏠 DASHBOARD VIEW
# =====================================================
if view == "dashboard":
    search_query = render_topbar(show_search=True)

    hero_col1, hero_col2 = st.columns([3, 2])
    with hero_col1:
        st.markdown("""
        <div class="hero-badge">⚡ Powered by AI</div>
        <div class="hero-title">DataFlow <span class="accent">Pro</span></div>
        <div class="hero-tagline">Turn your data into opportunities</div>
        <p class="hero-subtitle">
            Works on any industry's spreadsheet — clean, validate, deduplicate, and export in seconds.
        </p>
        <div class="feature-pills">
            <div class="pill">🌐 Hindi Translation</div>
            <div class="pill">📞 Phone Cleanup</div>
            <div class="pill">📍 Pincode Mapping</div>
            <div class="pill">🔍 OCR Extraction</div>
            <div class="pill">🧠 AI Dedup</div>
            <div class="pill">🏭 Industry Presets</div>
            <div class="pill">📋 Data Quality Report</div>
            <div class="pill">🔄 Format Converter</div>
        </div>
        """, unsafe_allow_html=True)
    with hero_col2:
        if os.path.exists(HERO_ILLUSTRATION_PATH):
            st.image(HERO_ILLUSTRATION_PATH, use_column_width=True)

    st.markdown('<div class="dashboard-eyebrow">Get Started</div>', unsafe_allow_html=True)

    head_col1, head_col2 = st.columns([4, 1])
    with head_col1:
        st.markdown("""
        <div class="dashboard-heading-row">
            <div>
                <h2>Choose a Tool to Begin</h2>
                <p>Powerful data processing tools, built for every industry.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with head_col2:
        st.markdown('<div style="height: 1.9rem;"></div>', unsafe_allow_html=True)
        st.button("View All Tools →", key="view_all_tools", on_click=clear_search, use_container_width=True)

    q = (search_query or "").strip().lower()
    filtered_tools = [
        t for t in TOOL_SECTIONS
        if not q or q in t["title"].lower() or q in t["desc"].lower()
    ]

    if not filtered_tools:
        st.info(f"No tools match \"{search_query}\". Try a different keyword.")
    else:
        for row_start in range(0, len(filtered_tools), 3):
            row_tools = filtered_tools[row_start:row_start + 3]
            cols = st.columns(3)
            for col, tool in zip(cols, row_tools):
                with col:
                    with st.container(border=True):
                        st.markdown('<div class="tool-card-marker"></div>', unsafe_allow_html=True)
                        icon_col, arrow_col = st.columns([5, 1])
                        with icon_col:
                            st.markdown(
                                f'<div class="tool-icon {tool["accent"]}">{tool["icon"]}</div>',
                                unsafe_allow_html=True,
                            )
                        with arrow_col:
                            st.markdown('<div class="arrow-btn-marker"></div>', unsafe_allow_html=True)
                            st.button(
                                "→",
                                key=f"open_{tool['key']}",
                                on_click=go_to, args=(tool["key"],),
                            )
                        st.markdown(f"""
                        <div class="tool-card-heading"><span class="tool-num">{tool['num']}</span>{tool['title']}</div>
                        <div class="tool-card-desc">{tool['desc']}</div>
                        """, unsafe_allow_html=True)

    render_footer()


# =====================================================
# 🔹 SECTION 1: SINGLE FILE CLEAN
# =====================================================
elif view == "sec-1":
    render_topbar(show_search=False)
    tool = TOOL_BY_KEY["sec-1"]
    render_tool_header(tool)

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            single_file = st.file_uploader(
                "📤 Upload Excel / CSV / PDF / Image",
                type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
                key="single"
            )
        with col2:
            if single_file:
                st.markdown(f"""
                <div class="file-badge">
                    <div class="file-badge-title">📄 File Loaded</div>
                    <div class="file-badge-name">{single_file.name}</div>
                </div>
                """, unsafe_allow_html=True)


    if single_file:
        with st.spinner("🔄 Processing file..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                progress_bar.progress(i + 1)

            if single_file.name.lower().endswith((".xlsx", ".csv")):
                df = read_any_table(single_file)
            elif single_file.name.lower().endswith(".pdf"):
                df = pdf_to_df(single_file)
            else:
                df = image_to_df(single_file)

            if df.empty:
                st.error("❌ No data detected in this file.")
            else:
                df = clean_dataframe(df, industry=selected_industry)
                if translate_on:
                    df = translate_hindi_df(df)
                df.drop_duplicates(inplace=True)

                show_detected_fields(df, industry=selected_industry)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-number'>{len(df):,}</div>
                        <div class='stat-label'>Rows</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-number'>{len(df.columns)}</div>
                        <div class='stat-label'>Columns</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-number'>{df.duplicated().sum()}</div>
                        <div class='stat-label'>Duplicates</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.success(f"✅ Processed {len(df):,} rows successfully!")
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(10), use_container_width=True, height=400)

                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        "⬇️ Download Cleaned File",
                        buffer,
                        f"cleaned_{os.path.splitext(single_file.name)[0]}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

    render_footer()


# =====================================================
# 🔹 SECTION 2: MULTIPLE FILES (BATCH)
# =====================================================
elif view == "sec-2":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-2"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        multi_files = st.file_uploader(
            "📤 Upload multiple files (ZIP export)",
            type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="multi"
        )

        if multi_files:
            st.markdown(f"""
            <div class="file-badge" style="max-width: 250px; margin: 1rem auto;">
                <div class="file-badge-title">📦 Files Ready</div>
                <div class="file-badge-name" style="font-size: 2rem;">{len(multi_files)}</div>
            </div>
            """, unsafe_allow_html=True)


    if multi_files:
        zip_buffer = io.BytesIO()
        processed_count = 0

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            with st.spinner(f"🔄 Processing {len(multi_files)} files..."):
                progress_bar = st.progress(0)

                for idx, file in enumerate(multi_files):
                    try:
                        if file.name.lower().endswith((".xlsx", ".csv")):
                            df = read_any_table(file)
                        elif file.name.lower().endswith(".pdf"):
                            df = pdf_to_df(file)
                        else:
                            df = image_to_df(file)

                        if df.empty:
                            st.warning(f"⚠️ No data: {file.name}")
                            continue

                        df = clean_dataframe(df, industry=selected_industry)
                        if translate_on:
                            df = translate_hindi_df(df)
                        df.drop_duplicates(inplace=True)

                        temp = io.BytesIO()
                        df.to_excel(temp, index=False, engine='openpyxl')
                        temp.seek(0)

                        zipf.writestr(
                            f"cleaned_{os.path.splitext(file.name)[0]}.xlsx",
                            temp.read()
                        )
                        processed_count += 1
                        progress_bar.progress((idx + 1) / len(multi_files))

                    except Exception as e:
                        st.warning(f"⚠️ Failed: {file.name} — {str(e)}")

        zip_buffer.seek(0)

        if processed_count > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-number'>{len(multi_files)}</div>
                    <div class='stat-label'>Uploaded</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-number'>{processed_count}</div>
                    <div class='stat-label'>Processed</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-number'>{len(multi_files) - processed_count}</div>
                    <div class='stat-label'>Failed</div>
                </div>
                """, unsafe_allow_html=True)

            st.success(f"✅ Batch complete: {processed_count} of {len(multi_files)} files processed!")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    "⬇️ Download ZIP Archive",
                    zip_buffer,
                    "cleaned_files.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        else:
            st.error("❌ No files processed successfully.")

    render_footer()


# =====================================================
# 🔹 SECTION 3: MERGE FILES
# =====================================================
elif view == "sec-3":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-3"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        merge_files = st.file_uploader(
            "📤 Drop Files to Merge",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key="merge"
        )

        if merge_files:
            st.markdown(f"""
            <div class="file-badge" style="max-width: 250px; margin: 1rem auto;">
                <div class="file-badge-title">🔗 Files to Merge</div>
                <div class="file-badge-name" style="font-size: 2rem;">{len(merge_files)}</div>
            </div>
            """, unsafe_allow_html=True)


    if merge_files:
        dfs = []

        with st.spinner(f"🔄 Merging {len(merge_files)} files..."):
            progress_bar = st.progress(0)

            for idx, file in enumerate(merge_files):
                df = read_any_table(file)
                df = clean_dataframe(df, industry=selected_industry)
                if translate_on:
                    df = translate_hindi_df(df)
                dfs.append(df)
                progress_bar.progress((idx + 1) / len(merge_files))

            merged_df = pd.concat(dfs, ignore_index=True)

        buffer = io.BytesIO()
        merged_df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.success(f"✅ Merged {len(merge_files)} files → {len(merged_df):,} total rows")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                "⬇️ Download Merged File",
                buffer,
                "merged_excel.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    render_footer()


# =====================================================
# 🔹 SECTION 4: ROW EXTRACTION
# =====================================================
elif view == "sec-4":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-4"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        range_file = st.file_uploader(
            "📤 Drop File for Extraction",
            type=["xlsx", "csv"],
            key="range"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            start_row = st.number_input("Start Row", min_value=1, value=1, key="start")
        with col2:
            end_row = st.number_input("End Row", min_value=1, value=10, key="end")


    if range_file and start_row <= end_row:
        df = read_any_table(range_file)
        extracted_df = df.iloc[start_row - 1: end_row]

        buffer = io.BytesIO()
        extracted_df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.success(f"✅ Extracted rows {start_row}–{end_row} ({len(extracted_df)} rows)")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                "⬇️ Download Extracted Rows",
                buffer,
                "extracted_rows.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    elif range_file and start_row > end_row:
        st.error("⚠️ Start row must be less than or equal to end row")

    render_footer()


# =====================================================
# 🔹 SECTION 5: MATCH & REMOVE
# =====================================================
elif view == "sec-5":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-5"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            file1 = st.file_uploader(
                "📤 Upload Reference File (File 1)",
                type=["xlsx", "csv"],
                key="match_file"
            )
        with col2:
            file2 = st.file_uploader(
                "📤 Upload Target File (File 2)",
                type=["xlsx", "csv"],
                key="target_file"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        match_col1, match_col2 = st.columns([1, 2])
        with match_col1:
            match_on = st.multiselect(
                "Match rows on",
                ["phone", "email", "name"],
                default=["phone", "email", "name"],
                key="match_fields_mr",
                help="Only these fields are checked for a match."
            )
        with match_col2:
            name_threshold = st.slider(
                "Name match sensitivity (%)",
                min_value=70, max_value=100, value=90,
                key="name_threshold_mr",
                help="Higher = stricter (fewer, more confident fuzzy-name matches)."
            )


    if file1 and file2:
        with st.spinner("🔍 Analyzing & matching rows..."):
            df1 = read_any_table(file1)
            df2 = read_any_table(file2)

            df1 = clean_dataframe(df1, industry=selected_industry)
            df2 = clean_dataframe(df2, industry=selected_industry)

            if translate_on:
                df1 = translate_hindi_df(df1)
                df2 = translate_hindi_df(df2)

            show_detected_fields(df2, label="Detected Field Types (File 2)", industry=selected_industry)

            updated_df2, report = enterprise_dedup_engine(
                df1, df2,
                name_threshold=name_threshold,
                match_fields=tuple(match_on),
            )

            st.subheader("🔴 Duplicate Highlight Preview")

            if report is not None and not report.empty:
                duplicate_indices = report["row_index"].tolist()
                styled_df = highlight_duplicates(df2, duplicate_indices)
                st.dataframe(styled_df, use_container_width=True, height=400)
            else:
                st.success("No duplicates detected")

            confirm = st.checkbox("Confirm Delete Duplicate Rows")

            if confirm:
                removed_count = len(df2) - len(updated_df2)
                st.success(f"✅ Removed {removed_count} matching rows")

                buffer = io.BytesIO()
                updated_df2.to_excel(buffer, index=False, engine="openpyxl")
                buffer.seek(0)

                st.download_button(
                    "⬇️ Download Cleaned File 2",
                    buffer,
                    "updated_file2.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                if report is not None and not report.empty:
                    report_buffer = io.BytesIO()
                    report.to_excel(report_buffer, index=False, engine="openpyxl")
                    report_buffer.seek(0)

                    st.download_button(
                        "⬇️ Download Duplicate Report",
                        report_buffer,
                        "duplicate_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                st.info("☝️ Tick the confirm box above to enable download of the cleaned file.")

    render_footer()


# =====================================================
# 🔹 SECTION 6: AI SMART DEDUP ENGINE
# =====================================================
elif view == "sec-6":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-6"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)
        dedup_file = st.file_uploader(
            "📤 Upload Excel / CSV File",
            type=["xlsx", "csv"],
            key="ai_dedup"
        )

    if dedup_file:
        df = read_any_table(dedup_file)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns)}")

        show_detected_fields(df, industry=selected_industry)

        ai_col1, ai_col2 = st.columns([1, 2])
        with ai_col1:
            ai_match_on = st.multiselect(
                "Match rows on",
                ["phone", "email", "name"],
                default=["phone", "email", "name"],
                key="match_fields_ai",
                help="Only these fields are checked for duplicates."
            )
        with ai_col2:
            ai_similarity = st.slider(
                "Name similarity sensitivity (%)",
                min_value=80, max_value=99, value=92,
                key="similarity_ai",
                help="Higher = stricter (fewer, more confident near-duplicate names)."
            )

        st.markdown("---")

        run_ai = st.button("🚀 Run AI Dedup Engine")

        if run_ai:
            progress_bar = st.progress(0)

            with st.spinner("🤖 AI analyzing data..."):
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)

                cleaned_df, report = ultra_fast_dedup(
                    df,
                    similarity_threshold=ai_similarity / 100,
                    match_fields=tuple(ai_match_on),
                )

            st.success("✅ AI Dedup Engine Completed")
            st.markdown("---")

            st.subheader("📊 Duplicate Detection Report")
            if not report.empty:
                st.metric("Duplicates Found", f"{len(report)}")
                st.dataframe(report, use_container_width=True, height=300)
            else:
                st.success("No duplicates detected")

            st.markdown("---")

            st.subheader("🧹 Cleaned Data Preview")
            st.dataframe(cleaned_df.head(50), use_container_width=True, height=350)
            st.info(f"Final Rows After Cleaning: {len(cleaned_df):,}")

            st.markdown("---")

            buffer = io.BytesIO()
            cleaned_df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                "⬇️ Download Clean File",
                buffer,
                "cleaned_data.xlsx",
                use_container_width=True
            )

    render_footer()


# =====================================================
# 🔹 SECTION 7: DATA QUALITY REPORT
# =====================================================
elif view == "sec-7":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-7"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)
        dq_file = st.file_uploader(
            "📤 Upload File to Inspect",
            type=["xlsx", "csv"],
            key="dq_file"
        )

    if dq_file:
        raw_df = read_any_table(dq_file)

        if raw_df.empty:
            st.error("❌ No data detected in this file.")
        else:
            summary, invalid = data_quality_report(raw_df, industry=selected_industry)
            issues = int((summary["Invalid"] > 0).sum() + ((summary["Missing"] > 0) & (summary["Invalid"] == 0)).sum())

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Rows", f"{len(raw_df):,}")
            with m2:
                st.metric("Total Columns", f"{len(raw_df.columns)}")
            with m3:
                st.metric("Duplicate Rows", f"{int(raw_df.duplicated().sum()):,}")
            with m4:
                st.metric("Columns w/ Issues", f"{issues}")

            st.subheader("📋 Column Summary")
            st.dataframe(summary, use_container_width=True, hide_index=True)

            st.subheader("🚩 Invalid Value Details")
            if not invalid.empty:
                st.warning(f"⚠️ {len(invalid)} invalid values found in structured fields (email / phone / pincode / GST / PAN / Aadhaar / website).")
                st.dataframe(invalid, use_container_width=True, height=300)

                invalid_buffer = io.BytesIO()
                invalid.to_excel(invalid_buffer, index=False, engine="openpyxl")
                invalid_buffer.seek(0)
                st.download_button(
                    "⬇️ Download Invalid Values Report",
                    invalid_buffer,
                    "invalid_values_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.success("✅ No invalid structured values detected.")

            summary_buffer = io.BytesIO()
            summary.to_excel(summary_buffer, index=False, engine="openpyxl")
            summary_buffer.seek(0)
            st.download_button(
                "⬇️ Download Quality Summary",
                summary_buffer,
                "data_quality_summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    render_footer()


# =====================================================
# 🔹 SECTION 8: COLUMN TOOLS
# =====================================================
elif view == "sec-8":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-8"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)
        ct_file = st.file_uploader(
            "📤 Upload File to Edit",
            type=["xlsx", "csv"],
            key="col_tools_file"
        )

    if ct_file:
        ct_df = read_any_table(ct_file)

        if ct_df.empty:
            st.error("❌ No data detected in this file.")
        else:
            st.markdown("#### 1️⃣ Select & Reorder Columns")
            keep_cols = st.multiselect(
                "Columns to keep (selection order becomes the new column order)",
                list(ct_df.columns),
                default=list(ct_df.columns),
                key="ct_keep_cols"
            )

            st.markdown("#### 2️⃣ Rename Columns")
            rename_source_df = pd.DataFrame({"Original Column": keep_cols, "New Name": keep_cols})
            rename_edited = st.data_editor(
                rename_source_df,
                use_container_width=True,
                hide_index=True,
                key="ct_rename_editor",
                disabled=["Original Column"],
            )

            st.markdown("#### 3️⃣ Find & Replace")
            fr1, fr2, fr3 = st.columns(3)
            with fr1:
                fr_target_col = st.selectbox("In column", ["(All Columns)"] + keep_cols, key="ct_fr_col")
            with fr2:
                find_text = st.text_input("Find", key="ct_find")
            with fr3:
                replace_text = st.text_input("Replace with", key="ct_replace")

            if not keep_cols:
                st.warning("⚠️ Select at least one column to continue.")
            elif st.button("✅ Apply Changes", key="ct_apply"):
                result_df = ct_df[keep_cols].copy()
                rename_map = dict(zip(rename_edited["Original Column"], rename_edited["New Name"]))
                result_df = result_df.rename(columns=rename_map)

                if find_text:
                    target_cols = (
                        list(result_df.columns) if fr_target_col == "(All Columns)"
                        else [rename_map.get(fr_target_col, fr_target_col)]
                    )
                    for c in target_cols:
                        if c in result_df.columns:
                            result_df[c] = result_df[c].astype(str).str.replace(find_text, replace_text, regex=False)

                st.success(f"✅ Applied — {len(result_df.columns)} columns, {len(result_df):,} rows")
                st.dataframe(result_df.head(10), use_container_width=True, height=350)

                ct_buffer = io.BytesIO()
                result_df.to_excel(ct_buffer, index=False, engine="openpyxl")
                ct_buffer.seek(0)
                st.download_button(
                    "⬇️ Download Edited File",
                    ct_buffer,
                    f"edited_{os.path.splitext(ct_file.name)[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    render_footer()


# =====================================================
# 🔹 SECTION 9: FORMAT CONVERTER
# =====================================================
elif view == "sec-9":
    render_topbar(show_search=False)
    render_tool_header(TOOL_BY_KEY["sec-9"])

    with st.container():
        st.markdown('<div class="glass-card-marker"></div>', unsafe_allow_html=True)

        conv_files = st.file_uploader(
            "📤 Upload Excel / CSV file(s)",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key="conv_files"
        )

        cv1, cv2, cv3 = st.columns(3)
        with cv1:
            output_format = st.selectbox("Convert to", ["xlsx", "csv", "json"], key="conv_format")
        with cv2:
            split_sheets = st.checkbox("Split multi-sheet workbooks", key="conv_split")
        with cv3:
            combine_files = st.checkbox(
                "Combine files into one workbook",
                key="conv_combine",
                disabled=(output_format != "xlsx"),
                help="Only available when converting to XLSX."
            )


    if conv_files:
        if combine_files and output_format == "xlsx":
            named_frames = {os.path.splitext(f.name)[0]: read_any_table(f) for f in conv_files}
            combined_buf = build_multi_sheet_excel(named_frames)

            st.success(f"✅ Combined {len(conv_files)} file(s) into one workbook ({len(named_frames)} sheets)")
            st.download_button(
                "⬇️ Download Combined Workbook",
                combined_buf,
                "combined_workbook.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        elif split_sheets:
            zip_buffer = io.BytesIO()
            total_parts = 0

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for f in conv_files:
                    if f.name.lower().endswith(".xlsx"):
                        sheets = read_all_sheets_raw(f)
                    else:
                        sheets = {os.path.splitext(f.name)[0]: read_any_table(f)}

                    for sheet_name, sheet_df in sheets.items():
                        out_bytes, _, ext = dataframe_to_bytes(sheet_df, output_format)
                        zipf.writestr(f"{os.path.splitext(f.name)[0]}_{sheet_name}.{ext}", out_bytes.read())
                        total_parts += 1

            zip_buffer.seek(0)
            st.success(f"✅ Split into {total_parts} file(s)")
            st.download_button(
                "⬇️ Download ZIP",
                zip_buffer,
                "split_files.zip",
                mime="application/zip",
                use_container_width=True
            )

        elif len(conv_files) == 1:
            f = conv_files[0]
            df = read_any_table(f)
            out_bytes, mime, ext = dataframe_to_bytes(df, output_format)

            st.success(f"✅ Converted to .{ext}")
            st.download_button(
                f"⬇️ Download .{ext.upper()} File",
                out_bytes,
                f"{os.path.splitext(f.name)[0]}.{ext}",
                mime=mime,
                use_container_width=True
            )

        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for f in conv_files:
                    df = read_any_table(f)
                    out_bytes, _, ext = dataframe_to_bytes(df, output_format)
                    zipf.writestr(f"{os.path.splitext(f.name)[0]}.{ext}", out_bytes.read())
            zip_buffer.seek(0)

            st.success(f"✅ Converted {len(conv_files)} file(s) to .{output_format}")
            st.download_button(
                "⬇️ Download ZIP",
                zip_buffer,
                f"converted_{output_format}_files.zip",
                mime="application/zip",
                use_container_width=True
            )

    render_footer()
