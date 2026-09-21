import streamlit as st
import pandas as pd
import io
import zipfile
import os
import time
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


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
            return ['background-color: rgba(239, 68, 68, 0.25); color: #fca5a5;'] * len(row)
        return [''] * len(row)
    return df.style.apply(highlight_row, axis=1)


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DataFlow Pro — Smart Data Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= MODERN GLASSMORPHISM THEME =================
st.markdown("""
<style>
    /* ===== Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ===== Reset & Global ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ===== App Background ===== */
    .stApp {
        background: linear-gradient(160deg, #0a0a1a 0%, #0d1117 30%, #0f172a 60%, #020617 100%);
        background-attachment: fixed;
    }

    /* Subtle grid pattern */
    .stApp::before {
        content: '';
        position: fixed;
        width: 100%; height: 100%;
        top: 0; left: 0;
        opacity: 0.03;
        background-image:
            linear-gradient(rgba(139, 92, 246, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139, 92, 246, 0.3) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
    }

    /* ===== Typography ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #e2e8f0 !important;
    }

    p, span, div, label {
        color: #cbd5e1;
    }

    /* ===== Hero Header ===== */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 3.5rem 2.5rem;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 2.5rem;
        border: 1px solid rgba(139, 92, 246, 0.2);
        box-shadow:
            0 25px 60px rgba(0, 0, 0, 0.4),
            0 0 80px rgba(139, 92, 246, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
        animation: heroFade 0.8s ease-out;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #8b5cf6, #06b6d4, #10b981, transparent);
    }

    @keyframes heroFade {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(6, 182, 212, 0.2));
        border: 1px solid rgba(139, 92, 246, 0.3);
        padding: 0.4rem 1.2rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #a78bfa;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
    }

    .hero-icon {
        font-size: 3.5rem;
        display: inline-block;
        margin-bottom: 1rem;
        filter: drop-shadow(0 0 20px rgba(139, 92, 246, 0.5));
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0;
        background: linear-gradient(135deg, #e2e8f0 0%, #a78bfa 40%, #06b6d4 70%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        color: #64748b;
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 1rem;
        letter-spacing: 0.5px;
    }

    .hero-subtitle span {
        color: #94a3b8;
        font-weight: 500;
    }

    /* ===== Feature Pills ===== */
    .feature-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        justify-content: center;
        margin: 2rem 0 0.5rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: default;
        border: 1px solid;
    }

    .pill:hover {
        transform: translateY(-3px);
    }

    .pill-violet {
        background: rgba(139, 92, 246, 0.12);
        border-color: rgba(139, 92, 246, 0.25);
        color: #c4b5fd;
    }
    .pill-cyan {
        background: rgba(6, 182, 212, 0.12);
        border-color: rgba(6, 182, 212, 0.25);
        color: #67e8f9;
    }
    .pill-emerald {
        background: rgba(16, 185, 129, 0.12);
        border-color: rgba(16, 185, 129, 0.25);
        color: #6ee7b7;
    }
    .pill-amber {
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.25);
        color: #fcd34d;
    }
    .pill-rose {
        background: rgba(244, 63, 94, 0.12);
        border-color: rgba(244, 63, 94, 0.25);
        color: #fda4af;
    }

    /* ===== Section Headers ===== */
    .section-header {
        margin: 2.5rem 0 1.5rem;
        padding: 1.8rem 2rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(139, 92, 246, 0.15);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 1.5rem;
        animation: sectionSlide 0.6s ease-out;
    }

    @keyframes sectionSlide {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .section-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        min-width: 50px;
    }

    .section-info {
        flex: 1;
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0 !important;
        letter-spacing: -0.5px;
        margin: 0;
    }

    .section-desc {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.3rem;
        font-weight: 400;
    }

    /* ===== Glass Cards ===== */
    .glass-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.7), rgba(30, 41, 59, 0.5));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.12);
        box-shadow:
            0 15px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.03);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(139, 92, 246, 0.25);
        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.4),
            0 0 30px rgba(139, 92, 246, 0.06);
    }

    /* ===== File Uploader ===== */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.5);
        border: 2px dashed rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(139, 92, 246, 0.5);
        background: rgba(139, 92, 246, 0.05);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.1);
    }

    /* ===== Buttons ===== */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%);
        color: #ffffff;
        border: none;
        padding: 0.85rem 2rem;
        font-size: 0.95rem;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.35);
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
        letter-spacing: 0.5px;
        font-family: 'Space Grotesk', sans-serif;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(139, 92, 246, 0.5);
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 50%, #7c3aed 100%);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 50%, #0e7490 100%);
        color: white;
        border: none;
        padding: 0.85rem 2rem;
        font-size: 0.95rem;
        font-weight: 700;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.35);
        transition: all 0.3s ease;
        width: 100%;
        letter-spacing: 0.5px;
        font-family: 'Space Grotesk', sans-serif;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(6, 182, 212, 0.5);
        background: linear-gradient(135deg, #22d3ee 0%, #06b6d4 50%, #0891b2 100%);
    }

    /* ===== Checkbox ===== */
    [data-testid="stCheckbox"] {
        background: rgba(139, 92, 246, 0.06);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid rgba(139, 92, 246, 0.15);
        transition: all 0.3s ease;
    }

    [data-testid="stCheckbox"]:hover {
        background: rgba(139, 92, 246, 0.1);
        border-color: rgba(139, 92, 246, 0.3);
    }

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a 0%, #0d1117 50%, #0f172a 100%);
        border-right: 1px solid rgba(139, 92, 246, 0.15);
    }

    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #a78bfa !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .sidebar-card {
        background: rgba(139, 92, 246, 0.06);
        border: 1px solid rgba(139, 92, 246, 0.12);
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
    }

    /* ===== Number Input ===== */
    .stNumberInput > div > div > input {
        background: rgba(15, 23, 42, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 10px;
        padding: 0.7rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }

    .stNumberInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
        outline: none;
    }

    /* ===== Stat Cards ===== */
    .stat-card {
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
        border: 1px solid;
        animation: statPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .stat-card:hover {
        transform: translateY(-4px);
    }

    @keyframes statPop {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    .stat-violet {
        background: rgba(139, 92, 246, 0.1);
        border-color: rgba(139, 92, 246, 0.25);
    }
    .stat-cyan {
        background: rgba(6, 182, 212, 0.1);
        border-color: rgba(6, 182, 212, 0.25);
    }
    .stat-emerald {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.25);
    }
    .stat-rose {
        background: rgba(244, 63, 94, 0.1);
        border-color: rgba(244, 63, 94, 0.25);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
    }

    .stat-label {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-top: 0.4rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* ===== File Info Badge ===== */
    .file-badge {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 1.2rem;
        border-radius: 14px;
        text-align: center;
    }

    .file-badge-title {
        font-size: 0.75rem;
        color: #6ee7b7;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .file-badge-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #a7f3d0;
        margin-top: 0.5rem;
        word-wrap: break-word;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ===== Alerts ===== */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        color: #6ee7b7 !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 500;
    }

    .stError {
        background: rgba(244, 63, 94, 0.1) !important;
        color: #fda4af !important;
        border: 1px solid rgba(244, 63, 94, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 500;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        color: #fcd34d !important;
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 500;
    }

    /* ===== Divider ===== */
    hr {
        margin: 3rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.3), rgba(6, 182, 212, 0.3), rgba(16, 185, 129, 0.3), transparent);
    }

    /* ===== Spinner ===== */
    .stSpinner > div {
        border-top-color: #8b5cf6 !important;
        border-right-color: #06b6d4 !important;
        border-bottom-color: #10b981 !important;
        border-left-color: transparent !important;
    }

    /* ===== Progress Bar ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
        height: 6px !important;
        border-radius: 3px;
    }

    /* ===== DataFrame ===== */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(139, 92, 246, 0.15) !important;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #a78bfa, #22d3ee);
    }

    /* ===== Footer ===== */
    .app-footer {
        text-align: center;
        padding: 2.5rem;
        margin-top: 3rem;
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.12);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        background: rgba(139, 92, 246, 0.06) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(139, 92, 246, 0.12) !important;
        font-weight: 600;
    }

    /* ===== Metric ===== */
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #a78bfa !important;
    }

    [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }

    /* ===== Responsive ===== */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem !important; }
        .section-title { font-size: 1.2rem !important; }
        .glass-card { padding: 1.2rem; }
        .feature-pills { gap: 0.5rem; }
    }
</style>
""", unsafe_allow_html=True)


