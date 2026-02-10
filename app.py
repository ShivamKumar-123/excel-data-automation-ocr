
import streamlit as st
import pandas as pd
import io
import zipfile
import os

from main import (
    clean_dataframe,
    translate_hindi_df,
    pdf_to_df,
    image_to_df
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Data Automation Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= CUSTOM CSS - BLACK, YELLOW, PINK, SKY BLUE THEME =================
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&family=Orbitron:wght@400;700;900&display=swap');
    
    /* Global */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background */
    .main {
        background: linear-gradient(135deg, #000000 0%, #0f0f1e 50%, #1a1a2e 100%);
        background-attachment: fixed;
    }
    
    /* Animated Header */
    .header-container {
        background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
        padding: 4rem 2rem;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 
            0 30px 80px rgba(255,215,0,0.5), 
            0 0 120px rgba(135,206,250,0.3),
            inset 0 0 150px rgba(255,105,180,0.15);
        animation: fadeInDown 1.2s ease-in-out;
        position: relative;
        overflow: hidden;
        border: 3px solid transparent;
        background-image: 
            linear-gradient(135deg, #000000 0%, #1a1a2e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB, #FFD700);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg, 
            transparent, 
            rgba(255,215,0,0.25), 
            rgba(135,206,250,0.2), 
            rgba(255,105,180,0.25),
            transparent
        );
        animation: shine 6s infinite linear;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-50px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes glow {
        0%, 100% { 
            text-shadow: 
                0 0 25px rgba(255,215,0,0.9), 
                0 0 35px rgba(255,215,0,0.7), 
                0 0 45px rgba(135,206,250,0.5),
                0 0 55px rgba(255,105,180,0.4); 
        }
        50% { 
            text-shadow: 
                0 0 35px rgba(255,215,0,1), 
                0 0 50px rgba(255,215,0,1), 
                0 0 60px rgba(135,206,250,0.7),
                0 0 70px rgba(255,105,180,0.6),
                0 0 80px rgba(255,215,0,0.5); 
        }
    }
    
    .header-title {
        color: #FFD700;
        font-size: 4.5rem;
        font-weight: 900;
        margin: 0;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 3px;
        text-shadow: 
            3px 3px 6px rgba(0,0,0,0.9),
            0 0 25px rgba(255,215,0,0.7);
        animation: glow 3.5s ease-in-out infinite;
        position: relative;
        z-index: 1;
        background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
    }
    
    .header-subtitle {
        color: #87CEEB;
        font-size: 1.5rem;
        font-weight: 500;
        margin-top: 1.5rem;
        position: relative;
        z-index: 1;
        text-shadow: 
            2px 2px 4px rgba(0,0,0,0.9),
            0 0 20px rgba(135,206,250,0.6);
        letter-spacing: 1.5px;
    }
    
    .header-emoji {
        font-size: 6rem;
        display: inline-block;
        animation: bounce-rotate 3s infinite ease-in-out;
        filter: drop-shadow(0 0 25px rgba(255,215,0,0.9));
        margin-bottom: 1.5rem;
    }
    
    @keyframes bounce-rotate {
        0%, 100% { 
            transform: translateY(0) rotate(0deg) scale(1); 
        }
        25% { 
            transform: translateY(-30px) rotate(10deg) scale(1.1); 
        }
        50% { 
            transform: translateY(0) rotate(0deg) scale(1); 
        }
        75% { 
            transform: translateY(-15px) rotate(-10deg) scale(1.05); 
        }
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        animation: slideUp 1s ease-in-out;
        box-shadow: 0 12px 35px rgba(255,215,0,0.5);
        border: 3px solid rgba(255,215,0,0.4);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.6s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:nth-child(2) {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: #FFFFFF;
        box-shadow: 0 12px 35px rgba(255,105,180,0.5);
        border-color: rgba(255,105,180,0.4);
    }
    
    .feature-card:nth-child(3) {
        background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
        color: #FFFFFF;
        box-shadow: 0 12px 35px rgba(135,206,250,0.5);
        border-color: rgba(135,206,250,0.4);
    }
    
    .feature-card:nth-child(4) {
        background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
        color: #FFFFFF;
        box-shadow: 0 12px 35px rgba(255,215,0,0.6);
        border-color: rgba(255,215,0,0.4);
    }
    
    .feature-card:nth-child(5) {
        background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
        color: #000000;
        box-shadow: 0 12px 35px rgba(135,206,250,0.6);
        border-color: rgba(135,206,250,0.4);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card:hover {
        transform: translateY(-18px) scale(1.1) rotate(3deg);
        box-shadow: 0 30px 60px rgba(255,215,0,0.7);
    }
    
    .feature-card:nth-child(2):hover {
        box-shadow: 0 30px 60px rgba(255,105,180,0.7);
    }
    
    .feature-card:nth-child(3):hover {
        box-shadow: 0 30px 60px rgba(135,206,250,0.7);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        animation: float 3.5s infinite ease-in-out;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(5deg); }
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        letter-spacing: 0.8px;
        font-family: 'Orbitron', sans-serif;
    }
    
    .feature-desc {
        font-size: 1.05rem;
        opacity: 0.95;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Upload Card */
    .upload-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 3.5rem;
        border-radius: 30px;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.7), 
            0 0 40px rgba(255,215,0,0.2),
            inset 0 0 80px rgba(255,215,0,0.05);
        margin-bottom: 3rem;
        transition: all 0.5s ease;
        animation: fadeIn 1.3s ease-in-out;
        border: 3px solid transparent;
        background-image: 
            linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.92) translateY(30px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
    
    .upload-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 
            0 25px 70px rgba(0,0,0,0.8), 
            0 0 60px rgba(255,215,0,0.35),
            inset 0 0 100px rgba(255,215,0,0.08);
    }
    
    .card-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFD700;
        margin-bottom: 2.5rem;
        display: flex;
        align-items: center;
        gap: 20px;
        text-shadow: 
            0 0 20px rgba(255,215,0,0.6),
            3px 3px 6px rgba(0,0,0,0.9);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
    }
    
    .card-icon {
        font-size: 3rem;
        animation: pulse-rotate 2.5s infinite;
        filter: drop-shadow(0 0 15px rgba(255,215,0,0.7));
    }
    
    @keyframes pulse-rotate {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.25) rotate(180deg); }
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #0f0f1e 50%, #1a1a2e 100%);
        border-right: 4px solid rgba(255,215,0,0.4);
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFD700 !important;
        text-shadow: 0 0 15px rgba(255,215,0,0.6);
        font-family: 'Orbitron', sans-serif;
    }
    
    .sidebar-content {
        background: linear-gradient(135deg, rgba(255,215,0,0.18) 0%, rgba(135,206,250,0.12) 100%);
        padding: 2rem;
        border-radius: 18px;
        margin: 1.5rem 0;
        backdrop-filter: blur(12px);
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 8px 25px rgba(255,215,0,0.25);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        border: none;
        padding: 1.2rem 3rem;
        font-size: 1.3rem;
        font-weight: 800;
        border-radius: 50px;
        box-shadow: 0 12px 35px rgba(255,215,0,0.6);
        transition: all 0.4s ease;
        cursor: pointer;
        width: 100%;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
        border: 3px solid rgba(255,215,0,0.5);
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 18px 50px rgba(255,215,0,0.8);
        background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
        border: none;
        padding: 1.2rem 3rem;
        font-size: 1.3rem;
        font-weight: 800;
        border-radius: 50px;
        box-shadow: 0 12px 35px rgba(255,105,180,0.6);
        transition: all 0.4s ease;
        width: 100%;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
        border: 3px solid rgba(255,105,180,0.5);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 18px 50px rgba(255,105,180,0.8);
        background: linear-gradient(135deg, #FF1493 0%, #FF69B4 100%);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(135,206,250,0.1) 0%, rgba(255,215,0,0.1) 100%);
        border: 4px dashed #87CEEB;
        border-radius: 25px;
        padding: 3rem;
        transition: all 0.5s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #FFD700;
        background: linear-gradient(135deg, rgba(135,206,250,0.18) 0%, rgba(255,215,0,0.18) 100%);
        transform: scale(1.04);
        box-shadow: 
            0 0 50px rgba(135,206,250,0.5),
            0 0 70px rgba(255,215,0,0.4);
    }
    
    /* Messages */
    .stSuccess {
        background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 18px;
        animation: slideInRight 0.7s ease-in-out;
        border: 3px solid rgba(135,206,250,0.7);
        box-shadow: 0 10px 30px rgba(135,206,250,0.5);
        font-weight: 600;
    }
    
    .stError {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 18px;
        animation: shake 0.7s ease-in-out;
        border: 3px solid rgba(255,105,180,0.7);
        box-shadow: 0 10px 30px rgba(255,105,180,0.5);
        font-weight: 600;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 1.5rem;
        border-radius: 18px;
        border: 3px solid rgba(255,215,0,0.7);
        box-shadow: 0 10px 30px rgba(255,215,0,0.5);
        font-weight: 700;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(120px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-15px); }
        75% { transform: translateX(15px); }
    }
    
    /* Divider */
    hr {
        margin: 4rem 0;
        border: none;
        height: 4px;
        background: linear-gradient(90deg, transparent, #FFD700, #FF69B4, #87CEEB, #FFD700, transparent);
        box-shadow: 0 0 15px rgba(255,215,0,0.6);
        border-radius: 2px;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #FFD700 !important;
        border-right-color: #FF69B4 !important;
        border-bottom-color: #87CEEB !important;
        border-left-color: transparent !important;
        border-width: 4px !important;
    }
    
    /* Checkbox */
    [data-testid="stCheckbox"] {
        background: rgba(255,215,0,0.15);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid rgba(255,215,0,0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stCheckbox"]:hover {
        background: rgba(255,215,0,0.22);
        border-color: rgba(255,215,0,0.5);
    }
    
    /* Stats Cards */
    .stats-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 12px 40px rgba(255,215,0,0.5);
        border: 3px solid rgba(255,215,0,0.5);
        transition: all 0.4s ease;
        animation: countUp 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .stats-card:hover {
        transform: translateY(-8px) scale(1.08);
        box-shadow: 0 18px 55px rgba(255,215,0,0.7);
    }
    
    .stats-number {
        font-size: 4rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        font-family: 'Orbitron', sans-serif;
    }
    
    .stats-label {
        font-size: 1.2rem;
        opacity: 0.95;
        margin-top: 1rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    @keyframes countUp {
        from {
            opacity: 0;
            transform: scale(0.5) rotate(-15deg);
        }
        to {
            opacity: 1;
            transform: scale(1) rotate(0deg);
        }
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3.5rem;
        margin-top: 5rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 30px;
        backdrop-filter: blur(15px);
        color: #FFD700;
        border: 4px solid transparent;
        background-image: 
            linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    }
    
    .footer h3 {
        color: #FFD700;
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        text-shadow: 0 0 20px rgba(255,215,0,0.6);
    }
    
    .footer p {
        color: #87CEEB;
        font-size: 1.1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 16px;
        height: 16px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(26,26,46,0.9);
        border-radius: 12px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
        border-radius: 12px;
        border: 3px solid rgba(26,26,46,0.6);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
        box-shadow: 0 0 25px rgba(255,215,0,0.7);
        height: 8px !important;
        border-radius: 4px;
    }
    
    /* Info */
    .stInfo {
        background: linear-gradient(135deg, rgba(135,206,250,0.3) 0%, rgba(135,206,250,0.2) 100%);
        border-left: 6px solid #87CEEB;
        color: #87CEEB;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(135,206,250,0.35);
        padding: 1.2rem;
        font-weight: 600;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 12px 45px rgba(0,0,0,0.6);
        border: 3px solid rgba(255,215,0,0.25);
    }
    
    /* File Info Box */
    .file-info-box {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 2rem;
        border-radius: 25px;
        color: #000000;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 12px 40px rgba(255,215,0,0.5);
        border: 4px solid rgba(255,215,0,0.6);
        animation: pulse-glow 2.5s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { 
            box-shadow: 0 12px 40px rgba(255,215,0,0.5);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 18px 55px rgba(255,215,0,0.7);
            transform: scale(1.02);
        }
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #FFD700 !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    p, span, div, label {
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# ================= ANIMATED HEADER =================
st.markdown("""
<div class="header-container">
    <div class="header-emoji">📊</div>
    <h1 class="header-title">Data Automation Pro</h1>
    <p class="header-subtitle">
        🚀 Excel • CSV • PDF • Image | Hindi → English | Phone Cleanup | Pincode Mapping
    </p>
</div>
""", unsafe_allow_html=True)

# ================= FEATURE CARDS =================
st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <div class="feature-title">Hindi Translation</div>
        <div class="feature-desc">Smart Hindi to English conversion</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📞</div>
        <div class="feature-title">Phone Cleanup</div>
        <div class="feature-desc">Standardize phone numbers</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📍</div>
        <div class="feature-title">Pincode Magic</div>
        <div class="feature-desc">Auto State & District mapping</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">OCR Power</div>
        <div class="feature-desc">Extract from images & PDFs</div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📦</div>
        <div class="feature-title">Batch Processing</div>
        <div class="feature-desc">Multiple files ZIP export</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### ⚙️ Settings & Features")
    
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("""
    **✨ Core Features:**
    - ✔ Hindi → English translation
    - ✔ Phone normalization  
    - ✔ Pincode → State & District  
    - ✔ Duplicate removal  
    - ✔ Multi-format support  
    - ✔ Batch ZIP export
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("""
    **📁 Supported Formats:**
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
    
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("""
    **📊 Processing Pipeline:**
    1. 📤 Upload file(s)
    2. 🔍 Auto data extraction
    3. 🧹 Clean & normalize
    4. 💾 Download results
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**💡 Pro Tips:**")
    st.info("✓ Use clear headers\n✓ Batch for efficiency\n✓ Download ZIP for multiple files")

# ================= MAIN CONTENT =================
st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# 🔹 SECTION 1: SINGLE FILE UPLOAD
# ======================================================
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><span class="card-icon">📁</span> Single File Upload</div>', unsafe_allow_html=True)

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
        <div class="file-info-box">
            <div style='font-size: 1.1rem; opacity: 0.9; font-weight: 800;'>📄 FILE LOADED</div>
            <div style='font-size: 1.3rem; font-weight: 900; margin-top: 1rem; word-wrap: break-word;'>{single_file.name}</div>
        </div>
        """, unsafe_allow_html=True)

if single_file:
    with st.spinner("🔄 Processing file... Please wait"):
        try:
            # ---------- READ ----------
            if single_file.name.lower().endswith(".xlsx"):
                df = pd.read_excel(single_file)

            elif single_file.name.lower().endswith(".csv"):
                try:
                    df = pd.read_csv(single_file, encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(single_file, encoding="latin1")

            elif single_file.name.lower().endswith(".pdf"):
                df = pdf_to_df(single_file)

            else:
                df = image_to_df(single_file)

            if df.empty:
                st.error("❌ No data detected in file.")
            else:
                # ---------- CLEAN ----------
                df = clean_dataframe(df)
                if translate_on:
                    df = translate_hindi_df(df)

                df.drop_duplicates(inplace=True)

                # Stats
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class='stats-card' style='background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%); color: white;'>
                        <div class='stats-number'>{len(df)}</div>
                        <div class='stats-label'>ROWS</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class='stats-card' style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: black;'>
                        <div class='stats-number'>{len(df.columns)}</div>
                        <div class='stats-label'>COLUMNS</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class='stats-card' style='background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white;'>
                        <div class='stats-number'>{df.duplicated().sum()}</div>
                        <div class='stats-label'>DUPLICATES</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.success("✅ File processed successfully!")
                
                st.markdown("### 📊 Data Preview (First 10 Rows)")
                st.dataframe(df.head(10), use_container_width=True, height=400)

                # ---------- DOWNLOAD ----------
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)

                output_name = f"cleaned_{os.path.splitext(single_file.name)[0]}.xlsx"
                st.download_button(
                    "⬇️ DOWNLOAD CLEANED EXCEL",
                    data=buffer,
                    file_name=output_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ======================================================
# 🔹 SECTION 2: MULTIPLE FILE UPLOAD (ZIP)
# ======================================================
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title"><span class="card-icon">📦</span> Batch Processing - Multiple Files</div>', unsafe_allow_html=True)

multi_files = st.file_uploader(
    "📤 Upload multiple files (ZIP export)",
    type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key="multiple"
)

if multi_files:
    st.markdown(f"""
    <div class="file-info-box">
        <div style='font-size: 3.5rem; font-weight: 900; font-family: "Orbitron", sans-serif;'>{len(multi_files)}</div>
        <div style='font-size: 1.3rem; opacity: 0.95; font-weight: 800; margin-top: 0.8rem; letter-spacing: 1px;'>FILES READY</div>
    </div>
    """, unsafe_allow_html=True)
    
    zip_buffer = io.BytesIO()
    processed_count = 0

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        with st.spinner("🔄 Processing multiple files..."):
            progress_bar = st.progress(0)
            
            for idx, file in enumerate(multi_files):
                try:
                    # ---------- READ ----------
                    if file.name.lower().endswith(".xlsx"):
                        df = pd.read_excel(file)

                    elif file.name.lower().endswith(".csv"):
                        try:
                            df = pd.read_csv(file, encoding="utf-8")
                        except UnicodeDecodeError:
                            df = pd.read_csv(file, encoding="latin1")

                    elif file.name.lower().endswith(".pdf"):
                        df = pdf_to_df(file)

                    else:
                        df = image_to_df(file)

                    if df.empty:
                        st.warning(f"⚠️ No data: {file.name}")
                        continue

                    # ---------- CLEAN ----------
                    df = clean_dataframe(df)
                    if translate_on:
                        df = translate_hindi_df(df)

                    df.drop_duplicates(inplace=True)

                    # ---------- SAVE ----------
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)

                    clean_name = f"cleaned_{os.path.splitext(file.name)[0]}.xlsx"
                    zipf.writestr(clean_name, excel_buffer.read())
                    processed_count += 1
                    
                    progress_bar.progress((idx + 1) / len(multi_files))
                    
                except Exception as e:
                    st.warning(f"⚠️ Failed: {file.name} - {str(e)}")
            
            progress_bar.empty()

    zip_buffer.seek(0)

    if processed_count > 0:
        # Stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='stats-card' style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: black;'>
                <div class='stats-number'>{len(multi_files)}</div>
                <div class='stats-label'>UPLOADED</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='stats-card' style='background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%); color: white;'>
                <div class='stats-number'>{processed_count}</div>
                <div class='stats-label'>PROCESSED</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='stats-card' style='background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white;'>
                <div class='stats-number'>{len(multi_files) - processed_count}</div>
                <div class='stats-label'>FAILED</div>
            </div>
            """, unsafe_allow_html=True)

        st.success(f"✅ Processed {processed_count} of {len(multi_files)} files!")

        st.download_button(
            "⬇️ DOWNLOAD ZIP PACKAGE",
            data=zip_buffer,
            file_name="cleaned_files.zip",
            mime="application/zip",
            use_container_width=True
        )
    else:
        st.error("❌ No files processed.")

st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <h3 style='margin-bottom: 1.5rem;'>📊 DATA AUTOMATION PRO</h3>
    <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>
        Built with ❤️ using Python • Streamlit • Tesseract • Google Translate
    </p>
    <div style='display: flex; justify-content: center; gap: 3rem; margin: 2rem 0;'>
        <div>
            <div style='font-size: 2.8rem; font-weight: 900; color: #FFD700; font-family: "Orbitron", sans-serif;'>80-90%</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Time Saved</div>
        </div>
        <div>
            <div style='font-size: 2.8rem; font-weight: 900; color: #FF69B4; font-family: "Orbitron", sans-serif;'>95%+</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Accuracy</div>
        </div>
        <div>
            <div style='font-size: 2.8rem; font-weight: 900; color: #87CEEB; font-family: "Orbitron", sans-serif;'>19K+</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Pincodes</div>
        </div>
    </div>
    <p style='font-size: 1rem; opacity: 0.9; margin-top: 2rem; color: #FFD700; font-weight: 700;'>
        © 2024 All Rights Reserved | Version 2.0 Pro
    </p>
</div>
""", unsafe_allow_html=True)

























#Prefect working code is below this is insane

# import streamlit as st
# import pandas as pd
# import io
# import zipfile
# import os

# from main import (
#     clean_dataframe,
#     translate_hindi_df,
#     pdf_to_df,
#     image_to_df
# )

# # ================= PAGE CONFIG =================
# st.set_page_config(
#     page_title="Excel Data Cleaner",
#     page_icon="📄",
#     layout="centered"
# )

# # ================= HEADER =================
# st.markdown(
#     """
#     <h1 style="text-align:center;">📄 Excel / CSV / PDF / Image Data Cleaner</h1>
#     <p style="text-align:center;">
#         Hindi → English • Phone Cleanup • Pincode → State/District
#     </p>
#     """,
#     unsafe_allow_html=True
# )

# st.divider()

# # ================= SIDEBAR =================
# with st.sidebar:
#     st.header("ℹ️ Features")
#     st.markdown(
#         """
#         ✔ Hindi → English conversion  
#         ✔ Phone normalization  
#         ✔ Pincode → State & District  
#         ✔ CSV / Excel / PDF / Image  
#         ✔ No unwanted row deletion  
#         """
#     )

# translate_on = st.sidebar.checkbox(
#     "🔤 Translate Hindi to English",
#     value=True
# )

# st.divider()

# # ======================================================
# # 🔹 SINGLE FILE UPLOAD
# # ======================================================
# st.subheader("📁 Single File Upload")

# single_file = st.file_uploader(
#     "Upload one file",
#     type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"]
# )

# if single_file:
#     with st.spinner("🔄 Processing file..."):
#         # ---------- READ ----------
#         if single_file.name.lower().endswith(".xlsx"):
#             df = pd.read_excel(single_file)

#         elif single_file.name.lower().endswith(".csv"):
#             try:
#                 df = pd.read_csv(single_file, encoding="utf-8")
#             except UnicodeDecodeError:
#                 df = pd.read_csv(single_file, encoding="latin1")

#         elif single_file.name.lower().endswith(".pdf"):
#             df = pdf_to_df(single_file)

#         else:
#             df = image_to_df(single_file)

#         if df.empty:
#             st.error("❌ No data found in file.")
#         else:
#             # ---------- CLEAN ----------
#             df = clean_dataframe(df)
#             if translate_on:
#                 df = translate_hindi_df(df)

#             df.drop_duplicates(inplace=True)

#             st.success(f"✅ Rows processed: {len(df)}")
#             st.dataframe(df.head(10), use_container_width=True)

#             # ---------- DOWNLOAD ----------
#             buffer = io.BytesIO()
#             df.to_excel(buffer, index=False)
#             buffer.seek(0)

#             output_name = f"cleaned_{os.path.splitext(single_file.name)[0]}.xlsx"
#             st.download_button(
#                 "⬇ Download Cleaned Excel",
#                 data=buffer,
#                 file_name=output_name,
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

# st.divider()

# # ======================================================
# # 🔹 MULTIPLE FILE UPLOAD (ZIP OUTPUT)
# # ======================================================
# st.subheader("📂 Multiple Files Upload")

# multi_files = st.file_uploader(
#     "Upload multiple files",
#     type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
#     accept_multiple_files=True
# )

# if multi_files:
#     zip_buffer = io.BytesIO()

#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#         with st.spinner("🔄 Processing multiple files..."):
#             for file in multi_files:
#                 # ---------- READ ----------
#                 if file.name.lower().endswith(".xlsx"):
#                     df = pd.read_excel(file)

#                 elif file.name.lower().endswith(".csv"):
#                     try:
#                         df = pd.read_csv(file, encoding="utf-8")
#                     except UnicodeDecodeError:
#                         df = pd.read_csv(file, encoding="latin1")

#                 elif file.name.lower().endswith(".pdf"):
#                     df = pdf_to_df(file)

#                 else:
#                     df = image_to_df(file)

#                 if df.empty:
#                     continue

#                 # ---------- CLEAN ----------
#                 df = clean_dataframe(df)
#                 if translate_on:
#                     df = translate_hindi_df(df)

#                 df.drop_duplicates(inplace=True)

#                 # ---------- SAVE EACH FILE ----------
#                 excel_buffer = io.BytesIO()
#                 df.to_excel(excel_buffer, index=False)
#                 excel_buffer.seek(0)

#                 clean_name = f"cleaned_{os.path.splitext(file.name)[0]}.xlsx"
#                 zipf.writestr(clean_name, excel_buffer.read())

#     zip_buffer.seek(0)

#     st.success(f"✅ {len(multi_files)} files processed")

#     st.download_button(
#         "⬇ Download All Cleaned Files (ZIP)",
#         data=zip_buffer,
#         file_name="cleaned_files.zip",
#         mime="application/zip"
#     )

# # ================= FOOTER =================
# st.divider()
# st.markdown(
#     """
#     <p style="text-align:center; font-size:0.9em;">
#         Built with ❤️ using Python & Streamlit<br>
#         © 2026
#     </p>
#     """,
#     unsafe_allow_html=True
# )



# issue inside taking csv file inside below code 


# import streamlit as st
# import pandas as pd
# import io
# import zipfile
# import os

# from main import (
#     clean_dataframe,
#     translate_hindi_df,
#     pdf_to_df,
#     image_to_df
# )

# # ================= PAGE CONFIG =================
# st.set_page_config(
#     page_title="Excel Data Cleaner",
#     page_icon="📄",
#     layout="centered"
# )

# # ================= HEADER =================
# st.markdown(
#     """
#     <h1 style="text-align:center;">📄 Excel / PDF / Image / CSV Data Cleaner</h1>
#     <p style="text-align:center;">
#         Hindi → English • Phone cleanup • Pincode → State/District
#     </p>
#     """,
#     unsafe_allow_html=True
# )

# st.divider()

# # ================= SIDEBAR =================
# with st.sidebar:
#     st.header("ℹ️ Features")
#     st.markdown(
#         """
#         ✔ Hindi → English conversion  
#         ✔ Phone normalization  
#         ✔ Pincode → State & District  
#         ✔ CSV / Excel / PDF / Image  
#         ✔ No unwanted row deletion  
#         """
#     )

# translate_on = st.sidebar.checkbox(
#     "🔤 Translate Hindi to English",
#     value=True
# )

# st.divider()

# # ======================================================
# # 🔹 SINGLE FILE UPLOAD
# # ======================================================
# st.subheader("📁 Single File Upload")

# single_file = st.file_uploader(
#     "Upload one file",
#     type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"]
# )

# if single_file:
#     with st.spinner("🔄 Processing file..."):
#         # ---------- READ ----------
#         if single_file.name.lower().endswith(".xlsx"):
#             df = pd.read_excel(single_file)

#         elif single_file.name.lower().endswith(".csv"):
#             df = pd.read_csv(single_file, encoding="utf-8", errors="ignore")

#         elif single_file.name.lower().endswith(".pdf"):
#             df = pdf_to_df(single_file)

#         else:
#             df = image_to_df(single_file)

#         if df.empty:
#             st.error("❌ No data found in file.")
#         else:
#             df = clean_dataframe(df)
#             if translate_on:
#                 df = translate_hindi_df(df)

#             df.drop_duplicates(inplace=True)

#             st.success(f"✅ Rows processed: {len(df)}")
#             st.dataframe(df.head(10), use_container_width=True)

#             buffer = io.BytesIO()
#             df.to_excel(buffer, index=False)
#             buffer.seek(0)

#             output_name = f"cleaned_{os.path.splitext(single_file.name)[0]}.xlsx"
#             st.download_button(
#                 "⬇ Download Cleaned Excel",
#                 data=buffer,
#                 file_name=output_name,
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

# st.divider()

# # ======================================================
# # 🔹 MULTIPLE FILE UPLOAD (ZIP OUTPUT)
# # ======================================================
# st.subheader("📂 Multiple Files Upload")

# multi_files = st.file_uploader(
#     "Upload multiple files",
#     type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
#     accept_multiple_files=True
# )

# if multi_files:
#     zip_buffer = io.BytesIO()

#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#         with st.spinner("🔄 Processing multiple files..."):
#             for file in multi_files:
#                 # ---------- READ ----------
#                 if file.name.lower().endswith(".xlsx"):
#                     df = pd.read_excel(file)

#                 elif file.name.lower().endswith(".csv"):
#                     df = pd.read_csv(file, encoding="utf-8", errors="ignore")

#                 elif file.name.lower().endswith(".pdf"):
#                     df = pdf_to_df(file)

#                 else:
#                     df = image_to_df(file)

#                 if df.empty:
#                     continue

#                 # ---------- CLEAN ----------
#                 df = clean_dataframe(df)
#                 if translate_on:
#                     df = translate_hindi_df(df)

#                 df.drop_duplicates(inplace=True)

#                 # ---------- SAVE EACH FILE ----------
#                 excel_buffer = io.BytesIO()
#                 df.to_excel(excel_buffer, index=False)
#                 excel_buffer.seek(0)

#                 clean_name = f"cleaned_{os.path.splitext(file.name)[0]}.xlsx"
#                 zipf.writestr(clean_name, excel_buffer.read())

#     zip_buffer.seek(0)

#     st.success(f"✅ {len(multi_files)} files processed")

#     st.download_button(
#         "⬇ Download All Cleaned Files (ZIP)",
#         data=zip_buffer,
#         file_name="cleaned_files.zip",
#         mime="application/zip"
#     )

# # ================= FOOTER =================
# st.divider()
# st.markdown(
#     """
#     <p style="text-align:center; font-size:0.9em;">
#         Built with ❤️ using Python & Streamlit<br>
#         © 2026
#     </p>
#     """,
#     unsafe_allow_html=True
# )










