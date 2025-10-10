
import streamlit as st
import requests, json, os, re, time
import random
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
import unicodedata
import pandas as pd

# --- Theme toggle state ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- Theme toggle (capsule-style single-click selector) ---
st.markdown('''
<style>
.st-theme-toggle-container { position: fixed; left: 18px; top: 18px; z-index: 10001; }
/* Make the radio look capsule-like where possible */
.st-theme-toggle-container .stRadio { width: 180px; }
.st-theme-toggle-container .stRadio .css-1wy0on6 { display: flex; gap: 0; }
.st-theme-toggle-container .stRadio label[data-baseweb="radio"] { flex: 1; }
.st-theme-toggle-container .stRadio .stRadio > div > label { border-radius: 999px; padding: 6px 12px; border: 1px solid rgba(0,0,0,0.06); }
</style>
''', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 6])
    with col1:
        # Single-click capsule radio for Light / Dark
        try:
            theme_choice = st.radio('', options=['Light', 'Dark'], index=(1 if st.session_state.dark_mode else 0), key='theme_radio', horizontal=True)
        except TypeError:
            # older Streamlit versions may not support horizontal=True
            theme_choice = st.radio('', options=['Light', 'Dark'], index=(1 if st.session_state.dark_mode else 0), key='theme_radio')

        st.session_state.dark_mode = (theme_choice == 'Dark')

    with col2:
        st.markdown('')
if st.session_state.dark_mode:
    st.markdown('''
    <style>
    :root {
        --text-primary: #f3f4f6; /* light text */
        --bg-card: #23272f;     /* dark card bg */
        --text-light: #ffffff;  /* white text for colored badges */
        --border-color: rgba(255,255,255,0.06);
        --accent-orange: #ff6b35;
        --musigma-red: #8b1e1e;
        --accent-teal: #0ea5a4;
    }
    /* Dark overall background */
    body, .stApp, .main {
        background: linear-gradient(135deg, #0b0f14 0%, #18181b 50%, #23272f 100%) !important;
        color: var(--text-primary) !important;
    }
    /* Make all main boxes use Mu-Sigma red gradient and white text for contrast */
    .info-card, .qa-box, .problem-display, .vocab-display, .section-title-box, .score-badge, .dimension-box, .dimension-display-box {
        background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%) !important;
        color: var(--text-light) !important;
        border-color: rgba(255,255,255,0.06) !important;
        box-shadow: 0 6px 30px rgba(0,0,0,0.45) !important;
    }
    /* Business problem text should be white in dark mode */
    .problem-display, .problem-display p { color: var(--text-light) !important; }
    /* Inputs use dark backgrounds with light text to match dark theme */
    .stTextArea textarea, .stTextInput input, .stSelectbox > div > div, .stSelectbox [data-baseweb="select"] {
        background: #1f2933 !important;
        color: var(--text-light) !important;
        border-color: rgba(255,255,255,0.06) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%) !important;
        color: var(--text-light) !important;
    }
    /* Ensure headings and labels are readable */
    h1, h2, h3, h4, h5, h6, .dimension-label, .qa-question, .score-badge *, .hardness-badge-hard, .hardness-badge-moderate, .hardness-badge-easy {
        color: var(--text-light) !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.6);
    }
    .theme-toggle-btn {
        background: transparent !important;
        color: var(--text-light) !important;
        border-color: var(--text-light) !important;
    }
    .theme-toggle-btn:hover {
        background: rgba(255,255,255,0.04) !important;
    }
    </style>
    ''', unsafe_allow_html=True)
else:
    st.markdown('''
    <style>
    :root {
        --text-primary: #1e293b;
        --bg-card: #ffffff;
        --text-light: #ffffff;
        --border-color: rgba(139, 30, 30, 0.15);
        --accent-orange: #ff6b35;
        --musigma-red: #8b1e1e;
    }
    body, .stApp, .main {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 50%, #eeeeee 100%) !important;
        color: #1e293b !important;
    }
    /* Regular content cards: white background, dark text */
    .info-card, .qa-box, .vocab-display, .section-title-box {
        background: #fff !important;
        color: var(--text-primary) !important;
        border-color: #e5e7eb !important;
        box-shadow: 0 2px 16px rgba(0,0,0,0.08) !important;
    }
    /* Business problem area stays white for readability */
    .problem-display { background: #fff !important; color: var(--text-primary) !important; border-color: #e5e7eb !important; }

    /* Branded boxes (scores & dimensions) use Mu-Sigma red gradient and white text in light mode too */
    .score-badge, .dimension-box, .dimension-display-box {
        background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%) !important;
        color: var(--text-light) !important;
        border: 3px solid rgba(255,255,255,0.18) !important;
        box-shadow: var(--shadow-xl) !important;
    }
    .score-badge *, .dimension-box *, .dimension-display-box * { color: var(--text-light) !important; }
    .stTextArea textarea, .stTextInput input, .stSelectbox > div > div, .stSelectbox [data-baseweb="select"] {
        background: #fff !important;
        color: #1e293b !important;
        border-color: #e5e7eb !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #8b1e1e 0%, #ff6b35 100%) !important;
        color: #fff !important;
    }
    h1, h2, h3, h4, h5, h6, .dimension-label, .qa-question, .score-badge *, .hardness-badge-hard, .hardness-badge-moderate, .hardness-badge-easy {
        color: #1e293b !important;
        text-shadow: none;
    }
    .theme-toggle-btn {
        background: #fff !important;
        color: #8b1e1e !important;
        border-color: #8b1e1e !important;
    }
    .theme-toggle-btn:hover {
        background: #ffe5e5 !important;
        border-color: #ff6b35 !important;
    }
    </style>
    ''', unsafe_allow_html=True)

# -----------------------------
# Config - Page Setup
# -----------------------------
st.set_page_config(
    page_title="Business Problem Level Classifier",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* --- GOOGLE FONTS --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;900&family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

/* --- HIDE DEFAULT STREAMLIT ELEMENTS --- */
#MainMenu, footer, header { visibility: hidden; }
.element-container:empty { display: none !important; }
div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }

/* --- COLOR VARIABLES (MU-SIGMA BRAND) --- */
:root {
    --musigma-red: #8b1e1e;
    --musigma-red-dark: #6b1515;
    --musigma-red-light: #a52828;
    --accent-orange: #ff6b35;
    --accent-teal: #940d0d;
    --accent-teal-light: #b81414;
    --bg-gradient: linear-gradient(135deg, #8b1e1e 0%, #00000 100%);
    --bg-card: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-light: #ffffff;
    --border-color: rgba(139, 30, 30, 0.15);
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 8px 32px rgba(139, 30, 30, 0.25);
    --shadow-xl: 0 16px 48px rgba(139, 30, 30, 0.35);
    --shadow-glow: 0 0 30px rgba(255, 107, 53, 0.3);
}

/* --- SMOOTH ANIMATIONS --- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes borderGlow {
    0%, 100% { box-shadow: 0 0 10px rgba(255, 107, 53, 0.3); }
    50% { box-shadow: 0 0 25px rgba(255, 107, 53, 0.6); }
}

/* --- APP BACKGROUND --- */
.main { 
    font-family: 'Inter', sans-serif; 
    background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 50%, #eeeeee 100%);
    background-attachment: fixed; 
    min-height: 100vh; 
    padding: 2rem 1rem;
}
.stApp { background: transparent; }

/* --- MAIN PAGE TITLE --- */
.page-title { 
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%);
    background-size: 200% 200%;
    animation: gradientFlow 6s ease infinite;
    padding: 3.5rem 3rem; 
    border-radius: 28px; 
    text-align: center; 
    margin-bottom: 3rem; 
    box-shadow: var(--shadow-xl);
    border: 3px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
}

.page-title::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate 30s linear infinite;
}

.page-title h1 { 
    margin: 0; 
    font-weight: 900; 
    color: #ffffff !important;
    font-size: 3.5rem;
    letter-spacing: -1.5px;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
    font-family: 'Poppins', sans-serif;
}

.page-subtitle {
    color: rgba(255,255,255,0.95) !important;
    font-size: 1.25rem;
    margin-top: 0.75rem;
    font-weight: 400;
    position: relative;
    z-index: 1;
    letter-spacing: 0.5px;
}

/* Decorative elements - STATIC */
.title-decoration {
    position: absolute;
    font-size: 3rem;
    opacity: 0.12;
}

.deco-1 { top: 25px; left: 40px; }
.deco-2 { top: 35px; right: 50px; }
.deco-3 { bottom: 30px; left: 60px; }
.deco-4 { bottom: 25px; right: 70px; }

/* Mu-Sigma Logo - FIXED POSITION */
.musigma-logo {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 95px;
    height: 95px;
    border-radius: 50%;
    border: 3px solid var(--musigma-red);
    box-shadow: 0 10px 40px rgba(139, 30, 30, 0.4);
    z-index: 9999;
    background: white;
    opacity: 1;
    overflow: hidden;
    animation: fadeIn 1s ease-out;
}

.musigma-logo:hover { 
    box-shadow: 0 15px 50px rgba(139, 30, 30, 0.6);
    animation: borderGlow 2s ease-in-out infinite;
}

.musigma-logo img {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    padding: 12px;
}

/* --- SECTION HEADINGS (CENTERED) --- */
h2, h3, h4, h5, h6,
.stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    text-align: center !important;
}

/* --- SECTION TITLE BOXES (CENTERED WITH GRADIENT) --- */

.section-title-box {
    /* Match the main title look: Mu-Sigma red -> accent orange gradient in all modes */
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%) !important;
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin: 2.5rem 0 1.5rem 0 !important;
    box-shadow: var(--shadow-lg) !important;
    /* Explicitly disable decorative animations for section title boxes */
    position: relative;
    overflow: hidden;
    text-align: center;
}

/* Remove shimmer overlay/animation for these boxes so headings remain fully visible */
.section-title-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 0;
    background: transparent !important;
    animation: none !important;
}

.section-title-box h2,
.section-title-box h3,
.section-title-box h4 {
    color: var(--text-light) !important; /* ensure white text in all themes */
    margin: 0 !important;
    font-weight: 900 !important;
    font-size: 1.9rem !important;
    font-family: 'Poppins', sans-serif !important;
    position: relative;
    z-index: 2;
    text-align: center !important;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
}

.section-icon {
    font-size: 2rem;
    display: inline-block;
}

/* --- INFO CARDS --- */
.info-card { 
    background: var(--bg-card);
    border: 2px solid var(--border-color);
    border-radius: 24px; 
    padding: 2.5rem; 
    margin-bottom: 2rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.7s ease-out;
    position: relative;
}

