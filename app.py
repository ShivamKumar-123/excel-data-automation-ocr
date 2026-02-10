import streamlit as st
import pandas as pd
import io
import zipfile
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

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

# ================= CUSTOM CSS - RESPONSIVE DESIGN =================
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
    
    /* Animated Header - RESPONSIVE */
    .header-container {
        background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 60px rgba(255,215,0,0.4), 
            0 0 80px rgba(135,206,250,0.2),
            inset 0 0 100px rgba(255,105,180,0.1);
        animation: fadeInDown 1.2s ease-in-out;
        position: relative;
        overflow: hidden;
        border: 2px solid transparent;
        background-image: 
            linear-gradient(135deg, #000000 0%, #1a1a2e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB, #FFD700);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }
    
    @media (min-width: 768px) {
        .header-container {
            padding: 3rem 2rem;
            border-radius: 30px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .header-container {
            padding: 4rem 2rem;
        }
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
            transform: translateY(-30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes glow {
        0%, 100% { 
            text-shadow: 
                0 0 15px rgba(255,215,0,0.8), 
                0 0 25px rgba(255,215,0,0.6), 
                0 0 35px rgba(135,206,250,0.4); 
        }
        50% { 
            text-shadow: 
                0 0 25px rgba(255,215,0,1), 
                0 0 40px rgba(255,215,0,0.9), 
                0 0 50px rgba(135,206,250,0.6),
                0 0 60px rgba(255,105,180,0.5); 
        }
    }
    
    /* Responsive Title */
    .header-title {
        color: #FFD700;
        font-size: 2rem;
        font-weight: 900;
        margin: 0;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        text-shadow: 
            2px 2px 4px rgba(0,0,0,0.9),
            0 0 20px rgba(255,215,0,0.6);
        animation: glow 3.5s ease-in-out infinite;
        position: relative;
        z-index: 1;
        background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
    }
    
    @media (min-width: 480px) {
        .header-title {
            font-size: 2.5rem;
        }
    }
    
    @media (min-width: 768px) {
        .header-title {
            font-size: 3.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .header-title {
            font-size: 4.5rem;
            letter-spacing: 3px;
        }
    }
    
    /* Responsive Subtitle */
    .header-subtitle {
        color: #87CEEB;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
        text-shadow: 
            1px 1px 3px rgba(0,0,0,0.9),
            0 0 15px rgba(135,206,250,0.5);
        letter-spacing: 1px;
    }
    
    @media (min-width: 480px) {
        .header-subtitle {
            font-size: 1.1rem;
        }
    }
    
    @media (min-width: 768px) {
        .header-subtitle {
            font-size: 1.3rem;
            letter-spacing: 1.5px;
        }
    }
    
    @media (min-width: 1024px) {
        .header-subtitle {
            font-size: 1.5rem;
        }
    }
    
    /* Responsive Emoji */
    .header-emoji {
        font-size: 3rem;
        display: inline-block;
        animation: bounce-rotate 3s infinite ease-in-out;
        filter: drop-shadow(0 0 20px rgba(255,215,0,0.8));
        margin-bottom: 1rem;
    }
    
    @media (min-width: 768px) {
        .header-emoji {
            font-size: 5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .header-emoji {
            font-size: 6rem;
            margin-bottom: 1.5rem;
        }
    }
    
    @keyframes bounce-rotate {
        0%, 100% { 
            transform: translateY(0) rotate(0deg) scale(1); 
        }
        25% { 
            transform: translateY(-20px) rotate(10deg) scale(1.05); 
        }
        50% { 
            transform: translateY(0) rotate(0deg) scale(1); 
        }
        75% { 
            transform: translateY(-10px) rotate(-10deg) scale(1.03); 
        }
    }
    
    /* Feature Cards - RESPONSIVE GRID */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    @media (min-width: 480px) {
        .feature-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (min-width: 768px) {
        .feature-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
        }
    }
    
    @media (min-width: 1200px) {
        .feature-grid {
            grid-template-columns: repeat(5, 1fr);
            gap: 2rem;
            margin: 3rem 0;
        }
    }
    
    .feature-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 1.5rem 1rem;
        border-radius: 15px;
        text-align: center;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        animation: slideUp 1s ease-in-out;
        box-shadow: 0 8px 25px rgba(255,215,0,0.4);
        border: 2px solid rgba(255,215,0,0.4);
        position: relative;
        overflow: hidden;
    }
    
    @media (min-width: 768px) {
        .feature-card {
            padding: 2rem 1.5rem;
            border-radius: 20px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .feature-card {
            padding: 2.5rem 2rem;
        }
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
        box-shadow: 0 8px 25px rgba(255,105,180,0.4);
        border-color: rgba(255,105,180,0.4);
    }
    
    .feature-card:nth-child(3) {
        background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
        color: #FFFFFF;
        box-shadow: 0 8px 25px rgba(135,206,250,0.4);
        border-color: rgba(135,206,250,0.4);
    }
    
    .feature-card:nth-child(4) {
        background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
        color: #FFFFFF;
        box-shadow: 0 8px 25px rgba(255,215,0,0.5);
        border-color: rgba(255,215,0,0.4);
    }
    
    .feature-card:nth-child(5) {
        background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
        color: #000000;
        box-shadow: 0 8px 25px rgba(135,206,250,0.5);
        border-color: rgba(135,206,250,0.4);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.05) rotate(2deg);
        box-shadow: 0 20px 45px rgba(255,215,0,0.6);
    }
    
    @media (min-width: 1024px) {
        .feature-card:hover {
            transform: translateY(-18px) scale(1.1) rotate(3deg);
            box-shadow: 0 30px 60px rgba(255,215,0,0.7);
        }
    }
    
    .feature-card:nth-child(2):hover {
        box-shadow: 0 20px 45px rgba(255,105,180,0.6);
    }
    
    .feature-card:nth-child(3):hover {
        box-shadow: 0 20px 45px rgba(135,206,250,0.6);
    }
    
    /* Responsive Feature Icon */
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3.5s infinite ease-in-out;
    }
    
    @media (min-width: 768px) {
        .feature-icon {
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .feature-icon {
            font-size: 4rem;
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-12px) rotate(5deg); }
    }
    
    /* Responsive Feature Title */
    .feature-title {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
        letter-spacing: 0.5px;
        font-family: 'Orbitron', sans-serif;
    }
    
    @media (min-width: 768px) {
        .feature-title {
            font-size: 1.3rem;
            margin-bottom: 1rem;
            letter-spacing: 0.8px;
        }
    }
    
    @media (min-width: 1024px) {
        .feature-title {
            font-size: 1.4rem;
        }
    }
    
    /* Responsive Feature Description */
    .feature-desc {
        font-size: 0.95rem;
        opacity: 0.95;
        line-height: 1.5;
        font-weight: 500;
    }
    
    @media (min-width: 768px) {
        .feature-desc {
            font-size: 1rem;
            line-height: 1.6;
        }
    }
    
    @media (min-width: 1024px) {
        .feature-desc {
            font-size: 1.05rem;
        }
    }
    
    /* CAROUSEL STYLES */
    .carousel-container {
        position: relative;
        width: 100%;
        overflow: hidden;
        margin: 2rem 0;
        border-radius: 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem 1rem;
        box-shadow: 0 15px 45px rgba(0,0,0,0.6);
    }
    
    @media (min-width: 768px) {
        .carousel-container {
            padding: 3rem 2rem;
        }
    }
    
    .carousel-slide {
        display: none;
        animation: fadeIn 0.8s ease-in-out;
    }
    
    .carousel-slide.active {
        display: block;
    }
    
    .carousel-controls {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .carousel-btn {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        border: none;
        color: #000;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(255,215,0,0.4);
    }
    
    .carousel-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(255,215,0,0.6);
    }
    
    .carousel-indicators {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        margin-top: 1.5rem;
    }
    
    .indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: rgba(255,215,0,0.3);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .indicator.active {
        background: #FFD700;
        box-shadow: 0 0 15px rgba(255,215,0,0.8);
        transform: scale(1.3);
    }
    
    /* Upload Card - RESPONSIVE */
    .upload-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        box-shadow: 
            0 15px 45px rgba(0,0,0,0.6), 
            0 0 30px rgba(255,215,0,0.15),
            inset 0 0 60px rgba(255,215,0,0.04);
        margin-bottom: 2rem;
        transition: all 0.5s ease;
        animation: fadeIn 1.3s ease-in-out;
        border: 2px solid transparent;
        background-image: 
            linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
        background-origin: border-box;
        background-clip: padding-box, border-box;
    }
    
    @media (min-width: 768px) {
        .upload-card {
            padding: 2.5rem 2rem;
            border-radius: 25px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .upload-card {
            padding: 3.5rem;
            border-radius: 30px;
            margin-bottom: 3rem;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95) translateY(20px); }
        to { opacity: 1; transform: scale(1) translateY(0); }
    }
    
    .upload-card:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 
            0 20px 55px rgba(0,0,0,0.7), 
            0 0 45px rgba(255,215,0,0.25),
            inset 0 0 80px rgba(255,215,0,0.06);
    }
    
    @media (min-width: 1024px) {
        .upload-card:hover {
            transform: translateY(-10px) scale(1.02);
        }
    }
    
    /* Responsive Card Title */
    .card-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #FFD700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 15px;
        text-shadow: 
            0 0 15px rgba(255,215,0,0.5),
            2px 2px 4px rgba(0,0,0,0.9);
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1.5px;
    }
    
    @media (min-width: 768px) {
        .card-title {
            font-size: 2rem;
            margin-bottom: 2rem;
            gap: 18px;
            letter-spacing: 2px;
        }
    }
    
    @media (min-width: 1024px) {
        .card-title {
            font-size: 2.5rem;
            margin-bottom: 2.5rem;
            gap: 20px;
        }
    }
    
    /* Responsive Card Icon */
    .card-icon {
        font-size: 2rem;
        animation: pulse-rotate 2.5s infinite;
        filter: drop-shadow(0 0 12px rgba(255,215,0,0.6));
    }
    
    @media (min-width: 768px) {
        .card-icon {
            font-size: 2.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .card-icon {
            font-size: 3rem;
            filter: drop-shadow(0 0 15px rgba(255,215,0,0.7));
        }
    }
    
    @keyframes pulse-rotate {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.25) rotate(180deg); }
    }
    
    /* Sidebar - RESPONSIVE */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #0f0f1e 50%, #1a1a2e 100%);
        border-right: 3px solid rgba(255,215,0,0.4);
    }
    
    @media (min-width: 1024px) {
        [data-testid="stSidebar"] {
            border-right-width: 4px;
        }
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
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,215,0,0.3);
        box-shadow: 0 6px 20px rgba(255,215,0,0.2);
    }
    
    @media (min-width: 1024px) {
        .sidebar-content {
            padding: 2rem;
            border-radius: 18px;
            margin: 1.5rem 0;
        }
    }
    
    /* Buttons - RESPONSIVE */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 800;
        border-radius: 40px;
        box-shadow: 0 8px 25px rgba(255,215,0,0.5);
        transition: all 0.4s ease;
        cursor: pointer;
        width: 100%;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
        border: 2px solid rgba(255,215,0,0.5);
    }
    
    @media (min-width: 768px) {
        .stButton > button {
            padding: 1.1rem 2.5rem;
            font-size: 1.2rem;
            border-radius: 45px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .stButton > button {
            padding: 1.2rem 3rem;
            font-size: 1.3rem;
            border-radius: 50px;
            letter-spacing: 1.5px;
        }
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 15px 40px rgba(255,215,0,0.7);
        background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
    }
    
    @media (min-width: 1024px) {
        .stButton > button:hover {
            transform: translateY(-5px) scale(1.03);
            box-shadow: 0 18px 50px rgba(255,215,0,0.8);
        }
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 800;
        border-radius: 40px;
        box-shadow: 0 8px 25px rgba(255,105,180,0.5);
        transition: all 0.4s ease;
        width: 100%;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
        border: 2px solid rgba(255,105,180,0.5);
    }
    
    @media (min-width: 768px) {
        .stDownloadButton > button {
            padding: 1.1rem 2.5rem;
            font-size: 1.2rem;
            border-radius: 45px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .stDownloadButton > button {
            padding: 1.2rem 3rem;
            font-size: 1.3rem;
            border-radius: 50px;
            letter-spacing: 1.5px;
        }
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 15px 40px rgba(255,105,180,0.7);
        background: linear-gradient(135deg, #FF1493 0%, #FF69B4 100%);
    }
    
    /* File Uploader - RESPONSIVE */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(135,206,250,0.1) 0%, rgba(255,215,0,0.1) 100%);
        border: 3px dashed #87CEEB;
        border-radius: 20px;
        padding: 2rem 1rem;
        transition: all 0.5s ease;
    }
    
    @media (min-width: 768px) {
        [data-testid="stFileUploader"] {
            padding: 2.5rem 1.5rem;
            border-width: 4px;
            border-radius: 25px;
        }
    }
    
    @media (min-width: 1024px) {
        [data-testid="stFileUploader"] {
            padding: 3rem;
        }
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #FFD700;
        background: linear-gradient(135deg, rgba(135,206,250,0.18) 0%, rgba(255,215,0,0.18) 100%);
        transform: scale(1.02);
        box-shadow: 
            0 0 35px rgba(135,206,250,0.4),
            0 0 50px rgba(255,215,0,0.3);
    }
    
    @media (min-width: 1024px) {
        [data-testid="stFileUploader"]:hover {
            transform: scale(1.04);
            box-shadow: 
                0 0 50px rgba(135,206,250,0.5),
                0 0 70px rgba(255,215,0,0.4);
        }
    }
    
    /* Messages - RESPONSIVE */
    .stSuccess {
        background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        animation: slideInRight 0.7s ease-in-out;
        border: 2px solid rgba(135,206,250,0.7);
        box-shadow: 0 8px 25px rgba(135,206,250,0.4);
        font-weight: 600;
    }
    
    @media (min-width: 768px) {
        .stSuccess {
            padding: 1.5rem;
            border-radius: 18px;
            border-width: 3px;
        }
    }
    
    .stError {
        background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        animation: shake 0.7s ease-in-out;
        border: 2px solid rgba(255,105,180,0.7);
        box-shadow: 0 8px 25px rgba(255,105,180,0.4);
        font-weight: 600;
    }
    
    @media (min-width: 768px) {
        .stError {
            padding: 1.5rem;
            border-radius: 18px;
            border-width: 3px;
        }
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 1.2rem;
        border-radius: 15px;
        border: 2px solid rgba(255,215,0,0.7);
        box-shadow: 0 8px 25px rgba(255,215,0,0.4);
        font-weight: 700;
    }
    
    @media (min-width: 768px) {
        .stWarning {
            padding: 1.5rem;
            border-radius: 18px;
            border-width: 3px;
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(80px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Stats Cards - RESPONSIVE */
    .stats-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000000;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 30px rgba(255,215,0,0.4);
        border: 2px solid rgba(255,215,0,0.5);
        transition: all 0.4s ease;
        animation: countUp 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    @media (min-width: 768px) {
        .stats-card {
            padding: 2rem;
            border-radius: 22px;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .stats-card {
            padding: 2.5rem;
            border-radius: 25px;
            margin: 1.5rem 0;
        }
    }
    
    .stats-card:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 12px 40px rgba(255,215,0,0.6);
    }
    
    @media (min-width: 1024px) {
        .stats-card:hover {
            transform: translateY(-8px) scale(1.08);
            box-shadow: 0 18px 55px rgba(255,215,0,0.7);
        }
    }
    
    /* Responsive Stats Number */
    .stats-number {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Orbitron', sans-serif;
    }
    
    @media (min-width: 768px) {
        .stats-number {
            font-size: 3.5rem;
        }
    }
    
    @media (min-width: 1024px) {
        .stats-number {
            font-size: 4rem;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        }
    }
    
    /* Responsive Stats Label */
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.95;
        margin-top: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    
    @media (min-width: 768px) {
        .stats-label {
            font-size: 1.1rem;
            margin-top: 1rem;
            letter-spacing: 1px;
        }
    }
    
    @media (min-width: 1024px) {
        .stats-label {
            font-size: 1.2rem;
        }
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
    
    /* Footer - RESPONSIVE */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        backdrop-filter: blur(12px);
        color: #FFD700;
        border: 2px solid transparent;
        background-image: 
            linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
            linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
        background-origin: border-box;
        background-clip: padding-box, border-box;
        box-shadow: 0 15px 45px rgba(0,0,0,0.6);
    }
    
    @media (min-width: 768px) {
        .footer {
            padding: 2.5rem 1.5rem;
            border-radius: 25px;
            margin-top: 4rem;
            border-width: 3px;
        }
    }
    
    @media (min-width: 1024px) {
        .footer {
            padding: 3.5rem;
            border-radius: 30px;
            margin-top: 5rem;
            border-width: 4px;
        }
    }
    
    .footer h3 {
        color: #FFD700;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        text-shadow: 0 0 15px rgba(255,215,0,0.5);
        margin-bottom: 1rem;
    }
    
    @media (min-width: 768px) {
        .footer h3 {
            font-size: 2.2rem;
            margin-bottom: 1.3rem;
        }
    }
    
    @media (min-width: 1024px) {
        .footer h3 {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            text-shadow: 0 0 20px rgba(255,215,0,0.6);
        }
    }
    
    .footer p {
        color: #87CEEB;
        font-size: 1rem;
    }
    
    @media (min-width: 768px) {
        .footer p {
            font-size: 1.05rem;
        }
    }
    
    @media (min-width: 1024px) {
        .footer p {
            font-size: 1.1rem;
        }
    }
    
    /* Divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #FFD700, #FF69B4, #87CEEB, #FFD700, transparent);
        box-shadow: 0 0 12px rgba(255,215,0,0.5);
        border-radius: 2px;
    }
    
    @media (min-width: 1024px) {
        hr {
            margin: 4rem 0;
            height: 4px;
            box-shadow: 0 0 15px rgba(255,215,0,0.6);
        }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    @media (min-width: 1024px) {
        ::-webkit-scrollbar {
            width: 16px;
            height: 16px;
        }
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(26,26,46,0.9);
        border-radius: 10px;
    }
    
    @media (min-width: 1024px) {
        ::-webkit-scrollbar-track {
            border-radius: 12px;
        }
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
        border-radius: 10px;
        border: 2px solid rgba(26,26,46,0.6);
    }
    
    @media (min-width: 1024px) {
        ::-webkit-scrollbar-thumb {
            border-radius: 12px;
            border-width: 3px;
        }
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
    }
    
    /* File Info Box - RESPONSIVE */
    .file-info-box {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 1.5rem;
        border-radius: 20px;
        color: #000000;
        text-align: center;
        margin-top: 1.5rem;
        box-shadow: 0 8px 30px rgba(255,215,0,0.4);
        border: 3px solid rgba(255,215,0,0.6);
        animation: pulse-glow 2.5s infinite;
    }
    
    @media (min-width: 768px) {
        .file-info-box {
            padding: 1.8rem;
            border-radius: 22px;
        }
    }
    
    @media (min-width: 1024px) {
        .file-info-box {
            padding: 2rem;
            border-radius: 25px;
            margin-top: 2rem;
            border-width: 4px;
        }
    }
    
    @keyframes pulse-glow {
        0%, 100% { 
            box-shadow: 0 8px 30px rgba(255,215,0,0.4);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 12px 45px rgba(255,215,0,0.6);
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
    
    /* Plotly Charts - Dark Theme */
    .js-plotly-plot .plotly {
        background: transparent !important;
    }
    
    /* Info Box */
    .stInfo {
        background: linear-gradient(135deg, rgba(135,206,250,0.3) 0%, rgba(135,206,250,0.2) 100%);
        border-left: 5px solid #87CEEB;
        color: #87CEEB;
        border-radius: 10px;
        box-shadow: 0 6px 20px rgba(135,206,250,0.3);
        padding: 1rem;
        font-weight: 600;
    }
    
    @media (min-width: 768px) {
        .stInfo {
            border-left-width: 6px;
            border-radius: 12px;
            padding: 1.2rem;
        }
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

# ================= ANALYTICS CAROUSEL =================
st.markdown("<br>", unsafe_allow_html=True)

# Initialize session state for carousel
if 'carousel_index' not in st.session_state:
    st.session_state.carousel_index = 0

def create_sample_data():
    """Generate sample analytics data"""
    # Processing trends
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    processing_data = pd.DataFrame({
        'Date': dates,
        'Files Processed': np.random.randint(50, 200, 30),
        'Success Rate': np.random.uniform(85, 99, 30),
        'Avg Processing Time (s)': np.random.uniform(2, 8, 30)
    })
    
    # File type distribution
    file_types = pd.DataFrame({
        'Type': ['Excel', 'CSV', 'PDF', 'Images'],
        'Count': [450, 380, 290, 180],
        'Percentage': [35, 30, 22, 13]
    })
    
    # Feature usage
    features = pd.DataFrame({
        'Feature': ['Hindi Translation', 'Phone Cleanup', 'Pincode Mapping', 'Duplicate Removal', 'OCR'],
        'Usage': [850, 920, 780, 1050, 560]
    })
    
    # Monthly stats
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_data = pd.DataFrame({
        'Month': months,
        'Files': [1200, 1450, 1680, 1920, 2100, 2350],
        'Users': [45, 52, 61, 68, 75, 82]
    })
    
    return processing_data, file_types, features, monthly_data

processing_data, file_types, features, monthly_data = create_sample_data()

# Carousel container
st.markdown('<div class="carousel-container">', unsafe_allow_html=True)

# Chart 1: Processing Trends
if st.session_state.carousel_index == 0:
    st.markdown('<div class="carousel-slide active">', unsafe_allow_html=True)
    st.markdown("### 📈 Daily Processing Trends")
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=processing_data['Date'],
        y=processing_data['Files Processed'],
        mode='lines+markers',
        name='Files Processed',
        line=dict(color='#FFD700', width=3),
        marker=dict(size=8, color='#FFD700', line=dict(width=2, color='#FFA500'))
    ))
    
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', size=12),
        xaxis=dict(
            gridcolor='rgba(255,215,0,0.1)',
            showgrid=True,
            title='Date'
        ),
        yaxis=dict(
            gridcolor='rgba(255,215,0,0.1)',
            showgrid=True,
            title='Files Processed'
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 2: File Type Distribution
elif st.session_state.carousel_index == 1:
    st.markdown('<div class="carousel-slide active">', unsafe_allow_html=True)
    st.markdown("### 📊 File Type Distribution")
    
    fig2 = go.Figure(data=[go.Pie(
        labels=file_types['Type'],
        values=file_types['Count'],
        hole=0.4,
        marker=dict(
            colors=['#FFD700', '#FF69B4', '#87CEEB', '#FFA500'],
            line=dict(color='#000000', width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='#000000', family='Orbitron')
    )])
    
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', size=12),
        showlegend=True,
        legend=dict(
            font=dict(color='#FFFFFF'),
            bgcolor='rgba(26,26,46,0.6)'
        ),
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 3: Feature Usage
elif st.session_state.carousel_index == 2:
    st.markdown('<div class="carousel-slide active">', unsafe_allow_html=True)
    st.markdown("### 🎯 Feature Usage Statistics")
    
    fig3 = go.Figure(data=[go.Bar(
        x=features['Feature'],
        y=features['Usage'],
        marker=dict(
            color=['#FFD700', '#FF69B4', '#87CEEB', '#FFA500', '#FF1493'],
            line=dict(color='#000000', width=2)
        ),
        text=features['Usage'],
        textposition='outside',
        textfont=dict(size=14, color='#FFFFFF', family='Orbitron')
    )])
    
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', size=12),
        xaxis=dict(
            gridcolor='rgba(255,215,0,0.1)',
            title='Feature',
            tickangle=-15
        ),
        yaxis=dict(
            gridcolor='rgba(255,215,0,0.1)',
            showgrid=True,
            title='Usage Count'
        ),
        height=400
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chart 4: Monthly Growth
elif st.session_state.carousel_index == 3:
    st.markdown('<div class="carousel-slide active">', unsafe_allow_html=True)
    st.markdown("### 📅 Monthly Growth Metrics")
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Files'],
        name='Files Processed',
        marker=dict(color='#FFD700', line=dict(color='#000000', width=2)),
        yaxis='y'
    ))
    
    fig4.add_trace(go.Scatter(
        x=monthly_data['Month'],
        y=monthly_data['Users'],
        name='Active Users',
        mode='lines+markers',
        line=dict(color='#FF69B4', width=3),
        marker=dict(size=10, color='#FF69B4', line=dict(width=2, color='#FF1493')),
        yaxis='y2'
    ))
    
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', size=12),
        xaxis=dict(
            gridcolor='rgba(255,215,0,0.1)',
            title='Month'
        ),
        yaxis=dict(
            title='Files Processed',
            gridcolor='rgba(255,215,0,0.1)',
            showgrid=True
        ),
        yaxis2=dict(
            title='Active Users',
            overlaying='y',
            side='right',
            gridcolor='rgba(255,105,180,0.1)'
        ),
        hovermode='x unified',
        height=400,
        legend=dict(
            font=dict(color='#FFFFFF'),
            bgcolor='rgba(26,26,46,0.6)'
        )
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Carousel controls
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("◀ Previous", key="prev_chart"):
        st.session_state.carousel_index = (st.session_state.carousel_index - 1) % 4
        st.rerun()

with col2:
    # Indicators
    indicators_html = '<div class="carousel-indicators">'
    for i in range(4):
        active_class = 'active' if i == st.session_state.carousel_index else ''
        indicators_html += f'<div class="indicator {active_class}"></div>'
    indicators_html += '</div>'
    st.markdown(indicators_html, unsafe_allow_html=True)

with col3:
    if st.button("Next ▶", key="next_chart"):
        st.session_state.carousel_index = (st.session_state.carousel_index + 1) % 4
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

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
    <div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem; margin: 2rem 0;'>
        <div style='min-width: 120px;'>
            <div style='font-size: 2.2rem; font-weight: 900; color: #FFD700; font-family: "Orbitron", sans-serif;'>80-90%</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1rem;'>Time Saved</div>
        </div>
        <div style='min-width: 120px;'>
            <div style='font-size: 2.2rem; font-weight: 900; color: #FF69B4; font-family: "Orbitron", sans-serif;'>95%+</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1rem;'>Accuracy</div>
        </div>
        <div style='min-width: 120px;'>
            <div style='font-size: 2.2rem; font-weight: 900; color: #87CEEB; font-family: "Orbitron", sans-serif;'>19K+</div>
            <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1rem;'>Pincodes</div>
        </div>
    </div>
    <p style='font-size: 1rem; opacity: 0.9; margin-top: 2rem; color: #FFD700; font-weight: 700;'>
        © 2024 All Rights Reserved | Version 2.0 Pro
    </p>
</div>
""", unsafe_allow_html=True)













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
#     page_title="Data Automation Pro",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ================= CUSTOM CSS - BLACK, YELLOW, PINK, SKY BLUE THEME =================
# st.markdown("""
# <style>
#     /* Import Fonts */
#     @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&family=Orbitron:wght@400;700;900&display=swap');
    
#     /* Global */
#     html, body, [class*="css"] {
#         font-family: 'Poppins', sans-serif;
#     }
    
#     /* Main Background */
#     .main {
#         background: linear-gradient(135deg, #000000 0%, #0f0f1e 50%, #1a1a2e 100%);
#         background-attachment: fixed;
#     }
    
#     /* Animated Header */
#     .header-container {
#         background: linear-gradient(135deg, #000000 0%, #1a1a2e 100%);
#         padding: 4rem 2rem;
#         border-radius: 30px;
#         text-align: center;
#         margin-bottom: 3rem;
#         box-shadow: 
#             0 30px 80px rgba(255,215,0,0.5), 
#             0 0 120px rgba(135,206,250,0.3),
#             inset 0 0 150px rgba(255,105,180,0.15);
#         animation: fadeInDown 1.2s ease-in-out;
#         position: relative;
#         overflow: hidden;
#         border: 3px solid transparent;
#         background-image: 
#             linear-gradient(135deg, #000000 0%, #1a1a2e 100%),
#             linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB, #FFD700);
#         background-origin: border-box;
#         background-clip: padding-box, border-box;
#     }
    
#     .header-container::before {
#         content: '';
#         position: absolute;
#         top: -50%;
#         left: -50%;
#         width: 200%;
#         height: 200%;
#         background: linear-gradient(
#             45deg, 
#             transparent, 
#             rgba(255,215,0,0.25), 
#             rgba(135,206,250,0.2), 
#             rgba(255,105,180,0.25),
#             transparent
#         );
#         animation: shine 6s infinite linear;
#     }
    
#     @keyframes shine {
#         0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
#         100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
#     }
    
#     @keyframes fadeInDown {
#         from {
#             opacity: 0;
#             transform: translateY(-50px) scale(0.95);
#         }
#         to {
#             opacity: 1;
#             transform: translateY(0) scale(1);
#         }
#     }
    
#     @keyframes glow {
#         0%, 100% { 
#             text-shadow: 
#                 0 0 25px rgba(255,215,0,0.9), 
#                 0 0 35px rgba(255,215,0,0.7), 
#                 0 0 45px rgba(135,206,250,0.5),
#                 0 0 55px rgba(255,105,180,0.4); 
#         }
#         50% { 
#             text-shadow: 
#                 0 0 35px rgba(255,215,0,1), 
#                 0 0 50px rgba(255,215,0,1), 
#                 0 0 60px rgba(135,206,250,0.7),
#                 0 0 70px rgba(255,105,180,0.6),
#                 0 0 80px rgba(255,215,0,0.5); 
#         }
#     }
    
#     .header-title {
#         color: #FFD700;
#         font-size: 4.5rem;
#         font-weight: 900;
#         margin: 0;
#         font-family: 'Orbitron', sans-serif;
#         letter-spacing: 3px;
#         text-shadow: 
#             3px 3px 6px rgba(0,0,0,0.9),
#             0 0 25px rgba(255,215,0,0.7);
#         animation: glow 3.5s ease-in-out infinite;
#         position: relative;
#         z-index: 1;
#         background: linear-gradient(45deg, #FFD700, #FFA500, #FFD700);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         background-clip: text;
#         text-transform: uppercase;
#     }
    
#     .header-subtitle {
#         color: #87CEEB;
#         font-size: 1.5rem;
#         font-weight: 500;
#         margin-top: 1.5rem;
#         position: relative;
#         z-index: 1;
#         text-shadow: 
#             2px 2px 4px rgba(0,0,0,0.9),
#             0 0 20px rgba(135,206,250,0.6);
#         letter-spacing: 1.5px;
#     }
    
#     .header-emoji {
#         font-size: 6rem;
#         display: inline-block;
#         animation: bounce-rotate 3s infinite ease-in-out;
#         filter: drop-shadow(0 0 25px rgba(255,215,0,0.9));
#         margin-bottom: 1.5rem;
#     }
    
#     @keyframes bounce-rotate {
#         0%, 100% { 
#             transform: translateY(0) rotate(0deg) scale(1); 
#         }
#         25% { 
#             transform: translateY(-30px) rotate(10deg) scale(1.1); 
#         }
#         50% { 
#             transform: translateY(0) rotate(0deg) scale(1); 
#         }
#         75% { 
#             transform: translateY(-15px) rotate(-10deg) scale(1.05); 
#         }
#     }
    
#     /* Feature Cards */
#     .feature-grid {
#         display: grid;
#         grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
#         gap: 2rem;
#         margin: 3rem 0;
#     }
    
#     .feature-card {
#         background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#         color: #000000;
#         padding: 2.5rem 2rem;
#         border-radius: 20px;
#         text-align: center;
#         transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
#         cursor: pointer;
#         animation: slideUp 1s ease-in-out;
#         box-shadow: 0 12px 35px rgba(255,215,0,0.5);
#         border: 3px solid rgba(255,215,0,0.4);
#         position: relative;
#         overflow: hidden;
#     }
    
#     .feature-card::before {
#         content: '';
#         position: absolute;
#         top: 0;
#         left: -100%;
#         width: 100%;
#         height: 100%;
#         background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
#         transition: left 0.6s;
#     }
    
#     .feature-card:hover::before {
#         left: 100%;
#     }
    
#     .feature-card:nth-child(2) {
#         background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
#         color: #FFFFFF;
#         box-shadow: 0 12px 35px rgba(255,105,180,0.5);
#         border-color: rgba(255,105,180,0.4);
#     }
    
#     .feature-card:nth-child(3) {
#         background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
#         color: #FFFFFF;
#         box-shadow: 0 12px 35px rgba(135,206,250,0.5);
#         border-color: rgba(135,206,250,0.4);
#     }
    
#     .feature-card:nth-child(4) {
#         background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
#         color: #FFFFFF;
#         box-shadow: 0 12px 35px rgba(255,215,0,0.6);
#         border-color: rgba(255,215,0,0.4);
#     }
    
#     .feature-card:nth-child(5) {
#         background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
#         color: #000000;
#         box-shadow: 0 12px 35px rgba(135,206,250,0.6);
#         border-color: rgba(135,206,250,0.4);
#     }
    
#     @keyframes slideUp {
#         from {
#             opacity: 0;
#             transform: translateY(50px);
#         }
#         to {
#             opacity: 1;
#             transform: translateY(0);
#         }
#     }
    
#     .feature-card:hover {
#         transform: translateY(-18px) scale(1.1) rotate(3deg);
#         box-shadow: 0 30px 60px rgba(255,215,0,0.7);
#     }
    
#     .feature-card:nth-child(2):hover {
#         box-shadow: 0 30px 60px rgba(255,105,180,0.7);
#     }
    
#     .feature-card:nth-child(3):hover {
#         box-shadow: 0 30px 60px rgba(135,206,250,0.7);
#     }
    
#     .feature-icon {
#         font-size: 4rem;
#         margin-bottom: 1.5rem;
#         display: inline-block;
#         animation: float 3.5s infinite ease-in-out;
#     }
    
#     @keyframes float {
#         0%, 100% { transform: translateY(0px) rotate(0deg); }
#         50% { transform: translateY(-12px) rotate(5deg); }
#     }
    
#     .feature-title {
#         font-size: 1.4rem;
#         font-weight: 800;
#         margin-bottom: 1rem;
#         letter-spacing: 0.8px;
#         font-family: 'Orbitron', sans-serif;
#     }
    
#     .feature-desc {
#         font-size: 1.05rem;
#         opacity: 0.95;
#         line-height: 1.6;
#         font-weight: 500;
#     }
    
#     /* Upload Card */
#     .upload-card {
#         background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
#         padding: 3.5rem;
#         border-radius: 30px;
#         box-shadow: 
#             0 20px 60px rgba(0,0,0,0.7), 
#             0 0 40px rgba(255,215,0,0.2),
#             inset 0 0 80px rgba(255,215,0,0.05);
#         margin-bottom: 3rem;
#         transition: all 0.5s ease;
#         animation: fadeIn 1.3s ease-in-out;
#         border: 3px solid transparent;
#         background-image: 
#             linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
#             linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
#         background-origin: border-box;
#         background-clip: padding-box, border-box;
#     }
    
#     @keyframes fadeIn {
#         from { opacity: 0; transform: scale(0.92) translateY(30px); }
#         to { opacity: 1; transform: scale(1) translateY(0); }
#     }
    
#     .upload-card:hover {
#         transform: translateY(-10px) scale(1.02);
#         box-shadow: 
#             0 25px 70px rgba(0,0,0,0.8), 
#             0 0 60px rgba(255,215,0,0.35),
#             inset 0 0 100px rgba(255,215,0,0.08);
#     }
    
#     .card-title {
#         font-size: 2.5rem;
#         font-weight: 800;
#         color: #FFD700;
#         margin-bottom: 2.5rem;
#         display: flex;
#         align-items: center;
#         gap: 20px;
#         text-shadow: 
#             0 0 20px rgba(255,215,0,0.6),
#             3px 3px 6px rgba(0,0,0,0.9);
#         font-family: 'Orbitron', sans-serif;
#         letter-spacing: 2px;
#     }
    
#     .card-icon {
#         font-size: 3rem;
#         animation: pulse-rotate 2.5s infinite;
#         filter: drop-shadow(0 0 15px rgba(255,215,0,0.7));
#     }
    
#     @keyframes pulse-rotate {
#         0%, 100% { transform: scale(1) rotate(0deg); }
#         50% { transform: scale(1.25) rotate(180deg); }
#     }
    
#     /* Sidebar */
#     [data-testid="stSidebar"] {
#         background: linear-gradient(180deg, #000000 0%, #0f0f1e 50%, #1a1a2e 100%);
#         border-right: 4px solid rgba(255,215,0,0.4);
#     }
    
#     [data-testid="stSidebar"] * {
#         color: #FFFFFF !important;
#     }
    
#     [data-testid="stSidebar"] h1,
#     [data-testid="stSidebar"] h2,
#     [data-testid="stSidebar"] h3 {
#         color: #FFD700 !important;
#         text-shadow: 0 0 15px rgba(255,215,0,0.6);
#         font-family: 'Orbitron', sans-serif;
#     }
    
#     .sidebar-content {
#         background: linear-gradient(135deg, rgba(255,215,0,0.18) 0%, rgba(135,206,250,0.12) 100%);
#         padding: 2rem;
#         border-radius: 18px;
#         margin: 1.5rem 0;
#         backdrop-filter: blur(12px);
#         border: 2px solid rgba(255,215,0,0.3);
#         box-shadow: 0 8px 25px rgba(255,215,0,0.25);
#     }
    
#     /* Buttons */
#     .stButton > button {
#         background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#         color: #000000;
#         border: none;
#         padding: 1.2rem 3rem;
#         font-size: 1.3rem;
#         font-weight: 800;
#         border-radius: 50px;
#         box-shadow: 0 12px 35px rgba(255,215,0,0.6);
#         transition: all 0.4s ease;
#         cursor: pointer;
#         width: 100%;
#         letter-spacing: 1.5px;
#         text-transform: uppercase;
#         font-family: 'Orbitron', sans-serif;
#         border: 3px solid rgba(255,215,0,0.5);
#     }
    
#     .stButton > button:hover {
#         transform: translateY(-5px) scale(1.03);
#         box-shadow: 0 18px 50px rgba(255,215,0,0.8);
#         background: linear-gradient(135deg, #FFA500 0%, #FFD700 100%);
#     }
    
#     .stDownloadButton > button {
#         background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
#         color: white;
#         border: none;
#         padding: 1.2rem 3rem;
#         font-size: 1.3rem;
#         font-weight: 800;
#         border-radius: 50px;
#         box-shadow: 0 12px 35px rgba(255,105,180,0.6);
#         transition: all 0.4s ease;
#         width: 100%;
#         letter-spacing: 1.5px;
#         text-transform: uppercase;
#         font-family: 'Orbitron', sans-serif;
#         border: 3px solid rgba(255,105,180,0.5);
#     }
    
#     .stDownloadButton > button:hover {
#         transform: translateY(-5px) scale(1.03);
#         box-shadow: 0 18px 50px rgba(255,105,180,0.8);
#         background: linear-gradient(135deg, #FF1493 0%, #FF69B4 100%);
#     }
    
#     /* File Uploader */
#     [data-testid="stFileUploader"] {
#         background: linear-gradient(135deg, rgba(135,206,250,0.1) 0%, rgba(255,215,0,0.1) 100%);
#         border: 4px dashed #87CEEB;
#         border-radius: 25px;
#         padding: 3rem;
#         transition: all 0.5s ease;
#     }
    
#     [data-testid="stFileUploader"]:hover {
#         border-color: #FFD700;
#         background: linear-gradient(135deg, rgba(135,206,250,0.18) 0%, rgba(255,215,0,0.18) 100%);
#         transform: scale(1.04);
#         box-shadow: 
#             0 0 50px rgba(135,206,250,0.5),
#             0 0 70px rgba(255,215,0,0.4);
#     }
    
#     /* Messages */
#     .stSuccess {
#         background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%);
#         color: white;
#         padding: 1.5rem;
#         border-radius: 18px;
#         animation: slideInRight 0.7s ease-in-out;
#         border: 3px solid rgba(135,206,250,0.7);
#         box-shadow: 0 10px 30px rgba(135,206,250,0.5);
#         font-weight: 600;
#     }
    
#     .stError {
#         background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%);
#         color: white;
#         padding: 1.5rem;
#         border-radius: 18px;
#         animation: shake 0.7s ease-in-out;
#         border: 3px solid rgba(255,105,180,0.7);
#         box-shadow: 0 10px 30px rgba(255,105,180,0.5);
#         font-weight: 600;
#     }
    
#     .stWarning {
#         background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#         color: #000000;
#         padding: 1.5rem;
#         border-radius: 18px;
#         border: 3px solid rgba(255,215,0,0.7);
#         box-shadow: 0 10px 30px rgba(255,215,0,0.5);
#         font-weight: 700;
#     }
    
#     @keyframes slideInRight {
#         from {
#             opacity: 0;
#             transform: translateX(120px);
#         }
#         to {
#             opacity: 1;
#             transform: translateX(0);
#         }
#     }
    
#     @keyframes shake {
#         0%, 100% { transform: translateX(0); }
#         25% { transform: translateX(-15px); }
#         75% { transform: translateX(15px); }
#     }
    
#     /* Divider */
#     hr {
#         margin: 4rem 0;
#         border: none;
#         height: 4px;
#         background: linear-gradient(90deg, transparent, #FFD700, #FF69B4, #87CEEB, #FFD700, transparent);
#         box-shadow: 0 0 15px rgba(255,215,0,0.6);
#         border-radius: 2px;
#     }
    
#     /* Spinner */
#     .stSpinner > div {
#         border-top-color: #FFD700 !important;
#         border-right-color: #FF69B4 !important;
#         border-bottom-color: #87CEEB !important;
#         border-left-color: transparent !important;
#         border-width: 4px !important;
#     }
    
#     /* Checkbox */
#     [data-testid="stCheckbox"] {
#         background: rgba(255,215,0,0.15);
#         padding: 1.5rem;
#         border-radius: 15px;
#         margin: 1rem 0;
#         border: 2px solid rgba(255,215,0,0.3);
#         transition: all 0.3s ease;
#     }
    
#     [data-testid="stCheckbox"]:hover {
#         background: rgba(255,215,0,0.22);
#         border-color: rgba(255,215,0,0.5);
#     }
    
#     /* Stats Cards */
#     .stats-card {
#         background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#         color: #000000;
#         padding: 2.5rem;
#         border-radius: 25px;
#         text-align: center;
#         margin: 1.5rem 0;
#         box-shadow: 0 12px 40px rgba(255,215,0,0.5);
#         border: 3px solid rgba(255,215,0,0.5);
#         transition: all 0.4s ease;
#         animation: countUp 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
#     }
    
#     .stats-card:hover {
#         transform: translateY(-8px) scale(1.08);
#         box-shadow: 0 18px 55px rgba(255,215,0,0.7);
#     }
    
#     .stats-number {
#         font-size: 4rem;
#         font-weight: 900;
#         margin: 0;
#         text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
#         font-family: 'Orbitron', sans-serif;
#     }
    
#     .stats-label {
#         font-size: 1.2rem;
#         opacity: 0.95;
#         margin-top: 1rem;
#         font-weight: 800;
#         letter-spacing: 1px;
#         text-transform: uppercase;
#     }
    
#     @keyframes countUp {
#         from {
#             opacity: 0;
#             transform: scale(0.5) rotate(-15deg);
#         }
#         to {
#             opacity: 1;
#             transform: scale(1) rotate(0deg);
#         }
#     }
    
#     /* Footer */
#     .footer {
#         text-align: center;
#         padding: 3.5rem;
#         margin-top: 5rem;
#         background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
#         border-radius: 30px;
#         backdrop-filter: blur(15px);
#         color: #FFD700;
#         border: 4px solid transparent;
#         background-image: 
#             linear-gradient(135deg, #1a1a2e 0%, #16213e 100%),
#             linear-gradient(90deg, #FFD700, #FF69B4, #87CEEB);
#         background-origin: border-box;
#         background-clip: padding-box, border-box;
#         box-shadow: 0 20px 60px rgba(0,0,0,0.7);
#     }
    
#     .footer h3 {
#         color: #FFD700;
#         font-family: 'Orbitron', sans-serif;
#         font-size: 2.5rem;
#         text-shadow: 0 0 20px rgba(255,215,0,0.6);
#     }
    
#     .footer p {
#         color: #87CEEB;
#         font-size: 1.1rem;
#     }
    
#     /* Scrollbar */
#     ::-webkit-scrollbar {
#         width: 16px;
#         height: 16px;
#     }
    
#     ::-webkit-scrollbar-track {
#         background: rgba(26,26,46,0.9);
#         border-radius: 12px;
#     }
    
#     ::-webkit-scrollbar-thumb {
#         background: linear-gradient(135deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
#         border-radius: 12px;
#         border: 3px solid rgba(26,26,46,0.6);
#     }
    
#     ::-webkit-scrollbar-thumb:hover {
#         background: linear-gradient(135deg, #87CEEB 0%, #FFD700 50%, #FF69B4 100%);
#     }
    
#     /* Progress Bar */
#     .stProgress > div > div {
#         background: linear-gradient(90deg, #FFD700 0%, #FF69B4 50%, #87CEEB 100%);
#         box-shadow: 0 0 25px rgba(255,215,0,0.7);
#         height: 8px !important;
#         border-radius: 4px;
#     }
    
#     /* Info */
#     .stInfo {
#         background: linear-gradient(135deg, rgba(135,206,250,0.3) 0%, rgba(135,206,250,0.2) 100%);
#         border-left: 6px solid #87CEEB;
#         color: #87CEEB;
#         border-radius: 12px;
#         box-shadow: 0 8px 25px rgba(135,206,250,0.35);
#         padding: 1.2rem;
#         font-weight: 600;
#     }
    
#     /* Dataframe */
#     .dataframe {
#         border-radius: 18px;
#         overflow: hidden;
#         box-shadow: 0 12px 45px rgba(0,0,0,0.6);
#         border: 3px solid rgba(255,215,0,0.25);
#     }
    
#     /* File Info Box */
#     .file-info-box {
#         background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
#         padding: 2rem;
#         border-radius: 25px;
#         color: #000000;
#         text-align: center;
#         margin-top: 2rem;
#         box-shadow: 0 12px 40px rgba(255,215,0,0.5);
#         border: 4px solid rgba(255,215,0,0.6);
#         animation: pulse-glow 2.5s infinite;
#     }
    
#     @keyframes pulse-glow {
#         0%, 100% { 
#             box-shadow: 0 12px 40px rgba(255,215,0,0.5);
#             transform: scale(1);
#         }
#         50% { 
#             box-shadow: 0 18px 55px rgba(255,215,0,0.7);
#             transform: scale(1.02);
#         }
#     }
    
#     /* Text Colors */
#     h1, h2, h3, h4, h5, h6 {
#         color: #FFD700 !important;
#         font-family: 'Orbitron', sans-serif;
#     }
    
#     p, span, div, label {
#         color: #FFFFFF;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ================= ANIMATED HEADER =================
# st.markdown("""
# <div class="header-container">
#     <div class="header-emoji">📊</div>
#     <h1 class="header-title">Data Automation Pro</h1>
#     <p class="header-subtitle">
#         🚀 Excel • CSV • PDF • Image | Hindi → English | Phone Cleanup | Pincode Mapping
#     </p>
# </div>
# """, unsafe_allow_html=True)

# # ================= FEATURE CARDS =================
# st.markdown("""
# <div class="feature-grid">
#     <div class="feature-card">
#         <div class="feature-icon">🌐</div>
#         <div class="feature-title">Hindi Translation</div>
#         <div class="feature-desc">Smart Hindi to English conversion</div>
#     </div>
#     <div class="feature-card">
#         <div class="feature-icon">📞</div>
#         <div class="feature-title">Phone Cleanup</div>
#         <div class="feature-desc">Standardize phone numbers</div>
#     </div>
#     <div class="feature-card">
#         <div class="feature-icon">📍</div>
#         <div class="feature-title">Pincode Magic</div>
#         <div class="feature-desc">Auto State & District mapping</div>
#     </div>
#     <div class="feature-card">
#         <div class="feature-icon">🔍</div>
#         <div class="feature-title">OCR Power</div>
#         <div class="feature-desc">Extract from images & PDFs</div>
#     </div>
#     <div class="feature-card">
#         <div class="feature-icon">📦</div>
#         <div class="feature-title">Batch Processing</div>
#         <div class="feature-desc">Multiple files ZIP export</div>
#     </div>
# </div>
# """, unsafe_allow_html=True)

# # ================= SIDEBAR =================
# with st.sidebar:
#     st.markdown("### ⚙️ Settings & Features")
    
#     st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
#     st.markdown("""
#     **✨ Core Features:**
#     - ✔ Hindi → English translation
#     - ✔ Phone normalization  
#     - ✔ Pincode → State & District  
#     - ✔ Duplicate removal  
#     - ✔ Multi-format support  
#     - ✔ Batch ZIP export
#     """)
#     st.markdown('</div>', unsafe_allow_html=True)
    
#     st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
#     st.markdown("""
#     **📁 Supported Formats:**
#     - 📊 Excel (`.xlsx`)
#     - 📄 CSV (`.csv`)
#     - 📑 PDF (`.pdf`)
#     - 🖼️ Images (`.jpg`, `.png`)
#     """)
#     st.markdown('</div>', unsafe_allow_html=True)
    
#     translate_on = st.checkbox(
#         "🔤 Enable Hindi Translation",
#         value=True,
#         help="Automatically translate Hindi text to English"
#     )
    
#     st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
#     st.markdown("""
#     **📊 Processing Pipeline:**
#     1. 📤 Upload file(s)
#     2. 🔍 Auto data extraction
#     3. 🧹 Clean & normalize
#     4. 💾 Download results
#     """)
#     st.markdown('</div>', unsafe_allow_html=True)
    
#     st.markdown("---")
#     st.markdown("**💡 Pro Tips:**")
#     st.info("✓ Use clear headers\n✓ Batch for efficiency\n✓ Download ZIP for multiple files")

# # ================= MAIN CONTENT =================
# st.markdown("<br>", unsafe_allow_html=True)

# # ======================================================
# # 🔹 SECTION 1: SINGLE FILE UPLOAD
# # ======================================================
# st.markdown('<div class="upload-card">', unsafe_allow_html=True)
# st.markdown('<div class="card-title"><span class="card-icon">📁</span> Single File Upload</div>', unsafe_allow_html=True)

# col1, col2 = st.columns([2, 1])

# with col1:
#     single_file = st.file_uploader(
#         "📤 Upload Excel / CSV / PDF / Image",
#         type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
#         key="single"
#     )

# with col2:
#     if single_file:
#         st.markdown(f"""
#         <div class="file-info-box">
#             <div style='font-size: 1.1rem; opacity: 0.9; font-weight: 800;'>📄 FILE LOADED</div>
#             <div style='font-size: 1.3rem; font-weight: 900; margin-top: 1rem; word-wrap: break-word;'>{single_file.name}</div>
#         </div>
#         """, unsafe_allow_html=True)

# if single_file:
#     with st.spinner("🔄 Processing file... Please wait"):
#         try:
#             # ---------- READ ----------
#             if single_file.name.lower().endswith(".xlsx"):
#                 df = pd.read_excel(single_file)

#             elif single_file.name.lower().endswith(".csv"):
#                 try:
#                     df = pd.read_csv(single_file, encoding="utf-8")
#                 except UnicodeDecodeError:
#                     df = pd.read_csv(single_file, encoding="latin1")

#             elif single_file.name.lower().endswith(".pdf"):
#                 df = pdf_to_df(single_file)

#             else:
#                 df = image_to_df(single_file)

#             if df.empty:
#                 st.error("❌ No data detected in file.")
#             else:
#                 # ---------- CLEAN ----------
#                 df = clean_dataframe(df)
#                 if translate_on:
#                     df = translate_hindi_df(df)

#                 df.drop_duplicates(inplace=True)

#                 # Stats
#                 col1, col2, col3 = st.columns(3)
                
#                 with col1:
#                     st.markdown(f"""
#                     <div class='stats-card' style='background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%); color: white;'>
#                         <div class='stats-number'>{len(df)}</div>
#                         <div class='stats-label'>ROWS</div>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col2:
#                     st.markdown(f"""
#                     <div class='stats-card' style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: black;'>
#                         <div class='stats-number'>{len(df.columns)}</div>
#                         <div class='stats-label'>COLUMNS</div>
#                     </div>
#                     """, unsafe_allow_html=True)
                
#                 with col3:
#                     st.markdown(f"""
#                     <div class='stats-card' style='background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white;'>
#                         <div class='stats-number'>{df.duplicated().sum()}</div>
#                         <div class='stats-label'>DUPLICATES</div>
#                     </div>
#                     """, unsafe_allow_html=True)

#                 st.success("✅ File processed successfully!")
                
#                 st.markdown("### 📊 Data Preview (First 10 Rows)")
#                 st.dataframe(df.head(10), use_container_width=True, height=400)

#                 # ---------- DOWNLOAD ----------
#                 buffer = io.BytesIO()
#                 df.to_excel(buffer, index=False, engine='openpyxl')
#                 buffer.seek(0)

#                 output_name = f"cleaned_{os.path.splitext(single_file.name)[0]}.xlsx"
#                 st.download_button(
#                     "⬇️ DOWNLOAD CLEANED EXCEL",
#                     data=buffer,
#                     file_name=output_name,
#                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#                     use_container_width=True
#                 )
                
#         except Exception as e:
#             st.error(f"❌ Error: {str(e)}")

# st.markdown('</div>', unsafe_allow_html=True)

# st.markdown("<br><br>", unsafe_allow_html=True)

# # ======================================================
# # 🔹 SECTION 2: MULTIPLE FILE UPLOAD (ZIP)
# # ======================================================
# st.markdown('<div class="upload-card">', unsafe_allow_html=True)
# st.markdown('<div class="card-title"><span class="card-icon">📦</span> Batch Processing - Multiple Files</div>', unsafe_allow_html=True)

# multi_files = st.file_uploader(
#     "📤 Upload multiple files (ZIP export)",
#     type=["xlsx", "csv", "pdf", "jpg", "jpeg", "png"],
#     accept_multiple_files=True,
#     key="multiple"
# )

# if multi_files:
#     st.markdown(f"""
#     <div class="file-info-box">
#         <div style='font-size: 3.5rem; font-weight: 900; font-family: "Orbitron", sans-serif;'>{len(multi_files)}</div>
#         <div style='font-size: 1.3rem; opacity: 0.95; font-weight: 800; margin-top: 0.8rem; letter-spacing: 1px;'>FILES READY</div>
#     </div>
#     """, unsafe_allow_html=True)
    
#     zip_buffer = io.BytesIO()
#     processed_count = 0

#     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#         with st.spinner("🔄 Processing multiple files..."):
#             progress_bar = st.progress(0)
            
#             for idx, file in enumerate(multi_files):
#                 try:
#                     # ---------- READ ----------
#                     if file.name.lower().endswith(".xlsx"):
#                         df = pd.read_excel(file)

#                     elif file.name.lower().endswith(".csv"):
#                         try:
#                             df = pd.read_csv(file, encoding="utf-8")
#                         except UnicodeDecodeError:
#                             df = pd.read_csv(file, encoding="latin1")

#                     elif file.name.lower().endswith(".pdf"):
#                         df = pdf_to_df(file)

#                     else:
#                         df = image_to_df(file)

#                     if df.empty:
#                         st.warning(f"⚠️ No data: {file.name}")
#                         continue

#                     # ---------- CLEAN ----------
#                     df = clean_dataframe(df)
#                     if translate_on:
#                         df = translate_hindi_df(df)

#                     df.drop_duplicates(inplace=True)

#                     # ---------- SAVE ----------
#                     excel_buffer = io.BytesIO()
#                     df.to_excel(excel_buffer, index=False, engine='openpyxl')
#                     excel_buffer.seek(0)

#                     clean_name = f"cleaned_{os.path.splitext(file.name)[0]}.xlsx"
#                     zipf.writestr(clean_name, excel_buffer.read())
#                     processed_count += 1
                    
#                     progress_bar.progress((idx + 1) / len(multi_files))
                    
#                 except Exception as e:
#                     st.warning(f"⚠️ Failed: {file.name} - {str(e)}")
            
#             progress_bar.empty()

#     zip_buffer.seek(0)

#     if processed_count > 0:
#         # Stats
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown(f"""
#             <div class='stats-card' style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: black;'>
#                 <div class='stats-number'>{len(multi_files)}</div>
#                 <div class='stats-label'>UPLOADED</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col2:
#             st.markdown(f"""
#             <div class='stats-card' style='background: linear-gradient(135deg, #87CEEB 0%, #4169E1 100%); color: white;'>
#                 <div class='stats-number'>{processed_count}</div>
#                 <div class='stats-label'>PROCESSED</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.markdown(f"""
#             <div class='stats-card' style='background: linear-gradient(135deg, #FF69B4 0%, #FF1493 100%); color: white;'>
#                 <div class='stats-number'>{len(multi_files) - processed_count}</div>
#                 <div class='stats-label'>FAILED</div>
#             </div>
#             """, unsafe_allow_html=True)

#         st.success(f"✅ Processed {processed_count} of {len(multi_files)} files!")

#         st.download_button(
#             "⬇️ DOWNLOAD ZIP PACKAGE",
#             data=zip_buffer,
#             file_name="cleaned_files.zip",
#             mime="application/zip",
#             use_container_width=True
#         )
#     else:
#         st.error("❌ No files processed.")

# st.markdown('</div>', unsafe_allow_html=True)

# # ================= FOOTER =================
# st.markdown("<br><br>", unsafe_allow_html=True)
# st.markdown("""
# <div class="footer">
#     <h3 style='margin-bottom: 1.5rem;'>📊 DATA AUTOMATION PRO</h3>
#     <p style='font-size: 1.2rem; margin-bottom: 1.5rem;'>
#         Built with ❤️ using Python • Streamlit • Tesseract • Google Translate
#     </p>
#     <div style='display: flex; justify-content: center; gap: 3rem; margin: 2rem 0;'>
#         <div>
#             <div style='font-size: 2.8rem; font-weight: 900; color: #FFD700; font-family: "Orbitron", sans-serif;'>80-90%</div>
#             <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Time Saved</div>
#         </div>
#         <div>
#             <div style='font-size: 2.8rem; font-weight: 900; color: #FF69B4; font-family: "Orbitron", sans-serif;'>95%+</div>
#             <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Accuracy</div>
#         </div>
#         <div>
#             <div style='font-size: 2.8rem; font-weight: 900; color: #87CEEB; font-family: "Orbitron", sans-serif;'>19K+</div>
#             <div style='opacity: 0.95; color: #87CEEB; font-weight: 700; font-size: 1.1rem;'>Pincodes</div>
#         </div>
#     </div>
#     <p style='font-size: 1rem; opacity: 0.9; margin-top: 2rem; color: #FFD700; font-weight: 700;'>
#         © 2024 All Rights Reserved | Version 2.0 Pro
#     </p>
# </div>
# """, unsafe_allow_html=True)









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