# ================= HERO HEADER =================
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚡ Powered by AI</div>
    <div class="hero-icon">⚡</div>
    <div class="hero-title">DataFlow Pro</div>
    <p class="hero-subtitle">
        Works on <span>any industry's</span> spreadsheet — <span>clean</span>, <span>validate</span>, <span>deduplicate</span>, and <span>export</span> in seconds.
    </p>
    <div class="feature-pills">
        <div class="pill pill-violet">🌐 Hindi Translation</div>
        <div class="pill pill-cyan">📞 Phone Cleanup</div>
        <div class="pill pill-emerald">📍 Pincode Mapping</div>
        <div class="pill pill-amber">🔍 OCR Extraction</div>
        <div class="pill pill-rose">🧠 AI Dedup</div>
        <div class="pill pill-violet">🏭 Industry Presets</div>
        <div class="pill pill-cyan">📋 Data Quality Report</div>
        <div class="pill pill-emerald">🔄 Format Converter</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 15px 0;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700;
                        color: #a78bfa; letter-spacing: 1px;">
                ⚡ DataFlow Pro
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px; letter-spacing: 2px; text-transform: uppercase;">
                Control Panel
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("""
    **✨ Core Features**
    - ✔ Hindi → English translation
    - ✔ Phone normalization
    - ✔ Pincode → State & District
    - ✔ Smart duplicate removal
    - ✔ Data quality validation
    - ✔ Column rename / reorder / find & replace
    - ✔ Excel / CSV / JSON conversion
    - ✔ Multi-format support
    - ✔ Batch ZIP export
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("""
    **📁 Supported Formats**
    - 📊 Excel (`.xlsx`)
    - 📄 CSV (`.csv`)
    - 📑 PDF (`.pdf`)
    - 🖼️ Images (`.jpg`, `.png`)
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    translate_on = st.checkbox(
        "🔤 Enable Hindi Translation",
        value=True,
        help="Automatically translate Hindi text to English"
    )

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    industry_choice = st.selectbox(
        "🏭 Industry Preset",
        INDUSTRY_PRESETS,
        index=0,
        help="Sharpens column detection for that industry's typical sheet layout. Generic auto-detection always runs underneath."
    )
    selected_industry = None if industry_choice.startswith("Generic") else industry_choice
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown("""
    **💡 Pro Tip**

    Drag multiple files for instant batch processing. Use clear column headers for best auto-detection.
    """)
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================
# 🔹 SECTION 1: SINGLE FILE CLEAN
# =====================================================
st.markdown("""
    <div class="section-header">
        <div class="section-num">01</div>
        <div class="section-info">
            <div class="section-title">Single File Processing</div>
            <div class="section-desc">Upload and auto-clean any individual file</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

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

            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class='stat-card stat-violet'>
                    <div class='stat-number' style='color: #a78bfa;'>{len(df):,}</div>
                    <div class='stat-label' style='color: #c4b5fd;'>Rows</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='stat-card stat-cyan'>
                    <div class='stat-number' style='color: #67e8f9;'>{len(df.columns)}</div>
                    <div class='stat-label' style='color: #a5f3fc;'>Columns</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class='stat-card stat-rose'>
                    <div class='stat-number' style='color: #fda4af;'>{df.duplicated().sum()}</div>
                    <div class='stat-label' style='color: #fecdd3;'>Duplicates</div>
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


# =====================================================
# 🔹 SECTION 2: MULTIPLE FILES (BATCH)
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">02</div>
        <div class="section-info">
            <div class="section-title">Batch Processing</div>
            <div class="section-desc">Process multiple files at once — export as ZIP</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

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
            <div class='stat-card stat-violet'>
                <div class='stat-number' style='color: #a78bfa;'>{len(multi_files)}</div>
                <div class='stat-label' style='color: #c4b5fd;'>Uploaded</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stat-card stat-emerald'>
                <div class='stat-number' style='color: #6ee7b7;'>{processed_count}</div>
                <div class='stat-label' style='color: #a7f3d0;'>Processed</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='stat-card stat-rose'>
                <div class='stat-number' style='color: #fda4af;'>{len(multi_files) - processed_count}</div>
                <div class='stat-label' style='color: #fecdd3;'>Failed</div>
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


# =====================================================
# 🔹 SECTION 3: MERGE FILES
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">03</div>
        <div class="section-info">
            <div class="section-title">Data Fusion</div>
            <div class="section-desc">Merge multiple datasets into one unified file</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 SECTION 4: ROW EXTRACTION
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">04</div>
        <div class="section-info">
            <div class="section-title">Precision Extract</div>
            <div class="section-desc">Extract specific row ranges from your data</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

if range_file and start_row <= end_row:
    df = read_any_table(range_file)
    extracted_df = df.iloc[start_row - 1 : end_row]

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


# =====================================================
# 🔹 SECTION 5: MATCH & REMOVE
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">05</div>
        <div class="section-info">
            <div class="section-title">Match & Remove</div>
            <div class="section-desc">Remove rows from File 2 that exist in File 1</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 SECTION 6: AI SMART DEDUP ENGINE
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">06</div>
        <div class="section-info">
            <div class="section-title">🧠 AI Smart Dedup</div>
            <div class="section-desc">Enterprise-grade duplicate detection — auto column detection + AI similarity matching</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

dedup_file = st.file_uploader(
    "📤 Upload Excel / CSV File",
    type=["xlsx", "csv"],
    key="ai_dedup"
)

st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 SECTION 7: DATA QUALITY REPORT
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">07</div>
        <div class="section-info">
            <div class="section-title">📋 Data Quality Report</div>
            <div class="section-desc">Inspect any file before cleaning — missing values, detected field types, and invalid entries</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
dq_file = st.file_uploader(
    "📤 Upload File to Inspect",
    type=["xlsx", "csv"],
    key="dq_file"
)
st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 SECTION 8: COLUMN TOOLS
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">08</div>
        <div class="section-info">
            <div class="section-title">🛠️ Column Tools</div>
            <div class="section-desc">Rename, reorder, drop columns, and find &amp; replace values before export</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
ct_file = st.file_uploader(
    "📤 Upload File to Edit",
    type=["xlsx", "csv"],
    key="col_tools_file"
)
st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 SECTION 9: FORMAT CONVERTER
# =====================================================
st.divider()

st.markdown("""
    <div class="section-header">
        <div class="section-num">09</div>
        <div class="section-info">
            <div class="section-title">🔄 Format Converter</div>
            <div class="section-desc">Convert between Excel / CSV / JSON, split multi-sheet workbooks, or combine files into one</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)

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


# =====================================================
# 🔹 FOOTER
# =====================================================
st.divider()

st.markdown("""
<div class="app-footer">
    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700;
            color: #e2e8f0; margin-bottom: 0.5rem;">
        ⚡ DataFlow Pro
    </div>
    <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 1.5rem;">
        Built with Python • Streamlit • EasyOCR • Google Translate • scikit-learn
    </p>
    <div style="display: flex; justify-content: center; gap: 3rem; margin: 1.5rem 0; flex-wrap: wrap;">
        <div style="text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 800; color: #a78bfa; font-family: 'Space Grotesk', sans-serif;">80-90%</div>
            <div style="color: #64748b; font-weight: 600; font-size: 0.8rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Time Saved</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 800; color: #67e8f9; font-family: 'Space Grotesk', sans-serif;">95%+</div>
            <div style="color: #64748b; font-weight: 600; font-size: 0.8rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Accuracy</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 800; color: #6ee7b7; font-family: 'Space Grotesk', sans-serif;">19K+</div>
            <div style="color: #64748b; font-weight: 600; font-size: 0.8rem; margin-top: 0.3rem; letter-spacing: 1px; text-transform: uppercase;">Pincodes</div>
        </div>
    </div>
    <p style="font-size: 0.8rem; opacity: 0.5; margin-top: 1.5rem; color: #94a3b8;">
        © 2025 DataFlow Pro • Version 3.0
    </p>
</div>
""", unsafe_allow_html=True)