.info-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 0;
    background: linear-gradient(180deg, var(--musigma-red), var(--accent-orange), var(--accent-teal));
    transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 24px 0 0 24px;
}

.info-card:hover::before {
    height: 100%;
}

.info-card:hover { 
    transform: translateY(-8px) scale(1.01); 
    box-shadow: var(--shadow-xl);
    border-color: var(--accent-orange);
}

.info-card p, .info-card li, .info-card span {
    color: var(--text-primary) !important; 
    line-height: 1.9;
    font-size: 1.05rem;
}

.info-card h3, .info-card h4 {
    color: var(--musigma-red) !important;
    font-weight: 700 !important;
    margin-bottom: 1.5rem !important;
}

/* --- PROBLEM DISPLAY --- */
.problem-display { 
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 2px solid var(--border-color);
    border-radius: 24px !important; 
    padding: 2.5rem !important; 
    margin-bottom: 2.5rem; 
    box-shadow: var(--shadow-md);
    animation: scaleIn 0.7s ease-out;
    position: relative;
    transition: all 0.4s ease;
}

.problem-display:hover {
    box-shadow: var(--shadow-lg);
    border-color: var(--accent-teal);
}

.problem-display::after {
    content: '📋';
    position: absolute;
    top: 25px;
    right: 25px;
    font-size: 2.5rem;
    opacity: 0.08;
}

.problem-display h4 { 
    color: var(--musigma-red) !important; 
    margin-top: 0; 
    font-weight: 700; 
    font-size: 1.5rem; 
    margin-bottom: 1.5rem;
    text-align: center !important;
}

.problem-display p { 
    color: var(--text-primary) !important; 
    line-height: 1.9;
    font-size: 1.05rem;
    margin: 0;
}

/* --- Q&A BOXES --- */
.qa-box { 
    background: var(--bg-card);
    border: 2px solid var(--border-color);
    border-radius: 20px; 
    padding: 2.25rem; 
    margin-bottom: 2rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    animation: slideInRight 0.7s ease-out;
    position: relative;
    overflow: hidden;
}

.qa-box::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--musigma-red), var(--accent-orange), var(--accent-teal));
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.qa-box:hover::after {
    width: 100%;
}

.qa-box:hover { 
    transform: translateX(8px) translateY(-6px); 
    box-shadow: var(--shadow-lg);
    border-color: var(--accent-orange);
}

.qa-question { 
    font-weight: 700; 
    font-size: 1.2rem; 
    color: inherit !important; 
    margin-bottom: 1.5rem; 
    line-height: 1.7; 
    font-family: 'Space Grotesk', sans-serif;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}

.qa-question::before {
    content: '▸';
    color: var(--accent-orange);
    font-size: 1.5rem;
    flex-shrink: 0;
}

.qa-answer { 
    font-size: 1.05rem; 
    line-height: 1.9; 
    color: inherit !important; 
    white-space: pre-wrap; 
}

/* --- SCORE BADGES --- */
.score-badge { 
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%);
    padding: 3.5rem; 
    border-radius: 28px; 
    text-align: center; 
    color: var(--text-light); 
    box-shadow: var(--shadow-xl);
    animation: scaleIn 0.8s ease-out; 
    min-height: 220px; 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    justify-content: center; 
    border: 3px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}

.score-badge:hover {
    transform: scale(1.03);
    box-shadow: var(--shadow-glow);
}

.score-badge::before {
    content: '';
    position: absolute;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

.score-badge * { 
    color: var(--text-light) !important;
    position: relative;
    z-index: 1;
}

/* --- HARDNESS BADGES --- */
.hardness-badge-hard, 
.hardness-badge-moderate, 
.hardness-badge-easy { 
    color: var(--text-light) !important; 
    padding: 3.5rem; 
    border-radius: 28px; 
    font-size: 2.2rem; 
    font-weight: 900; 
    text-align: center; 
    min-height: 220px; 
    display: flex; 
    flex-direction: column;
    align-items: center; 
    justify-content: center; 
    animation: scaleIn 0.8s ease-out; 
    border: 3px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-xl);
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}

.hardness-badge-hard:hover,
.hardness-badge-moderate:hover,
.hardness-badge-easy:hover {
    transform: scale(1.03);
}

.hardness-badge-hard { 
    background: linear-gradient(135deg, #c62828 0%, #8b0000 100%);
}

.hardness-badge-moderate { 
    background: linear-gradient(135deg, #f57c00 0%, #e65100 100%);
}

.hardness-badge-easy { 
    background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-teal-light) 100%);
}

/* --- DIMENSION BOXES --- */
.dimension-box, 
.dimension-display-box { 
    color: var(--text-light) !important; 
    padding: 3rem; 
    border-radius: 24px; 
    text-align: center; 
    box-shadow: var(--shadow-md);
    min-height: 200px; 
    margin-bottom: 2rem; 
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.8s ease-out; 
    border: 3px solid rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
}

.dimension-box::before,
.dimension-display-box::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at top right, rgba(255,255,255,0.15) 0%, transparent 60%);
    top: 0;
    right: 0;
}

.dimension-box { 
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%);
    cursor: pointer;
}

.dimension-box:hover { 
    transform: translateY(-12px) scale(1.04); 
    box-shadow: 0 20px 60px rgba(139, 30, 30, 0.4);
    animation: borderGlow 2s ease-in-out infinite;
}

.dimension-display-box { 
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%);
}

.dimension-display-box:hover { 
    transform: translateY(-8px) scale(1.02); 
    box-shadow: var(--shadow-xl);
}

.dimension-score { 
    font-size: 4rem; 
    font-weight: 900; 
    margin: 1.25rem 0; 
    color: inherit !important; 
    font-family: 'Poppins', sans-serif;
    text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}

.dimension-label { 
    font-size: 1.35rem; 
    font-weight: 700; 
    color: inherit !important; 
    text-transform: uppercase; 
    letter-spacing: 2px; 
    font-family: 'Space Grotesk', sans-serif;
    position: relative;
    z-index: 1;
}

/* --- VOCABULARY DISPLAY --- */
.vocab-display { 
    background: var(--bg-card) !important; 
    border: 2px solid var(--border-color);
    border-radius: 24px; 
    padding: 2.5rem; 
    line-height: 1.7 !important; 
    margin-top: 2rem;
    color: var(--text-primary) !important;
    font-size: 1.05rem;
    max-height: 650px;
    overflow-y: auto;
    box-shadow: var(--shadow-md);
    animation: slideInLeft 0.6s ease-out;
}

.vocab-display h4 {
    color: var(--musigma-red) !important;
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    margin-bottom: 2rem !important;
    text-align: center !important;
}

.vocab-display strong {
    color: var(--accent-black) !important;
    font-weight: 700 !important;
}

/* --- SCORE GRID & DIMENSION ITEM STYLES (theme-aware) --- */
.scores-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
}
.score-item {
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    background: rgba(255, 107, 53, 0.05);
    color: var(--accent-orange);
}
.score-item strong { display:block; }
.score-item .score-value { font-size: 1.2rem; font-weight: 700; color: var(--accent-orange); }

.dim-item { 
    padding: 1rem; 
    margin-bottom: 0.75rem; 
    background: rgba(255, 107, 53, 0.05); 
    border-radius: 8px; 
    border-left: 3px solid var(--accent-orange);
}
.dim-item strong { color: var(--accent-orange); font-size: 1.1rem; }
.dim-item .dim-score { font-size: 1.5rem; font-weight: 700; color: var(--accent-orange); }

.vocab-item {
    margin-bottom: 1.25rem !important;
    padding-bottom: 1.25rem !important;
    border-bottom: 1px solid rgba(139, 30, 30, 0.1);
    transition: all 0.3s ease;
}

.vocab-item:hover {
    padding-left: 15px;
    background: linear-gradient(90deg, rgba(139, 30, 30, 0.03) 0%, transparent 100%);
    border-radius: 10px;
}

/* --- DIMENSION CLICK TEXT --- */
.dimension-click-text {
    color: var(--text-secondary) !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    text-align: center;
    margin-bottom: 3rem !important;
    padding: 1.5rem;
    background: linear-gradient(135deg, rgba(139, 30, 30, 0.05) 0%, rgba(255, 107, 53, 0.05) 100%);
    border-radius: 16px;
    border: 2px dashed var(--accent-orange);
    animation: pulse 4s ease-in-out infinite;
}

/* --- STREAMLIT SELECT BOXES (FIXED) --- */
.stSelectbox {
    margin-bottom: 1rem;
}

.stSelectbox > label {
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.5rem !important;
}

.stSelectbox > div > div { 
    background-color: var(--bg-card) !important; 
    border: 2px solid var(--border-color) !important; 
    border-radius: 16px !important; 
    padding: 0.5rem 1rem !important; 
    min-height: 48px !important; 
    max-height: 48px !important;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease; 
}

.stSelectbox > div > div:hover { 
    border-color: var(--accent-purple) !important; 
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
    transform: translateY(-2px); 
}

.stSelectbox [data-baseweb="select"] { 
    background-color: transparent !important; 
    min-height: 40px !important;
    max-height: 40px !important;
}

.stSelectbox [data-baseweb="select"] > div {
    color: var(--text-primary) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 100% !important;
}

/* Fix for selected text visibility */
div[data-baseweb="select"] > div:first-child {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    max-width: 100% !important;
    padding-right: 20px !important;
}

[data-baseweb="popover"] { 
    background-color: var(--bg-card) !important; 
    border-radius: 16px !important;
    box-shadow: var(--shadow-lg) !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}

ul[role="listbox"] { 
    background-color: var(--bg-card) !important; 
    border: 2px solid var(--border-color) !important; 
    border-radius: 16px !important; 
    max-height: 280px !important; 
    overflow-y: auto !important; 
    box-shadow: var(--shadow-lg);
    padding: 0.5rem !important;
}

li[role="option"] { 
    color: var(--text-primary) !important; 
    background-color: transparent !important; 
    padding: 10px 14px !important; 
    font-size: 0.95rem !important; 
    line-height: 1.5 !important; 
    transition: all 0.2s ease;
    border-radius: 10px !important;
    margin: 2px 0 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

li[role="option"]:hover { 
    background-color: rgba(124, 58, 237, 0.1) !important; 
    color: var(--accent-purple) !important; 
    transform: translateX(5px); 
}

li[role="option"][aria-selected="true"] { 
    background-color: rgba(139, 30, 30, 0.15) !important; 
    color: var(--musigma-red) !important; 
    font-weight: 600 !important; 
}

/* --- TEXT AREAS & INPUTS --- */
.stTextArea textarea, 
.stTextInput input { 
    background: var(--bg-card) !important; 
    border: 2px solid var(--border-color) !important; 
    border-radius: 16px !important; 
    color: var(--text-primary) !important; 
    font-size: 1.05rem !important; 
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease; 
    padding: 1.25rem !important;
    line-height: 1.7 !important;
}

.stTextArea textarea {
    min-height: 180px !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: var(--text-secondary) !important;
    opacity: 0.7 !important;
}

.stTextArea textarea:focus, 
.stTextInput input:focus { 
    border-color: var(--accent-orange) !important; 
    box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1) !important;
    outline: none !important;
}

/* --- BUTTONS --- */
.stButton > button { 
    background: linear-gradient(135deg, var(--musigma-red) 0%, var(--accent-orange) 100%);
    color: #ffffff !important; 
    border: none; 
    border-radius: 16px; 
    padding: 1.1rem 2.75rem; 
    font-weight: 700; 
    font-size: 1.1rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.stButton > button:hover::before {
    width: 400px;
    height: 400px;
}

.stButton > button:hover { 
    transform: translateY(-4px) scale(1.02); 
    box-shadow: 0 10px 30px rgba(139, 30, 30, 0.4);
}

.stButton > button:active { 
    transform: translateY(-2px); 
}

/* --- PROGRESS BAR --- */
.stProgress > div > div { 
    background: linear-gradient(90deg, var(--musigma-red), var(--accent-orange), var(--accent-teal)) !important; 
    border-radius: 12px; 
    height: 12px !important;
}

/* --- FUN FACT STYLING --- */
.fun-fact {
    background: linear-gradient(135deg, rgba(139, 30, 30, 0.05) 0%, rgba(255, 107, 53, 0.05) 100%);
    padding: 1.5rem 2rem;
    border-radius: 16px;
    border-left: 4px solid var(--accent-orange);
    margin-top: 1rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    animation: slideInRight 0.5s ease-out;
}

.fun-fact-title {
    font-weight: 700;
    color: var(--musigma-red);
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}

.fun-fact-text {
    color: var(--text-secondary);
    font-size: 1rem;
    line-height: 1.6;
}

/* --- SCROLLBAR --- */
::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(139, 30, 30, 0.05);
    border-radius: 12px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--musigma-red), var(--accent-orange));
    border-radius: 12px;
    transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, var(--musigma-red-dark), var(--accent-orange));
}

/* --- RESPONSIVE --- */
@media (max-width: 768px) {
    .page-title h1 {
        font-size: 2.2rem;
    }
    
    .section-title-box h2,
    .section-title-box h3 {
        font-size: 1.4rem !important;
    }
    
    .dimension-score {
        font-size: 3rem;
    }
    
    .musigma-logo {
        width: 75px;
        height: 75px;
    }
}

/* Navigation breadcrumb */
.nav-breadcrumb {
    background: rgba(139, 30, 30, 0.05);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.95rem;
    color: var(--text-secondary);
    animation: fadeIn 0.5s ease-out;
}

.nav-breadcrumb a {
    color: var(--musigma-red);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s ease;
}

.nav-breadcrumb a:hover {
    color: var(--accent-orange);
}
</style>
""", unsafe_allow_html=True)

# Logo
st.markdown('''
<div class="musigma-logo">
    <img src="https://yt3.googleusercontent.com/ytc/AIdro_k-7HkbByPWjKpVPO3LCF8XYlKuQuwROO0vf3zo1cqgoaE=s900-c-k-c0x00ffffff-no-rj" alt="Mu-Sigma">
</div>
''', unsafe_allow_html=True)
# -----------------------------
# Config - Data & Auth
# -----------------------------
TENANT_ID = "talos"
AUTH_TOKEN = None
HEADERS_BASE = {"Content-Type": "application/json"}

# -----------------------------
# EXPANDED ACCOUNTS with Industry Mapping (CORRECTED VERSION)
# -----------------------------
ACCOUNT_INDUSTRY_MAP = {
    "Select Account": "Select Industry",

    # --- Priority Accounts (shown first) ---
    "Abbvie": "Pharma",
    "BMS": "Pharma",
    "BLR Airport": "Other",
    "Chevron": "Energy",
    "Coles": "Retail",
    "DELL": "Technology",
    "Microsoft": "Technology",
    "Mu Labs": "Technology",
    "Nike": "Consumer Goods",
    "Skill Development": "Education",
    "Southwest Airlines": "Airlines",
    "Sabic": "Energy",
    "Johnson & Johnson": "Pharma",
    "THD": "Retail",
    "Tmobile": "Telecom",
    "Walmart": "Retail",

    # --- Rest of the Accounts ---
    # Pharmaceutical
    "Pfizer": "Pharma",
    "Novartis": "Pharma",
    "Merck": "Pharma",
    "Roche": "Pharma",

    # Technology
    "IBM": "Technology",
    "Oracle": "Technology",
    "SAP": "Technology",
    "Salesforce": "Technology",
    "Adobe": "Technology",

    # Retail
    "Target": "Retail",
    "Costco": "Retail",
    "Kroger": "Retail",
    "Tesco": "Retail",
    "Carrefour": "Retail",

    # Airlines
    "Delta Airlines": "Airlines",
    "United Airlines": "Airlines",
    "American Airlines": "Airlines",
    "Emirates": "Airlines",
    "Lufthansa": "Airlines",

    # Consumer Goods
    "Adidas": "Consumer Goods",
    "Unilever": "Consumer Goods",
    "Procter & Gamble": "Consumer Goods",
    "Coca-Cola": "Consumer Goods",
    "PepsiCo": "Consumer Goods",

    # Energy
    "ExxonMobil": "Energy",
    "Shell": "Energy",
    "BP": "Energy",
    "TotalEnergies": "Energy",

    # Finance
    "JPMorgan Chase": "Finance",
    "Bank of America": "Finance",
    "Wells Fargo": "Finance",
    "Goldman Sachs": "Finance",
    "Morgan Stanley": "Finance",
    "Citigroup": "Finance",

    # Healthcare
    "UnitedHealth": "Healthcare",
    "CVS Health": "Healthcare",
    "Anthem": "Healthcare",
    "Humana": "Healthcare",
    "Kaiser Permanente": "Healthcare",

    # Logistics
    "FedEx": "Logistics",
    "UPS": "Logistics",
    "DHL": "Logistics",
    "Maersk": "Logistics",
    "Amazon Logistics": "Logistics",

    # E-commerce
    "Amazon": "E-commerce",
    "Alibaba": "E-commerce",
    "eBay": "E-commerce",
    "Shopify": "E-commerce",
    "Flipkart": "E-commerce",

    # Automotive
    "Tesla": "Automotive",
    "Ford": "Automotive",
    "General Motors": "Automotive",
    "Toyota": "Automotive",
    "Volkswagen": "Automotive",

    # Hospitality
    "Marriott": "Hospitality",
    "Hilton": "Hospitality",
    "Hyatt": "Hospitality",
    "Airbnb": "Hospitality",

    # Education
    "Coursera": "Education",
    "Udemy": "Education",
    "Khan Academy": "Education",
    "Mars": "Consumer Goods",  # CORRECTED: Mars should be Consumer Goods, not Confectionery
}

# --- Priority Account Order ---
PRIORITY_ACCOUNTS = [
    "Abbvie", "BMS", "BLR Airport", "Chevron", "Coles", "DELL",
    "Microsoft", "Mars", "Mu Labs", "Nike", "Skill Development",  # CORRECTED: Mars was missing comma
    "Southwest Airlines", "Sabic", "Johnson & Johnson",
    "THD", "Tmobile", "Walmart"
]

# --- Add Remaining Accounts (Alphabetically), keeping 'Others' at the end ---
OTHER_ACCOUNTS = [
    acc for acc in ACCOUNT_INDUSTRY_MAP.keys()
    if acc not in PRIORITY_ACCOUNTS and acc != "Select Account"
]
OTHER_ACCOUNTS.sort()

# Add "Others" account to both lists
OTHER_ACCOUNTS.append("Others")  # ✅ Keep Others at last

# --- Final Ordered Account List ---
ACCOUNTS = ["Select Account"] + PRIORITY_ACCOUNTS + OTHER_ACCOUNTS

# --- Add 'Others' Industry mapping ---
ACCOUNT_INDUSTRY_MAP["Others"] = "Other"

# --- Unique Industries ---
# Remove "Confectionery" and "Select Industry" from the industries list
all_industries = list(set(ACCOUNT_INDUSTRY_MAP.values()))
# Filter out "Select Industry" and any non-standard industries
INDUSTRIES = sorted([industry for industry in all_industries 
                    if industry != "Select Industry"])

# Ensure "Other" is included in industries
if "Other" not in INDUSTRIES:
    INDUSTRIES.append("Other")
INDUSTRIES.sort()

# Add "Select Industry" at the beginning
INDUSTRIES = ["Select Industry"] + INDUSTRIES

# Debug info (you can remove this in production)
print(f"Total Accounts: {len(ACCOUNTS)}")
print(f"Total Industries: {len(INDUSTRIES)}")
print(f"Industries: {INDUSTRIES}")

# === API CONFIGURATION ===
API_CONFIGS = [
    {
        "name": "vocabulary",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758548233201&level=1",
        "multiround_convo":3,
        "description": "vocabulary",
        "prompt": lambda problem, outputs: (
            f"{problem}\n\nExtract the vocabulary from this problem statement."
        )
    },
    {
        "name": "current_system",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758549095254&level=1",
        "multiround_convo": 2,
        "description": "Current System in Place",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from vocabulary:\n{outputs.get('vocabulary','')}\n\n"
            "Describe the current system, inputs, outputs, and pain points in detail with clear sections."
        )
    },
    {
        "name": "Q1",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758555344231&level=1",
        "multiround_convo": 2,
        "description": "Q1. What is the frequency and pace of change in the key inputs driving the business?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q1. What is the frequency and pace of change in the key inputs driving the business?\n"
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q2",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758549615986&level=1",
        "multiround_convo": 2,
        "description": "Q2. To what extent are these changes cyclical and predictable versus sporadic and unpredictable?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q2. To what extent are these changes cyclical and predictable vs sporadic and unpredictable?\nScore 0–5. Provide justification."
        )
    },
    {
        "name": "Q3",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758614550482&level=1",
        "multiround_convo": 2,
        "description": "Q3. How resilient is the current system in absorbing these changes without requiring significant rework or disruption?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q3. How resilient is the current system in absorbing these changes? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q4",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758614809984&level=1",
        "multiround_convo": 2,
        "description": "Q4. To what extent do stakeholders share a common understanding of the key terms and concepts?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q4. To what extent do stakeholders share a common understanding and goals about the problem? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q5",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615038050&level=1",
        "multiround_convo": 2,
        "description": "Q5. Are there any conflicting definitions or interpretations that could create confusion",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q5. Are there significant conflicts or tradeoffs between stakeholders or system elements? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q6",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615386880&level=1",
        "multiround_convo": 2,
        "description": "Q6. Are objectives, priorities, and constraints clearly communicated and well-defined?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q6. How clear is the problem definition and scope? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q7",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615778653&level=1",
        "multiround_convo": 2,
        "description": "Q7. To what extent are key inputs interdependent?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q7. How adequate are current resources (people, budget, technology) to handle the issue? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q8",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758616081630&level=1",
        "multiround_convo": 2,
        "description": "Q8. How well are the governing rules, functions, and relationships between inputs understood?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q8. How complex is the problem in terms of stakeholders, processes, or technology involved? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q9",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758616793510&level=1",
        "multiround_convo": 2,
        "description": "Q9. Are there any hidden or latent dependencies that could impact outcomes?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q9. How dependent is the problem on external factors or third parties? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q10",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758617140479&level=1",
        "multiround_convo": 2,
        "description": "Q10. Are there hidden or latent dependencies that could affect outcomes?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q10. What is the risk/impact if this problem remains unresolved? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q11",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758618137301&level=1",
        "multiround_convo": 2,
        "description": "Q11. Are feedback loops insufficient or missing, limiting our ability to adapt?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q11. How urgent is it to address this problem? Score 0–5. Provide justification."
        )
    },
    {
        "name": "Q12",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758619317968&level=1",
        "multiround_convo": 2,
        "description": "Q12. Do we lack established benchmarks or \"gold standards\" to validate results?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q12. How well does solving this problem align with organizational strategy or goals? Score 0–5. Provide justification."
        )
    },
 {
        "name": "hardness_summary",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758619658634&level=1",
        "multiround_convo": 2,
        "description": "Hardness Level, Summary & Key Takeaways",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\n"
            "Context from all previous analysis:\n"
            f"Current System:\n{outputs.get('current_system','')}\n"
            f"Q1:\n{outputs.get('Q1','')}\n"
            f"Q2:\n{outputs.get('Q2','')}\n"
            f"Q3:\n{outputs.get('Q3','')}\n"
            f"Q4:\n{outputs.get('Q4','')}\n"
            f"Q5:\n{outputs.get('Q5','')}\n"
            f"Q6:\n{outputs.get('Q6','')}\n"
            f"Q7:\n{outputs.get('Q7','')}\n"
            f"Q8:\n{outputs.get('Q8','')}\n"
            f"Q9:\n{outputs.get('Q9','')}\n"
            f"Q10:\n{outputs.get('Q10','')}\n"
            f"Q11:\n{outputs.get('Q11','')}\n"
            f"Q12:\n{outputs.get('Q12','')}\n\n"
            "Based on all the Q1-Q12 analysis above (which includes individual scores and detailed explanations), "
            "provide a comprehensive assessment with the following sections IN THIS EXACT FORMAT:\n\n"
            "Individual Question Scores\n"
            "• Q1: [score]\n"
            "• Q2: [score]\n"
            "...\n\n"
            "Dimension Averages\n"
            "• Volatility: (Q1 + Q2 + Q3) / 3 = [calculation] = [result]\n"
            "• Ambiguity: (Q4 + Q5 + Q6) / 3 = [calculation] = [result]\n"
            "• Interconnectedness: (Q7 + Q8 + Q9) / 3 = [calculation] = [result]\n"
            "• Uncertainty: (Q10 + Q11 + Q12) / 3 = [calculation] = [result]\n\n"
            "Overall Hardness Score\n"
            "[Provide calculation and final score]\n\n"
            "Hardness Level\n"
            "[Easy: 0-3.0, Moderate: 3.1-4.0, or Hard: 4.1-5.0]\n\n"
            "SME Justification\n"
            "[Provide detailed justification analyzing all four dimensions with specific insights]\n\n"
            "Summary\n"
            "[Provide a concise summary of the overall assessment in 2-3 sentences]\n\n"
            "Key Takeaways\n"
            "[Provide 3-5 bullet points with actionable insights]\n\n"
            "IMPORTANT: Make sure each section is clearly labeled with its header as shown above."
        )
    }
]

# Dimension mapping
DIMENSION_QUESTIONS = {
    "Volatility": ["Q1", "Q2", "Q3"],
    "Ambiguity": ["Q4", "Q5", "Q6"],
    "Interconnectedness": ["Q7", "Q8", "Q9"],
    "Uncertainty": ["Q10", "Q11", "Q12"]
}

# -----------------------------
# Utility Functions
# -----------------------------
def json_to_text(data):
    if data is None: 
        return ""
    if isinstance(data, str): 
        return data
    if isinstance(data, dict):
        for key in ("result", "output", "content", "text"):
            if key in data and data[key]: 
                return json_to_text(data[key])
        if "data" in data: 
            return json_to_text(data["data"])
        return "\n".join(f"{k}: {json_to_text(v)}" for k, v in data.items() if v)
    if isinstance(data, list): 
        return "\n".join(json_to_text(x) for x in data if x)
    return str(data)

def sanitize_text(text):
    """Remove markdown artifacts and clean up text"""
    if not text:
        return ""
    
    # Fix the "s" character issue - remove stray 's' characters at the beginning
    text = re.sub(r'^\s*s\s+', '', text.strip())
    text = re.sub(r'\n\s*s\s+', '\n', text)
    
    text = re.sub(r'Q\d+\s*Answer\s*Explanation\s*:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'<\/?[^>]+>', '', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'& Key Takeaway:', 'Key Takeaway:', text)
    
    return text.strip()

def extract_full_sme_justification(text):
    """Extract the complete SME Justification section for page 1"""
    if not text:
        return ""
    # Look for SME Justification section and extract everything in it.
    # Be flexible about spacing and headers that follow (Summary, Key Takeaways, Individual Question Scores, Dimension Averages, Overall Hardness Score, Hardness Level)
    patterns = [
        r"SME Justification[:\s]*((?:.|\n)*?)(?=\n\s*(?:Summary|Key Takeaways|Key Takeaway|Individual Question Scores|Dimension Averages|Overall Hardness Score|Hardness Level|$))",
        r"Justification[:\s]*((?:.|\n)*?)(?=\n\s*(?:Summary|Key Takeaways|Key Takeaway|Individual Question Scores|Dimension Averages|Overall Hardness Score|Hardness Level|$))",
        r"SME[:\s]*((?:.|\n)*)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            justification = match.group(1).strip()
            if justification:
                return format_sme_justification(justification)

    # If no specific section found, return the entire text (it might be just the justification)
    return format_sme_justification(text)

def format_sme_justification(text):
    """Format SME justification with proper HTML formatting"""
    if not text:
        return ""
    
    # Clean up the text
    text = sanitize_text(text)
    
    # Format dimension headings with bold
    text = re.sub(r'(Volatility|Ambiguity|Interconnectedness|Uncertainty)[:\s]*([\d.]+)?', 
                 r'<strong>\1\2</strong>', text)
    
    # Format bullet points
    text = re.sub(r'•\s*', '<br>• ', text)
    text = re.sub(r'(\w):\s*•', r'\1:<br>•', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Convert remaining newlines to HTML breaks for display in Streamlit
    text = text.strip()
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    return text
def extract_comprehensive_analysis(text):
    """Extract everything from API response EXCEPT score calculations and SME Justification"""
    if not text:
        return ""
    # First, try to explicitly extract Summary and Key Takeaways if present.
    # This ensures the final page surfaces the concise summary and bullets the user expects.
    summary_match = re.search(r"Summary[:\s]*((?:.|\n)*?)(?=\n\s*Key Takeaways|\n\s*Key Takeaway|$)", text, flags=re.IGNORECASE | re.DOTALL)
    key_takeaways_match = re.search(r"Key Takeaways?[:\s]*((?:.|\n)*)$", text, flags=re.IGNORECASE | re.DOTALL)

    parts = []
    if summary_match:
        summary = summary_match.group(1).strip()
        if summary:
            parts.append("Summary:\n" + summary)

    if key_takeaways_match:
        kt = key_takeaways_match.group(1).strip()
        if kt:
            parts.append("Key Takeaways:\n" + kt)

    if parts:
        combined = "\n\n".join(parts)
        # Sanitize and convert newlines to HTML breaks for proper display in Streamlit
        cleaned = sanitize_text(combined)
        cleaned = cleaned.replace('\r\n', '\n')
        cleaned = cleaned.replace('\n\n', '<br><br>')
        cleaned = cleaned.replace('\n', '<br>')
        return cleaned

    # If specific sections aren't present, fall back to the previous approach:
    # remove detailed score/calculation sections and SME Justification, leaving the remaining prose.
    # Remove Individual Question Scores section
    text = re.sub(
        r'Individual Question Scores.*?(?=\n\nDimension|\n\nOverall|\n\nHardness|\n\nSME|\Z)',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove Dimension Averages section
    text = re.sub(
        r'Dimension Averages.*?(?=\n\nOverall|\n\nHardness|\n\nSME|\Z)',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove Overall Difficulty Score section
    text = re.sub(
        r'Overall Hardness Score.*?(?=\n\nHardness|\n\nSME|\Z)',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove Hardness Level section
    text = re.sub(
        r'Hardness Level.*?(?=\n\nSME|\Z)',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove SME Justification section
    text = re.sub(
        r'SME Justification.*',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove any remaining score-related patterns
    score_patterns = [
        r'Q\d+\s*Score.*?\n',
        r'Score:.*?\n',
        r'\d+\.\d+\s*/\s*5',
        r'Individual.*?Scores',
        r'Dimension.*?Averages',
        r'Overall.*?Score',
        r'Hardness.*?Level'
    ]

    for pattern in score_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean up the remaining text
    text = sanitize_text(text)

    # Remove any empty sections and clean up formatting
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    # Convert newlines to HTML breaks for display
    text = text.replace('\r\n', '\n')
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')

    return text

def format_sme_justification(text):
    """Format SME justification with bold dimension headings and proper HTML"""
    if not text:
        return ""
    
    # Format dimension headings with bold and scores
    text = re.sub(r'(Volatility):\s*([\d.]+)', r'<strong>Volatility:</strong> \2/5', text)
    text = re.sub(r'(Ambiguity):\s*([\d.]+)', r'<strong>Ambiguity:</strong> \2/5', text)
    text = re.sub(r'(Interconnectedness):\s*([\d.]+)', r'<strong>Interconnectedness:</strong> \2/5', text)
    text = re.sub(r'(Uncertainty):\s*([\d.]+)', r'<strong>Uncertainty:</strong> \2/5', text)
    
    # Format bullet points
    text = re.sub(r'•\s*', '<br>• ', text)
    text = re.sub(r'(\w):\s*•', r'\1:<br>•', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def format_vocabulary_with_bold(text):  
    """Format vocabulary text with clean headings, spacing, and readable structure"""
    if not text:
        return "No vocabulary data available"
    
    clean_text = sanitize_text(text)

    # --- Fix line breaks between Step sections ---
    clean_text = re.sub(r'(Step\s*\d+:)', r'\n\n\1', clean_text)
    clean_text = re.sub(r'(?<=\.)\s*(Step\s*\d+:)', r'\n\n\1', clean_text)

    # --- Preserve numbered list breaks (1., 2., etc.) ---
    clean_text = re.sub(r'(?<!\n)(\d+\.)', r'\n\1', clean_text)
    
    # --- Make section headers bold ---
    clean_text = re.sub(r'(?<=\n)(Step\s*\d+:.*?)\n', r'\n<strong>\1</strong>\n', clean_text)
    clean_text = re.sub(r'(?<=\n)(\d+\.\s*VOCABULARY ANALYSIS)', r'\n<strong>\1</strong>', clean_text)
    
    # --- Make KPI formulas and key labels bold ---
    clean_text = re.sub(r'(\bFormula:)', r'<strong>\1</strong>', clean_text)
    clean_text = re.sub(r'(\bMeasures:)', r'<strong>\1</strong>', clean_text)
    clean_text = re.sub(r'(\bImportance:)', r'<strong>\1</strong>', clean_text)
    
    # --- Add line breaks for bullet points and after formulas ---
    clean_text = re.sub(r'•\s*', r'\n• ', clean_text)
    clean_text = re.sub(r'(?<=\))\s*•', r'\n•', clean_text)
    
    # --- Clean multiple spaces and excessive line breaks ---
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
    clean_text = re.sub(r' +', ' ', clean_text)
    
    # --- Wrap final output in pre-like block for consistent spacing ---
    formatted_output = f"<pre style='white-space: pre-wrap; font-family: Inter, sans-serif;'>{clean_text.strip()}</pre>"
    
    return formatted_output

def extract_individual_question_scores(text):
    """Extract scores for Q1-Q12 from the hardness_summary API response"""
    if not text:
        return {}
    
    scores = {}
    # First pass: simple inline patterns (Q7: 3, Q7 Score: 3, Q7 - 3)
    inline_patterns = [
        r"Q(\d+)(?:\s+Score)?:\s*(\d+(?:\.\d+)?)\s*(?:/\s*5)?",
        r"Question\s+(\d+).*?Score[:\s]+(\d+(?:\.\d+)?)",
        r"Q(\d+)\s*[-–]\s*(?:Score[:\s]+)?(\d+(?:\.\d+)?)",
        r"Q(\d+)[^\d]*?(\d+(?:\.\d+)?)\s*/\s*5",
    ]

    for pattern in inline_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            try:
                q_num = int(match.group(1))
                score = float(match.group(2))
                if 1 <= q_num <= 12 and 0 <= score <= 5:
                    scores[f"Q{q_num}"] = score
            except (ValueError, IndexError):
                continue

    # Second pass: scan each question block (from Qn up to next Q#) and look for a score anywhere inside that block.
    # This handles outputs where the question text appears first and the score appears later on a separate line.
    for q_num in range(1, 13):
        key = f"Q{q_num}"
        if key in scores:
            # already found via inline patterns
            continue

        # Build a non-greedy block pattern from this question to the next question or end of text
        block_pattern = rf"(Q{q_num}\b.*?)(?=\n\s*Q\d\b|\Z)"
        m = re.search(block_pattern, text, re.IGNORECASE | re.DOTALL)
        if not m:
            continue

        block = m.group(1)

        # look for common score formats inside the block
        block_patterns = [
            r"Score[:\s]*([0-5](?:\.\d+)?)",
            r"Final\s*Score[:\s]*([0-5](?:\.\d+)?)",
            r"([0-5](?:\.\d+)?)\s*/\s*5",
            r"[:\s]([0-5](?:\.\d+)?)(?:\s*/\s*5)?\s*$",  # number at end of block/line
        ]

        found = None
        for bp in block_patterns:
            bm = re.search(bp, block, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if bm:
                try:
                    val = float(bm.group(1))
                    if 0 <= val <= 5:
                        found = val
                        break
                except (ValueError, IndexError):
                    continue

        if found is not None:
            scores[key] = found

    return scores

def calculate_dimension_scores_from_questions(question_scores):
    """Calculate dimension averages from individual question scores"""
    dimensions = {
        "Volatility": ["Q1", "Q2", "Q3"],
        "Ambiguity": ["Q4", "Q5", "Q6"],
        "Interconnectedness": ["Q7", "Q8", "Q9"],
        "Uncertainty": ["Q10", "Q11", "Q12"]
    }
    
    dimension_scores = {}
    
    for dim_name, questions in dimensions.items():
        scores = [question_scores.get(q, 0) for q in questions if q in question_scores]
        if scores:
            dimension_scores[dim_name] = round(sum(scores) / len(scores), 2)
        else:
            dimension_scores[dim_name] = 0.0
    
    return dimension_scores

def calculate_overall_score_from_dimensions(dimension_scores):
    """Calculate overall difficulty score from dimension averages"""
    if not dimension_scores:
        return 0.0
    
    valid_scores = [s for s in dimension_scores.values() if s > 0]
    if valid_scores:
        return round(sum(valid_scores) / len(valid_scores), 2)
    return 0.0

def classify_hardness_level(overall_score):
    """Classify hardness level: 0-3.0=Easy, 3.1-4.0=Moderate, 4.1-5.0=Hard"""
    if overall_score <= 3.0:
        return "Easy"
    elif overall_score <= 4.0:
        return "Moderate"
    else:
        return "Hard"

def extract_current_system_sections(text):
    """Extract current system, inputs, outputs, and pain points from the current_system API response"""
    if not text:
        return {
            "current_system": "No current system information available",
            "inputs": "No input information available", 
            "outputs": "No output information available",
            "pain_points": "No pain points identified"
        }
    
    # Initialize sections
    sections = {
        "current_system": "",
        "inputs": "",
        "outputs": "",
        "pain_points": ""
    }
    
    # Try different patterns to extract sections
    patterns = [
        # Pattern 1: Numbered sections
        (r"1\.\s*Current\s+System[:\s]*(.*?)(?=2\.\s*Input|$)", "current_system"),
        (r"2\.\s*Input[:\s]*(.*?)(?=3\.\s*Output|$)", "inputs"),
        (r"3\.\s*Output[:\s]*(.*?)(?=4\.\s*Pain\s+Points|$)", "outputs"),
        (r"4\.\s*Pain\s+Points[:\s]*(.*?)$", "pain_points"),
        
        # Pattern 2: Bold sections
        (r"\*\*Current System\*\*[:\s]*(.*?)(?=\*\*Input|\*\*Output|\*\*Pain Points|$)", "current_system"),
        (r"\*\*Input\*\*[:\s]*(.*?)(?=\*\*Output|\*\*Pain Points|$)", "inputs"),
        (r"\*\*Output\*\*[:\s]*(.*?)(?=\*\*Pain Points|$)", "outputs"),
        (r"\*\*Pain Points\*\*[:\s]*(.*?)$", "pain_points"),
        
        # Pattern 3: Section headers without formatting
        (r"Current System[:\s]*(.*?)(?=Input|Output|Pain Points|$)", "current_system"),
        (r"Input[:\s]*(.*?)(?=Output|Pain Points|$)", "inputs"),
        (r"Output[:\s]*(.*?)(?=Pain Points|$)", "outputs"),
        (r"Pain Points[:\s]*(.*?)$", "pain_points")
    ]
    
    for pattern, section in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 10:  # Only use if substantial content
                sections[section] = sanitize_text(content)
    
    # If no structured sections found, use the entire text as current system
    if not any(sections.values()):
        sections["current_system"] = sanitize_text(text)
    
    return sections

# -----------------------------
# Session State Initialization
# -----------------------------
def init_session_state():
    defaults = {
        "current_page": "page1",
        "problem_text": "",
        "industry": "Select Industry",
        "account": "Select Account",
        "account_input": "",
        "outputs": {},
        "analysis_complete": False,
        "dimension_scores": {
            "Volatility": 0.0,
            "Ambiguity": 0.0, 
            "Interconnectedness": 0.0,
            "Uncertainty": 0.0
        },
        "question_scores": {},
        "hardness_level": None,
        "overall_score": 0.0,
        "summary": "",
        "current_system_full": "",
        "input_text": "",
        "output_text": "",
        "pain_points_text": "",
        "hardness_summary_text": "",
        "show_vocabulary": False,
        "industry_updated": False  # ADDED: For tracking industry updates
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()


def reset_app_state():
    """Reset session state to defaults for a new analysis."""
    # Store only the essential page state
    preserved_page = st.session_state.get('current_page', 'page1')
    
    # Clear all session state
    st.session_state.clear()
    
    # Re-initialize with defaults
    init_session_state()
    
    # Restore the page but keep default selections
    st.session_state.current_page = preserved_page
    
    # Ensure dropdowns show correct default values
    st.session_state.account = 'Select Account'
    st.session_state.industry = 'Select Industry'
    st.session_state.problem_text = ''
    st.session_state.account_input = ''
    st.session_state.outputs = {}
    st.session_state.analysis_complete = False
    st.session_state.show_vocabulary = False
    st.session_state.question_scores = {}
    st.session_state.dimension_scores = {
        'Volatility': 0.0,
        'Ambiguity': 0.0,
        'Interconnectedness': 0.0,
        'Uncertainty': 0.0
    }
    st.session_state.overall_score = 0.0
    st.session_state.hardness_level = None
    st.session_state.summary = ''
    st.session_state.current_system_full = ''
    st.session_state.input_text = ''
    st.session_state.output_text = ''
    st.session_state.pain_points_text = ''
    st.session_state.hardness_summary_text = ''
    st.session_state.industry_updated = False
    
    # Use success message without rerun to avoid double execution
    st.success("Application state reset. You can start a new analysis.")
# -----------------------------
# PAGE 1: Business Problem Input & Analysis
# -----------------------------
if st.session_state.current_page == "page1":
    st.markdown("""
    <div class="page-title" style="text-align:center; margin-bottom:1.5rem;">
        <h1 style="font-weight:800; color:#ffffff;">Business Problem Level Classifier</h1>
        <p style="
            font-size:1.1rem; 
            color:#ffffff; 
            font-family:'Open Sans', sans-serif; 
            font-weight:300; 
            letter-spacing:0.5px; 
            margin-top:-0.3rem;">
            A quick way for every TDS & AL to validate problem depth before diving in.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Account & Industry Selection - FIXED WITH PROPER DROPDOWN UPDATES
    st.markdown('<div class="section-title-box"><h3>Account & Industry Selection</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Get current account safely
        current_account = st.session_state.get('account', 'Select Account')
        try:
            current_account_index = ACCOUNTS.index(current_account)
        except (ValueError, AttributeError):
            current_account_index = 0
        
        # Account selector - use key to track changes
        selected_account = st.selectbox(
            "Select Account:",
            options=ACCOUNTS,
            index=current_account_index,
            key="account_selector"
        )
        
        # Update session state immediately when account changes
        if selected_account != st.session_state.get('account'):
            st.session_state.account = selected_account
            # Auto-map industry when account changes
            if selected_account in ACCOUNT_INDUSTRY_MAP:
                st.session_state.industry = ACCOUNT_INDUSTRY_MAP[selected_account]
                # Force update the industry dropdown by using a unique key
                st.session_state.industry_updated = True
            st.rerun()

    with col2:
        # Get current industry safely - this will reflect the auto-mapped value
        current_industry = st.session_state.get('industry', 'Select Industry')
        try:
            current_industry_index = INDUSTRIES.index(current_industry)
        except (ValueError, AttributeError):
            current_industry_index = 0
        
        # Create a unique key for industry selector that changes when industry updates
        industry_key = f"industry_selector_{current_industry}"
        
        # Industry selector - use dynamic key to force update
        selected_industry = st.selectbox(
            "Industry:",
            options=INDUSTRIES,
            index=current_industry_index,
            key=industry_key,
            disabled=(st.session_state.get('account', 'Select Account') == "Select Account")
        )
        
        # Update session state immediately when industry changes
        if selected_industry != st.session_state.get('industry'):
            st.session_state.industry = selected_industry
            st.rerun()

    # Display current selections for user feedback
    if st.session_state.get('account') != 'Select Account' and st.session_state.get('industry') != 'Select Industry':
        st.markdown(f"""
        <div style="background: rgba(139, 30, 30, 0.05); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid var(--accent-orange);">
            <strong>Selected:</strong> 
            <span style="color: var(--musigma-red); font-weight: 600;">{st.session_state.account}</span> | 
            <span style="color: var(--accent-orange); font-weight: 600;">{st.session_state.industry}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Business Problem Description
    st.markdown('<div class="section-title-box"><h3>Business Problem Description</h3></div>', unsafe_allow_html=True)
    
    # Initialize problem_text if not exists
    if 'problem_text' not in st.session_state:
        st.session_state.problem_text = ""
    
    st.session_state.problem_text = st.text_area(
        "Describe your business problem in detail:",
        value=st.session_state.problem_text,
        height=200,
        placeholder="Enter a detailed description of your business challenge...",
        label_visibility="collapsed",
        key="problem_text_area"
    )
    
    # Analysis Button
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_btn = st.button(
            "Find Out How Hard It Is",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.problem_text.strip() and 
                         st.session_state.industry != "Select Industry" and 
                         st.session_state.account != "Select Account"),
            key="analyze_btn"
        )
    
    with col2:
        # Vocabulary Button - only show after analysis
        if st.session_state.analysis_complete:
            vocab_label = "Hide Vocabulary" if st.session_state.get('show_vocabulary', False) else "View Vocabulary"
            if st.button(vocab_label, use_container_width=True, type="secondary", key="vocab_btn"):
                st.session_state.show_vocabulary = not st.session_state.get('show_vocabulary', False)
                st.rerun()
        else:
            # Placeholder to maintain layout
            st.button("Vocabulary", use_container_width=True, disabled=True)
    
    with col3:
        # Reset button
        if st.button("Reset", use_container_width=True, type="secondary", key="reset_btn"):
            reset_app_state()
    
    # Display vocabulary when toggled - COMPACT VERSION
    if st.session_state.analysis_complete and st.session_state.get('show_vocabulary', False):
        vocab_text = st.session_state.outputs.get('vocabulary', 'No vocabulary data available')
        formatted_vocab = format_vocabulary_with_bold(vocab_text)
        
        st.markdown(f'''
        <div class="vocab-display">
            <h4 style="color: var(--musigma-red) !important; margin-bottom: 1rem; text-align: center;">Extracted Vocabulary</h4>
            {formatted_vocab}
        </div>
        ''', unsafe_allow_html=True)
    
    if analyze_btn:
        # Validate inputs
        if not st.session_state.problem_text.strip():
            st.error("Please enter a business problem description.")
            st.stop()
        
        if st.session_state.account == "Select Account":
            st.error("Please select an account.")
            st.stop()
            
        if st.session_state.industry == "Select Industry":
            st.error("Please select an industry.")
            st.stop()
        
        full_problem_context = (
            f"The business problem is:\n{st.session_state.problem_text.strip()}\n\n"
            f"Context:\n"
            f"Industry: {st.session_state.industry}\n"
            f"Account/Customer: {st.session_state.account}"
        )

        HEADERS = HEADERS_BASE.copy()
        if TENANT_ID:
            HEADERS["Tenant-ID"] = TENANT_ID
            HEADERS["X-Tenant-ID"] = TENANT_ID
        if AUTH_TOKEN:
            HEADERS["Authorization"] = f"Bearer {AUTH_TOKEN}"
        
        HEADERS["Cache-Control"] = "no-cache, no-store, must-revalidate"
        HEADERS["Pragma"] = "no-cache"
        HEADERS["Expires"] = "0"
        
        with st.spinner("Analyzing your business problem..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            st.session_state.outputs = {}
            total_apis = len(API_CONFIGS)
            session = requests.Session()
            
            # Interesting analysis messages
            analysis_messages = [
                "🔍 Extracting key vocabulary and terminology...",
                "📊 Analyzing current system architecture...",
                "⚡ Assessing business volatility factors...",
                "❓ Evaluating ambiguity in requirements...",
                "🔗 Mapping interconnected dependencies...",
                "🎲 Calculating uncertainty levels...",
                "📈 Scoring problem dimensions...",
                "🧮 Calculating overall difficulty...",
                "📋 Generating comprehensive summary...",
                "🎯 Finalizing hardness classification...",
                "💡 Identifying key pain points...",
                "Analyzing system inputs and outputs...",
                "📝 Compiling stakeholder perspectives...",
                "🔎 Evaluating resource adequacy...",
                "🏆 Preparing final assessment..."
            ]
            
            for i, api_config in enumerate(API_CONFIGS):
                progress = (i / total_apis)
                progress_bar.progress(progress)
                
                # Show interesting messages with progress
                if i < len(analysis_messages):
                    status_text.info(f"{analysis_messages[i]} ({i+1}/{total_apis} completed)")
                else:
                    status_text.info(f"Processing analysis step {i+1} of {total_apis}...")
                
                try:
                    agency_goal = api_config["prompt"](full_problem_context, st.session_state.outputs)
                except Exception as e:
                    output_text = f"Error building prompt for {api_config['name']}: {e}"
                    st.session_state.outputs[api_config["name"]] = output_text
                    time.sleep(0.5)
                    continue

                payload = {
                    "agency_goal": agency_goal,
                    "multiround_convo": api_config.get("multiround_convo", 1),
                    "user_id": "talos-rest-endpoint"
                }

                try:
                    response = session.post(
                        api_config["url"], 
                        headers=HEADERS, 
                        json=payload, 
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        output_text = json_to_text(data)
                        output_text = sanitize_text(output_text)
                    else:
                        output_text = f"API Error HTTP {response.status_code}: {response.text}"
                
                except requests.exceptions.Timeout:
                    output_text = "Error calling API: Request timed out after 120 seconds."
                except Exception as e:
                    output_text = f"Error calling API: {str(e)}"
                
                st.session_state.outputs[api_config["name"]] = output_text
                time.sleep(0.5)

            session.close()
            progress_bar.progress(1.0)
            status_text.success("Analysis complete! All steps finished.")
            
            # Extract scores from hardness_summary API
            hardness_summary = st.session_state.outputs.get('hardness_summary', '')
            st.session_state.hardness_summary_text = hardness_summary
            
            # Extract Q1-Q12 scores
            question_scores = extract_individual_question_scores(hardness_summary)
            st.session_state.question_scores = question_scores
            
            # Calculate dimension scores
            calculated_dimensions = calculate_dimension_scores_from_questions(question_scores)
            
            for dimension in ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]:
                if dimension in calculated_dimensions and calculated_dimensions[dimension] > 0:
                    st.session_state.dimension_scores[dimension] = calculated_dimensions[dimension]
                else:
                    st.session_state.dimension_scores[dimension] = 0.0
            
            # Calculate overall score
            st.session_state.overall_score = calculate_overall_score_from_dimensions(st.session_state.dimension_scores)
            
            # Classify hardness
            st.session_state.hardness_level = classify_hardness_level(st.session_state.overall_score)
            
            # Extract FULL SME Justification
            st.session_state.summary = extract_full_sme_justification(hardness_summary)
            
            # Extract current system details with improved parsing
            current_system_text = st.session_state.outputs.get('current_system', '')
            sections = extract_current_system_sections(current_system_text)
            st.session_state.current_system_full = sections["current_system"]
            st.session_state.input_text = sections["inputs"]
            st.session_state.output_text = sections["outputs"]
            st.session_state.pain_points_text = sections["pain_points"]
            
            st.session_state.analysis_complete = True
            st.session_state.show_vocabulary = False  # Reset vocabulary toggle
            st.rerun()
    
    # Display Results
    if st.session_state.analysis_complete:
        st.markdown("---")
        
        # Hardness Level & Score
        col1, col2 = st.columns(2)
        
        with col1:
            hardness = st.session_state.hardness_level
            if hardness == "Hard":
                badge_class = "hardness-badge-hard"
                icon = "🔴"
            elif hardness == "Moderate":
                badge_class = "hardness-badge-moderate"
                icon = "🟡"
            else:
                badge_class = "hardness-badge-easy"
                icon = "🟢"
            
            st.markdown(f'<div class="{badge_class}">{icon} {hardness}</div>', unsafe_allow_html=True)
        
        with col2:
            overall = st.session_state.overall_score
            st.markdown(f'''
            <div class="score-badge">
                <div style="font-size: 1.2rem; font-weight: 600; opacity: 0.95; margin-bottom: 0.5rem;">Overall Hardness Score</div>
                <div style="font-size: 2.8rem; font-weight: 900;">{overall:.2f}/5</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Dimension Scores
        st.markdown('<div class="section-title-box"><h3>Dimension Scores</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
        dimension_icons = ["⚡", "❓", "🔗", "🎲"]
        for i, dimension in enumerate(dimensions):
            with col1 if i < 2 else col2:
                score = st.session_state.dimension_scores.get(dimension, 0.0)
                st.markdown(f'''
                <div class="dimension-display-box">
                    <div class="dimension-label"><span class="dim-icon">{dimension_icons[i]}</span> {dimension}</div>
                    <div class="dimension-score">{score:.2f}/5</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # SME Justification Section - FULL CONTENT in orange-bordered box
        st.markdown('<div class="section-title-box"><h3>Justification</h3></div>', unsafe_allow_html=True)

        # Prefer extracting the full SME Justification from the raw hardness_summary_text to avoid trimmed paragraphs
        full_hs = st.session_state.get('hardness_summary_text', '')
        full_sme = ''
        if full_hs and full_hs.strip():
            full_sme = extract_full_sme_justification(full_hs)

        if full_sme:
            st.markdown(f'<div class="info-card">{full_sme}</div>', unsafe_allow_html=True)
        elif st.session_state.summary:
            st.markdown(f'<div class="info-card">{st.session_state.summary}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-card">SME Justification not available.</div>', unsafe_allow_html=True)

        # Large In Detail Button
        st.markdown("---")
        if st.button("View In Detail Analysis →", key="in_detail_main", use_container_width=True, type="primary"):
            st.session_state.current_page = "page2"
            st.rerun()
# -----------------------------
# PAGE 2: Current System & Pain Points - IMPROVED LAYOUT
# -----------------------------
if st.session_state.current_page == "page2":
    st.markdown('<div class="page-title"><h1>Current System & Pain Points</h1></div>', unsafe_allow_html=True)

    # Business Problem in text area style box
    st.markdown('<div class="section-title-box"><h3>Business Problem</h3></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="problem-display"><p>{st.session_state.problem_text}</p></div>', unsafe_allow_html=True)

    if st.button("← Back to Analysis", use_container_width=False):
        st.session_state.current_page = "page1"
        st.rerun()

    # Current System - in info-card (white background)
    if st.session_state.current_system_full and st.session_state.current_system_full.strip():
        st.markdown('<div class="section-title-box"><h3>1. Current System</h3></div>', unsafe_allow_html=True)
        formatted_text = st.session_state.current_system_full.replace('\n', '<br>')
        st.markdown(f'<div class="info-card">{formatted_text}</div>', unsafe_allow_html=True)

    # Inputs & Outputs - Side by side in columns with info-cards
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.input_text and st.session_state.input_text.strip():
            st.markdown('<div class="section-title-box"><h3>2. Input</h3></div>', unsafe_allow_html=True)
            formatted_input = st.session_state.input_text.replace('\n', '<br>')
            st.markdown(f'<div class="info-card">{formatted_input}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-title-box"><h3>2. Input</h3></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-card">No input information available</div>', unsafe_allow_html=True)

    with col2:
        if st.session_state.output_text and st.session_state.output_text.strip():
            st.markdown('<div class="section-title-box"><h3>3. Output</h3></div>', unsafe_allow_html=True)
            formatted_output = st.session_state.output_text.replace('\n', '<br>')
            st.markdown(f'<div class="info-card">{formatted_output}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-title-box"><h3>3. Output</h3></div>', unsafe_allow_html=True)
            st.markdown('<div class="info-card">No output information available</div>', unsafe_allow_html=True)

    # Pain Points - in info-card (white background)
    if st.session_state.pain_points_text and st.session_state.pain_points_text.strip():
        st.markdown('<div class="section-title-box"><h3>4. Pain Points</h3></div>', unsafe_allow_html=True)
        formatted_pain = st.session_state.pain_points_text.replace('\n', '<br>')
        st.markdown(f'<div class="info-card">{formatted_pain}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-title-box"><h3>4. Pain Points</h3></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-card">No pain points identified</div>', unsafe_allow_html=True)

    # Dimension Scores Section - REMOVED COMPREHENSIVE ANALYSIS HEADING
    st.markdown('<div class="section-title-box"><h3>Dimension Analysis</h3></div>', unsafe_allow_html=True)
    
    # Make the click text visible
    st.markdown('<div class="dimension-click-text">Click dimension boxes to view detailed analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)
    dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
    # Icons removed to avoid colored emoji rendering; using neutral placeholders instead
    dimension_icons = ["", "", "", ""]

    for i, dimension in enumerate(dimensions):
        with col1 if i < 2 else col2:
            score = st.session_state.dimension_scores.get(dimension, 0.0)
            st.markdown(f'''
            <div class="dimension-box">
                <div class="dimension-label"><span class="dim-icon">{dimension_icons[i]}</span> {dimension}</div>
                <div class="dimension-score">{score:.2f}/5</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"View {dimension} Details →", key=f"dim_{dimension}", use_container_width=True):
                st.session_state.current_page = f"dimension_{dimension.lower()}"
                st.rerun()

    # Navigation
    st.markdown("---")
    if st.button("View Hardness Summary →", use_container_width=True, type="primary"):
        st.session_state.current_page = "hardness_summary"
        st.rerun()

# -----------------------------
# DIMENSION DETAIL PAGES
# -----------------------------
elif st.session_state.current_page.startswith("dimension_"):
    dimension_name = st.session_state.current_page.replace("dimension_", "").title()
    dimension_icons = {
        "Volatility": "⚡",
        "Ambiguity": "❓", 
        "Interconnectedness": "🔗",
        "Uncertainty": "🎲"
    }
    
    st.markdown(f'<div class="page-title"><h1>{dimension_icons.get(dimension_name, "")} {dimension_name} Analysis</h1></div>', unsafe_allow_html=True)
    
    # Business Problem - in problem-display box (text area style)
    st.markdown('<div class="section-title-box"><h3>Business Problem</h3></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="problem-display"><p>{st.session_state.problem_text}</p></div>', unsafe_allow_html=True)
    
    # Display dimension score
    score = st.session_state.dimension_scores.get(dimension_name, 0.0)
    st.markdown(f'''
    <div class="score-badge" style="margin-bottom: 3rem;">
        <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">{dimension_icons.get(dimension_name, "")} {dimension_name} Score</div>
        <div style="font-size: 3.2rem; font-weight: 900;">{score:.2f}/5</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Display Q&A for this dimension - in qa-boxes
    st.markdown('<div class="section-title-box"><h3>Detailed Analysis</h3></div>', unsafe_allow_html=True)
    
    questions = DIMENSION_QUESTIONS.get(dimension_name, [])
    
    for q_name in questions:
        answer_text = st.session_state.outputs.get(q_name, "No analysis available")
        clean_answer = sanitize_text(answer_text)
        
        # Get the question description
        q_description = next((api["description"] for api in API_CONFIGS if api["name"] == q_name), q_name)
        
        st.markdown(f'<div class="qa-box"><div class="qa-question">{q_description}</div><div class="qa-answer">{clean_answer.replace(chr(10), "<br>")}</div></div>', unsafe_allow_html=True)
    
    # Navigation buttons - 3-column layout for all dimension pages
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if dimension_name == "Volatility":
            if st.button("🏠 Back to Main Analysis", use_container_width=True, type="primary", key=f"home_{dimension_name}"):
                st.session_state.current_page = "page1"
                st.rerun()
        elif dimension_name == "Ambiguity":
            if st.button("← Back to Volatility", use_container_width=True, type="primary", key=f"back_{dimension_name}"):
                st.session_state.current_page = "dimension_volatility"
                st.rerun()
        elif dimension_name == "Interconnectedness":
            if st.button("← Back to Ambiguity", use_container_width=True, type="primary", key=f"back_{dimension_name}"):
                st.session_state.current_page = "dimension_ambiguity"
                st.rerun()
        elif dimension_name == "Uncertainty":
            if st.button("← Back to Interconnectedness", use_container_width=True, type="primary", key=f"back_{dimension_name}"):
                st.session_state.current_page = "dimension_interconnectedness"
                st.rerun()
    
    with col2:
        if st.button("Reset", use_container_width=True, type="secondary", key=f"reset_{dimension_name}"):
            reset_app_state()
            st.rerun()
    
    with col3:
        if dimension_name == "Volatility":
            if st.button("Next → Ambiguity", use_container_width=True, type="primary", key="next_volatility"):
                st.session_state.current_page = "dimension_ambiguity"
                st.rerun()
        elif dimension_name == "Ambiguity":
            if st.button("Next → Interconnectedness", use_container_width=True, type="primary", key="next_ambiguity"):
                st.session_state.current_page = "dimension_interconnectedness"
                st.rerun()
        elif dimension_name == "Interconnectedness":
            if st.button("Next → Uncertainty", use_container_width=True, type="primary", key="next_interconnectedness"):
                st.session_state.current_page = "dimension_uncertainty"
                st.rerun()
        elif dimension_name == "Uncertainty":
            if st.button("View Hardness Summary →", use_container_width=True, type="primary", key="next_uncertainty"):
                st.session_state.current_page = "hardness_summary"
                st.rerun()

# -----------------------------
# HARDNESS SUMMARY PAGE
# -----------------------------
elif st.session_state.current_page == "hardness_summary":
    # Add JavaScript to scroll to top when page loads
    st.markdown("""
    <script>
        window.addEventListener('load', function() {
            window.scrollTo(0, 0);
        });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown('''
    <div class="page-title">
        <h1>Hardness Summary Analysis</h1>
    </div>
    ''', unsafe_allow_html=True)
    
    # Business Problem
    st.markdown('''
    <div class="section-title-box">
        <h3>Business Problem</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="problem-display">
        <p>{st.session_state.problem_text}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Display Scores Summary
    st.markdown('''
    <div class="section-title-box">
        <h3>Score Breakdown</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Question Scores
    if st.session_state.question_scores:
        st.markdown('''
        <div class="section-title-box">
            <h4>Individual Question Scores</h4>
        </div>
        ''', unsafe_allow_html=True)
        
        scores_html = '<div class="info-card"><div class="scores-grid">'
        for q, score in sorted(st.session_state.question_scores.items(), key=lambda x: int(x[0][1:])):
            scores_html += f'<div class="score-item"><strong>{q}:</strong><br><span class="score-value">{score:.2f}/5</span></div>'
        scores_html += '</div></div>'
        st.markdown(scores_html, unsafe_allow_html=True)
    
    # Dimension Averages
    st.markdown('''
    <div class="section-title-box">
        <h4>Dimension Averages</h4>
    </div>
    ''', unsafe_allow_html=True)
    
    dimensions_html = '<div class="info-card">'
    dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
    
    for dimension in dimensions:
        score = st.session_state.dimension_scores.get(dimension, 0.0)
        questions = DIMENSION_QUESTIONS.get(dimension, [])
        q_list = ", ".join(questions)
        dimensions_html += f'<div class="dim-item"><strong>{dimension}</strong><br><span style="color: var(--text-secondary); font-size: 0.9rem;">({q_list})</span><br><span class="dim-score">{score:.2f}/5</span></div>'
    dimensions_html += '</div>'
    st.markdown(dimensions_html, unsafe_allow_html=True)
    
    # Overall Score and Level
    st.markdown('''
    <div class="section-title-box">
        <h3>Overall Classification</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        <div class="score-badge" style="margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 500; opacity: 0.9; margin-bottom: 0.5rem;">Overall Hardness Score</div>
            <div style="font-size: 2.5rem; font-weight: 900;">{st.session_state.overall_score:.2f}/5</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        hardness = st.session_state.hardness_level
        if hardness == "Hard":
            badge_class = "hardness-badge-hard"
            icon = "🔴"
        elif hardness == "Moderate":
            badge_class = "hardness-badge-moderate"
            icon = "🟡"
        else:
            badge_class = "hardness-badge-easy"
            icon = "🟢"
        
        st.markdown(f'''
        <div class="{badge_class}" style="margin-bottom: 1rem;">
            <div style="font-size: 1rem; opacity: 0.9; margin-bottom: 0.5rem;">Hardness Level</div>
            <div style="font-size: 2.2rem; font-weight: 900;">{icon} {hardness}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Comprehensive Analysis
    st.markdown('''
    <div class="section-title-box">
        <h3>Comprehensive Analysis</h3>
    </div>
    ''', unsafe_allow_html=True)

    if st.session_state.hardness_summary_text:
        hs_text = st.session_state.hardness_summary_text
        comprehensive_analysis = extract_comprehensive_analysis(hs_text)

        if comprehensive_analysis and comprehensive_analysis.strip():
            st.markdown(f'<div class="info-card">{comprehensive_analysis}</div>', unsafe_allow_html=True)
        else:
            sme = st.session_state.get('summary') or extract_full_sme_justification(hs_text)
            if sme:
                st.markdown(f'<div class="info-card">{sme}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-card">No comprehensive analysis or SME justification available.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-card">No hardness summary data available.</div>', unsafe_allow_html=True)

    # Bottom Navigation with 3-column layout
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Previous Page", use_container_width=True, type="primary", key="back_prev_from_summary"):
            st.session_state.current_page = "dimension_uncertainty"
            st.rerun()

    with col2:
        if st.button("🏠 Back to Main Analysis", use_container_width=True, type="primary", key="back_home_from_summary"):
            st.session_state.current_page = "page1"
            st.rerun()

    with col3:
        # Build comprehensive report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("BUSINESS PROBLEM LEVEL CLASSIFIER - COMPREHENSIVE REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Session ID: {st.session_state.get('session_id', 'N/A')}")
        report_lines.append("")
        
        # Business Problem
        report_lines.append("BUSINESS PROBLEM")
        report_lines.append("-" * 40)
        report_lines.append(st.session_state.problem_text or "(no problem provided)")
        report_lines.append("")
        
        # Context
        report_lines.append("CONTEXT")
        report_lines.append("-" * 40)
        report_lines.append(f"Industry: {st.session_state.get('industry','')}")
        report_lines.append(f"Account: {st.session_state.get('account','')}")
        report_lines.append("")
        
        # API 1: Vocabulary
        report_lines.append("1. VOCABULARY ANALYSIS")
        report_lines.append("-" * 40)
        vocab_text = st.session_state.outputs.get('vocabulary', 'No vocabulary data available')
        report_lines.append(sanitize_text(vocab_text))
        report_lines.append("")
        
        # API 2: Current System
        report_lines.append("2. CURRENT SYSTEM ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append("Current System:")
        report_lines.append(st.session_state.get('current_system_full','') or "No current system details")
        report_lines.append("")
        report_lines.append("Inputs:")
        report_lines.append(st.session_state.get('input_text','') or "No inputs available")
        report_lines.append("")
        report_lines.append("Outputs:")
        report_lines.append(st.session_state.get('output_text','') or "No outputs available")
        report_lines.append("")
        report_lines.append("Pain Points:")
        report_lines.append(st.session_state.get('pain_points_text','') or "No pain points identified")
        report_lines.append("")
        
        # APIs 3-14: All 12 Questions (Q1-Q12)
        report_lines.append("3-14. DETAILED QUESTION ANALYSIS (Q1-Q12)")
        report_lines.append("-" * 40)
        
        question_descriptions = {
            "Q1": "What is the frequency and pace of change in the key inputs driving the business?",
            "Q2": "To what extent are these changes cyclical and predictable versus sporadic and unpredictable?",
            "Q3": "How resilient is the current system in absorbing these changes without requiring significant rework or disruption?",
            "Q4": "To what extent do stakeholders share a common understanding of the key terms and concepts?",
            "Q5": "Are there any conflicting definitions or interpretations that could create confusion?",
            "Q6": "Are objectives, priorities, and constraints clearly communicated and well-defined?",
            "Q7": "To what extent are key inputs interdependent?",
            "Q8": "How well are the governing rules, functions, and relationships between inputs understood?",
            "Q9": "Are there any hidden or latent dependencies that could impact outcomes?",
            "Q10": "Are there hidden or latent dependencies that could affect outcomes?",
            "Q11": "Are feedback loops insufficient or missing, limiting our ability to adapt?",
            "Q12": "Do we lack established benchmarks or 'gold standards' to validate results?"
        }
        
        for q_num in range(1, 13):
            q_key = f"Q{q_num}"
            report_lines.append(f"\nQ{q_num}. {question_descriptions.get(q_key, '')}")
            report_lines.append("-" * 60)
            
            # Add score if available
            score = st.session_state.question_scores.get(q_key, 'N/A')
            if score != 'N/A':
                report_lines.append(f"SCORE: {score}/5")
                report_lines.append("")
            
            # Add the detailed answer from the API
            answer_text = st.session_state.outputs.get(q_key, "No analysis available")
            clean_answer = sanitize_text(answer_text)
            report_lines.append(clean_answer)
            report_lines.append("")
        
        # API 15: Hardness Summary
        report_lines.append("15. HARDNESS SUMMARY & FINAL ASSESSMENT")
        report_lines.append("-" * 40)
        
        # Dimension Scores
        report_lines.append("DIMENSION SCORES:")
        report_lines.append("-" * 20)
        dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
        for dimension in dimensions:
            score = st.session_state.dimension_scores.get(dimension, 0.0)
            report_lines.append(f"  {dimension}: {score:.2f}/5")
        report_lines.append("")
        
        # Overall Classification
        report_lines.append("OVERALL CLASSIFICATION:")
        report_lines.append("-" * 20)
        report_lines.append(f"  Overall Hardness Score: {st.session_state.overall_score:.2f}/5")
        report_lines.append(f"  Hardness Level: {st.session_state.hardness_level}")
        report_lines.append("")
        
        # Hardness Summary API content
        hs_text = st.session_state.get('hardness_summary_text', 'No hardness summary available')
        report_lines.append("COMPREHENSIVE ASSESSMENT:")
        report_lines.append("-" * 20)
        report_lines.append(sanitize_text(hs_text))
        
        report_content = "\n".join(report_lines)
        
        # Download button with same styling as other buttons
        if st.button("Download Full Report", use_container_width=True, type="primary", key="download_report"):
            st.download_button(
                label="Download Full Report",
                data=report_content,
                file_name=f"business_problem_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )

# Remove the "all_questions" page entirely
# Update session persistence to prevent auto-reset
def init_session_state():
    defaults = {
        "current_page": "page1",
        "problem_text": "",
        "industry": "Select Industry",
        "account": "Select Account",
        "account_input": "",
        "outputs": {},
        "analysis_complete": False,
        "dimension_scores": {
            "Volatility": 0.0,
            "Ambiguity": 0.0, 
            "Interconnectedness": 0.0,
            "Uncertainty": 0.0
        },
        "question_scores": {},
        "hardness_level": None,
        "overall_score": 0.0,
        "summary": "",
        "current_system_full": "",
        "input_text": "",
        "output_text": "",
        "pain_points_text": "",
        "hardness_summary_text": "",
        "show_vocabulary": False,
        "industry_updated": False,
        "last_reset_time": time.time(),
        "session_id": str(time.time()) + str(random.randint(1000, 9999)),
        "initialized": True
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Enhanced session persistence
if 'initialized' not in st.session_state:
    init_session_state()

# Add auto-scroll JavaScript to all pages
st.markdown("""
<script>
    // Auto-scroll to top when page loads
    window.addEventListener('load', function() {
        window.scrollTo(0, 0);
    });
    
    // Also scroll to top when navigating (for SPA behavior)
    window.addEventListener('popstate', function() {
        window.scrollTo(0, 0);
    });
</script>
""", unsafe_allow_html=True)

# ======== REMOVE OR COMMENT OUT THE BOTTOM NAVIGATION CALL ========
# Don't call render_bottom_navigation() since we have custom navigation in each page

# Enhanced session persistence - prevent auto-reset on browser lock/refresh
st.markdown(f"""
<script>
    // Store session data in localStorage for persistence
    localStorage.setItem('musigma_session_id', '{st.session_state.get('session_id', '')}');
    localStorage.setItem('musigma_last_activity', '{time.time()}');
    
    // Restore session on page load
    window.addEventListener('load', function() {{
        const savedSessionId = localStorage.getItem('musigma_session_id');
        if (savedSessionId) {{
            // Session exists, don't auto-reset
            console.log('Restoring session:', savedSessionId);
        }}
    }});
</script>
""", unsafe_allow_html=True)


