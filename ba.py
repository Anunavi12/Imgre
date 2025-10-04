import streamlit as st
import requests, json, os, re, time
import random
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
import unicodedata
import pandas as pd

# -----------------------------
# Config - Page Setup
# -----------------------------
st.set_page_config(
    page_title="Business Problem Level Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* --- GOOGLE FONTS --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* --- HIDE DEFAULT STREAMLIT ELEMENTS --- */
#MainMenu, footer, header { visibility: hidden; }
.element-container:empty { display: none !important; }
div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }

/* --- MODERN COLOR VARIABLES --- */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --accent-orange: #FF6B35;
    --accent-coral: #8b1e1e;
    --accent-purple: #764ba2;
    --accent-teal: #2A9D8F;
    --bg-dark: #0f0f23;
    --bg-card: #1a1a2e;
    --bg-light: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #64748b;
    --text-light: #ffffff;
    --border-color: rgba(255, 107, 53, 0.2);
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
    --shadow-xl: 0 12px 48px rgba(0, 0, 0, 0.24);
}

/* --- SMOOTH ANIMATIONS --- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

/* --- APP BACKGROUND --- */
.main { 
    font-family: 'Inter', sans-serif; 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed; 
    min-height: 100vh; 
    padding: 2rem 1rem;
}
.stApp { background: transparent; }

/* --- MAIN PAGE TITLE --- */
.page-title { 
    background: rgba(255, 255, 255, 0.98);
    padding: 2rem 3rem; 
    border-radius: 20px; 
    text-align: center; 
    margin-bottom: 3rem; 
    box-shadow: var(--shadow-xl);
    animation: fadeInUp 0.6s ease-out; 
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.page-title h1 { 
    margin: 0; 
    font-weight: 800; 
    background: linear-gradient(135deg, var(--accent-orange), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    letter-spacing: -0.5px;
}

/* Mu-Sigma Logo - Fixed positioning with color protection */
.musigma-logo {
    position: fixed;
    top: 14px;
    right: 14px;
    width: 80px;
    height: 80px;
    border-radius: 10px;
    border: 2px solid rgba(255,255,255,0.9);
    box-shadow: 0 8px 28px rgba(0,0,0,0.18);
    z-index: 9999;
    background: transparent !important;
    opacity: 0.99;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    overflow: hidden;
    /* Prevent any color inheritance */
    background-color: transparent !important;
    background-image: none !important;
}

.musigma-logo:hover { 
    transform: translateY(-4px) scale(1.02); 
    box-shadow: 0 12px 36px rgba(0,0,0,0.22);
}

@media (max-width: 640px) { 
    .musigma-logo { 
        display: none !important; 
    } 
}

/* Logo image - complete color protection */
.musigma-logo img {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    display: block !important;
    /* Prevent any color filters or transformations */
    filter: none !important;
    mix-blend-mode: normal !important;
    background: transparent !important;
    /* Reset any inherited styles */
    color: inherit !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    /* Prevent any text rendering issues */
    font-size: 0 !important;
    line-height: 0 !important;
}

/* Link wrapper protection */
.musigma-logo-link {
    background: transparent !important;
    text-decoration: none !important;
    display: inline-block !important;
}

/* Force remove any gradient/color backgrounds */
.musigma-logo,
.musigma-logo *,
.musigma-logo-link,
.musigma-logo-link * {
    background: transparent !important;
    background-image: none !important;
    background-color: transparent !important;
    /* Remove any text color inheritance */
    color: inherit !important;
    -webkit-text-fill-color: inherit !important;
}

/* --- SECTION HEADINGS --- */
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
}

/* --- SECTION TITLE BOXES --- */
.section-title-box { 
    background: rgba(255, 255, 255, 0.98); 
    backdrop-filter: blur(16px);
    border-left: 4px solid var(--accent-orange);
    border-radius: 12px; 
    padding: 1.25rem 1.75rem; 
    margin: 2rem 0 1.5rem 0 !important; 
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s ease-out; 
}

.section-title-box h2,
.section-title-box h3,
.section-title-box h4 {
    color: var(--text-primary) !important;
    margin: 0 !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* --- INFO CARDS --- */
.info-card { 
    background: rgba(255, 255, 255, 0.98); 
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 16px; 
    padding: 2rem; 
    margin-bottom: 1.5rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.6s ease-out; 
}

.info-card:hover { 
    transform: translateY(-4px); 
    box-shadow: var(--shadow-lg);
}

.info-card,
.info-card *:not(h1):not(h2):not(h3):not(h4):not(h5):not(h6) { 
    color: var(--text-primary) !important; 
}

.info-card p, .info-card li, .info-card span {
    color: var(--text-primary) !important; 
    line-height: 1.7;
    font-size: 1rem;
}

.info-card h3, .info-card h4 {
    color: var(--accent-orange) !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
}

.info-card ul, .info-card ol { 
    margin-left: 1.5rem; 
    padding-left: 0.5rem; 
}

.info-card li { 
    margin-bottom: 0.5rem; 
}

/* --- PROBLEM DISPLAY --- */
.problem-display { 
    background: rgba(255, 255, 255, 0.98) !important; 
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 16px !important; 
    padding: 2rem !important; 
    margin-bottom: 2rem; 
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s ease-out;
}

.problem-display h4 { 
    color: var(--accent-orange) !important; 
    margin-top: 0; 
    font-weight: 700; 
    font-size: 1.25rem; 
    margin-bottom: 1rem;
}

.problem-display p { 
    color: var(--text-primary) !important; 
    line-height: 1.7;
    font-size: 1rem;
    margin: 0;
}

/* --- INPUT CARD --- */
.input-card { 
    background: rgba(255, 255, 255, 0.12); 
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 16px; 
    padding: 2rem; 
    margin-bottom: 2rem; 
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s ease-out; 
}

.input-card h3 { 
    color: var(--text-light) !important; 
    margin-top: 0; 
    font-weight: 700;
}

.input-card p, .input-card label { 
    color: rgba(255, 255, 255, 0.9) !important; 
}

/* --- Q&A BOXES --- */
.qa-box { 
    background: rgba(255, 255, 255, 0.98); 
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 16px; 
    padding: 1.75rem; 
    margin-bottom: 1.5rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.6s ease-out; 
}

.qa-box:hover { 
    transform: translateY(-4px); 
    box-shadow: var(--shadow-lg);
}

.qa-question { 
    font-weight: 700; 
    font-size: 1.1rem; 
    color: var(--accent-orange) !important; 
    margin-bottom: 1rem; 
    line-height: 1.6; 
    font-family: 'Space Grotesk', sans-serif;
}

.qa-answer { 
    font-size: 1rem; 
    line-height: 1.7; 
    color: var(--text-primary) !important; 
    white-space: pre-wrap; 
}

.qa-answer p, .qa-answer li, .qa-answer span { 
    color: var(--text-primary) !important; 
}

.qa-answer ul, .qa-answer ol { 
    margin-left: 1.5rem; 
    padding-left: 0.5rem; 
}

.qa-answer li { 
    margin-bottom: 0.5rem; 
}

/* --- SCORE BADGES --- */
.score-badge { 
    background: linear-gradient(135deg, var(--accent-orange), var(--accent-coral)); 
    padding: 2.5rem; 
    border-radius: 20px; 
    text-align: center; 
    color: var(--text-light); 
    box-shadow: var(--shadow-lg);
    animation: fadeInUp 0.6s ease-out; 
    min-height: 180px; 
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    justify-content: center; 
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.score-badge * { 
    color: var(--text-light) !important; 
}

/* --- HARDNESS BADGES --- */
.hardness-badge-hard, 
.hardness-badge-moderate, 
.hardness-badge-easy { 
    color: var(--text-light) !important; 
    padding: 2.5rem; 
    border-radius: 20px; 
    font-size: 1.8rem; 
    font-weight: 800; 
    text-align: center; 
    min-height: 180px; 
    display: flex; 
    flex-direction: column;
    align-items: center; 
    justify-content: center; 
    animation: fadeInUp 0.6s ease-out; 
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-lg);
}

.hardness-badge-hard { 
    background: linear-gradient(135deg, #E74C3C, #C0392B); 
}

.hardness-badge-moderate { 
    background: linear-gradient(135deg, #F39C12, #E67E22); 
}

.hardness-badge-easy { 
    background: linear-gradient(135deg, #27AE60, #229954); 
}

/* --- DIMENSION BOXES --- */
.dimension-box, 
.dimension-display-box { 
    color: var(--text-light) !important; 
    padding: 2rem; 
    border-radius: 16px; 
    text-align: center; 
    box-shadow: var(--shadow-md);
    min-height: 150px; 
    margin-bottom: 1.5rem; 
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInUp 0.6s ease-out; 
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.dimension-box { 
    background: linear-gradient(135deg, var(--accent-orange), var(--accent-coral)); 
    cursor: pointer;
}

.dimension-box:hover { 
    transform: translateY(-6px) scale(1.02); 
    box-shadow: var(--shadow-xl);
}

.dimension-display-box { 
    background: linear-gradient(135deg, var(--accent-orange), var(--accent-coral)); 
}

.dimension-display-box:hover { 
    transform: translateY(-4px); 
    box-shadow: var(--shadow-lg);
}

.dimension-score { 
    font-size: 3rem; 
    font-weight: 900; 
    margin: 0.75rem 0; 
    color: var(--text-light) !important; 
    font-family: 'Space Grotesk', sans-serif;
}

.dimension-label { 
    font-size: 1.15rem; 
    font-weight: 600; 
    color: var(--text-light) !important; 
    opacity: 0.95; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
    font-family: 'Space Grotesk', sans-serif;
}

/* --- VOCABULARY DISPLAY --- */
.vocab-display { 
    background: rgba(255, 255, 255, 0.98) !important; 
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 16px; 
    padding: 1.5rem; 
    line-height: 1.5 !important; 
    margin-top: 1rem;
    color: var(--text-primary) !important;
    font-size: 0.95rem;
    max-height: 500px;
    overflow-y: auto;
    box-shadow: var(--shadow-md);
}

.vocab-display * { 
    color: var(--text-primary) !important; 
    line-height: 1.5 !important;
}

.vocab-display strong {
    color: var(--accent-orange) !important;
    font-weight: 700 !important;
}

.vocab-item {
    margin-bottom: 0.75rem !important;
    padding-bottom: 0.75rem !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.vocab-item:last-child {
    border-bottom: none;
}

/* --- DIMENSION CLICK TEXT --- */
.dimension-click-text {
    color: rgba(255, 255, 255, 0.95) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    text-align: center;
    margin-bottom: 2rem !important;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    backdrop-filter: blur(8px);
}

/* --- INFO ICONS --- */
.info-icon { 
    font-size: 3rem; 
    display: inline-block; 
    margin-right: 1rem; 
    animation: float 3s ease-in-out infinite; 
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2)); 
}

/* --- STREAMLIT SELECT BOXES --- */
.stSelectbox > div > div { 
    background-color: rgba(255, 255, 255, 0.98) !important; 
    border: 1px solid var(--border-color) !important; 
    border-radius: 12px !important; 
    padding: 0.75rem 1rem !important; 
    min-height: 56px !important; 
    display: flex; 
    align-items: center; 
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease; 
}

.stSelectbox > div > div:hover { 
    border-color: var(--accent-orange) !important; 
    box-shadow: var(--shadow-md);
    transform: translateY(-2px); 
}

.stSelectbox [data-baseweb="select"] { 
    background-color: transparent !important; 
    color: var(--text-primary) !important; 
    line-height: 1.5 !important; 
    min-height: 50px !important; 
}

.stSelectbox [data-baseweb="select"] *, 
.stSelectbox [data-baseweb="select"] div, 
.stSelectbox [data-baseweb="select"] span, 
.stSelectbox [data-baseweb="select"] input { 
    color: var(--text-primary) !important; 
    background-color: transparent !important; 
    font-size: 1rem !important; 
    font-weight: 500 !important; 
}

.stSelectbox [data-baseweb="select"] svg { 
    fill: var(--accent-orange) !important; 
}

[data-baseweb="popover"] { 
    background-color: var(--bg-light) !important; 
}

ul[role="listbox"] { 
    background-color: var(--bg-light) !important; 
    border: 1px solid var(--border-color) !important; 
    border-radius: 12px !important; 
    max-height: 280px !important; 
    overflow-y: auto !important; 
    box-shadow: var(--shadow-lg);
}

li[role="option"] { 
    color: var(--text-primary) !important; 
    background-color: var(--bg-light) !important; 
    padding: 12px 16px !important; 
    font-size: 1rem !important; 
    line-height: 1.5 !important; 
    transition: all 0.2s ease; 
}

li[role="option"]:hover { 
    background-color: rgba(255, 107, 53, 0.08) !important; 
    color: var(--accent-orange) !important; 
    transform: translateX(4px); 
}

li[role="option"][aria-selected="true"] { 
    background-color: rgba(255, 107, 53, 0.12) !important; 
    color: var(--accent-orange) !important; 
    font-weight: 600 !important; 
}

/* --- STREAMLIT TEXT AREAS & INPUTS --- */
.stTextArea textarea, 
.stTextInput input { 
    background: rgba(255, 255, 255, 0.98) !important; 
    border: 1px solid var(--border-color) !important; 
    border-radius: 12px !important; 
    color: var(--text-primary) !important; 
    font-size: 1rem !important; 
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease; 
    padding: 0.875rem !important; 
}

.stTextArea textarea:focus, 
.stTextInput input:focus { 
    border-color: var(--accent-orange) !important; 
    box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    outline: none !important;
}

/* --- STREAMLIT BUTTONS --- */
.stButton > button { 
    background: linear-gradient(135deg, var(--accent-orange), var(--accent-coral)); 
    color: #ffffff !important; 
    border: none; 
    border-radius: 12px; 
    padding: 0.875rem 2rem; 
    font-weight: 600; 
    font-size: 1rem; 
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer; 
}

.stButton > button:hover { 
    transform: translateY(-3px); 
    box-shadow: var(--shadow-lg);
}

.stButton > button:active { 
    transform: translateY(-1px); 
}

/* --- EXPANDER --- */
.streamlit-expanderHeader { 
    background: rgba(255, 255, 255, 0.12) !important; 
    border-radius: 12px !important; 
    color: var(--text-light) !important; 
    font-weight: 600 !important; 
    padding: 1rem !important; 
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover { 
    background: rgba(255, 255, 255, 0.18) !important; 
}

.streamlit-expanderContent { 
    background: rgba(255, 255, 255, 0.08) !important; 
    border-radius: 12px !important; 
    padding: 1.5rem !important; 
    margin-top: 0.5rem;
}

/* --- PROGRESS BAR --- */
.stProgress > div > div { 
    background: linear-gradient(90deg, var(--accent-orange), var(--accent-coral)) !important; 
    border-radius: 10px; 
    height: 8px !important;
}

/* --- SCROLLBAR STYLING --- */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--accent-orange);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-coral);
}
</style>
""", unsafe_allow_html=True)

# Small CSS tweak for heading icons so emoji/icons keep a distinct accent color
st.markdown("""
<style>
    .heading-icon { color: var(--accent-orange) !important; margin-right: 0.5rem; font-size: 1.05em; vertical-align: middle; }
    .info-card .heading-icon { margin-right: 0.6rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Config - Data & Auth
# -----------------------------
TENANT_ID = "talos"
AUTH_TOKEN = None
HEADERS_BASE = {"Content-Type": "application/json"}

# EXPANDED ACCOUNTS with Industry Mapping
ACCOUNT_INDUSTRY_MAP = {
    "Select Account": "Select Industry",
    # Pharmaceutical
    "Abbvie": "Pharma",
    "BMS": "Pharma",
    "Pfizer": "Pharma",
    "Johnson & Johnson": "Pharma",
    "Novartis": "Pharma",
    "Merck": "Pharma",
    "Roche": "Pharma",
    # Technology
    "Microsoft": "Technology",
    "DELL": "Technology",
    "IBM": "Technology",
    "Oracle": "Technology",
    "SAP": "Technology",
    "Salesforce": "Technology",
    "Adobe": "Technology",
    # Retail
    "Walmart": "Retail",
    "Target": "Retail",
    "Costco": "Retail",
    "Kroger": "Retail",
    "Coles": "Retail",
    "Tesco": "Retail",
    "Carrefour": "Retail",
    # Airlines
    "Southwest Airlines": "Airlines",
    "Delta Airlines": "Airlines",
    "United Airlines": "Airlines",
    "American Airlines": "Airlines",
    "Emirates": "Airlines",
    "Lufthansa": "Airlines",
    # Consumer Goods
    "Nike": "Consumer Goods",
    "Adidas": "Consumer Goods",
    "Unilever": "Consumer Goods",
    "Procter & Gamble": "Consumer Goods",
    "Coca-Cola": "Consumer Goods",
    "PepsiCo": "Consumer Goods",
    # Energy
    "Chevron": "Energy",
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
    "Skill Development": "Education",
    "Coursera": "Education",
    "Udemy": "Education",
    "Khan Academy": "Education",
    # Other
    "BLR Airport": "Other",
    "THD": "Other",
    "Tmobile": "Other",
    "Mu Labs": "Other",
}

ACCOUNTS = sorted(list(ACCOUNT_INDUSTRY_MAP.keys()))
INDUSTRIES = sorted(list(set(ACCOUNT_INDUSTRY_MAP.values())))

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
            "Overall Difficulty Score\n"
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
    # Be flexible about spacing and headers that follow (Summary, Key Takeaways, Individual Question Scores, Dimension Averages, Overall Difficulty Score, Hardness Level)
    patterns = [
        r"SME Justification[:\s]*((?:.|\n)*?)(?=\n\s*(?:Summary|Key Takeaways|Key Takeaway|Individual Question Scores|Dimension Averages|Overall Difficulty Score|Hardness Level|$))",
        r"Justification[:\s]*((?:.|\n)*?)(?=\n\s*(?:Summary|Key Takeaways|Key Takeaway|Individual Question Scores|Dimension Averages|Overall Difficulty Score|Hardness Level|$))",
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
        r'Overall Difficulty Score.*?(?=\n\nHardness|\n\nSME|\Z)',
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
    """Format vocabulary with proper bold styling for terms and definitions - COMPACT VERSION"""
    if not text:
        return "No vocabulary data available"
    
    clean_text = sanitize_text(text)
    
    # Split into items and format each one compactly
    items = re.split(r'\n\s*(?=\d+\.)', clean_text)
    formatted_items = []
    
    for item in items:
        if not item.strip():
            continue
            
        # Format the term in bold orange
        item = re.sub(r'^(\d+\.\s*[^•\n:]+)(?=•|$)', r'<strong>\1</strong>', item)
        
        # Format definition and implication labels in bold
        item = re.sub(r'(•\s*)Definition:\s*', r'<br><strong>• Definition:</strong> ', item)
        item = re.sub(r'(•\s*)Implication:\s*', r'<br><strong>• Implication:</strong> ', item)
        
        # Remove extra spacing
        item = re.sub(r'\s+', ' ', item)
        formatted_items.append(item.strip())
    
    # Join with minimal spacing
    result = '<br>'.join(formatted_items)
    
    # Ensure proper compact spacing
    result = re.sub(r'<br><br>', '<br>', result)
    
    return result

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
        "hardness_summary_text": ""
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()


def reset_app_state():
    """Reset session state to defaults for a new analysis."""
    keys_to_keep = [
        # Keep UI defaults but reset user inputs/outputs
        'current_page', 'account', 'industry'
    ]
    preserved = {k: st.session_state.get(k) for k in keys_to_keep}
    st.session_state.clear()
    init_session_state()
    for k, v in preserved.items():
        st.session_state[k] = v
    st.success("🔄 Application state reset. You can start a new analysis.")
    # Use a safe rerun that works across Streamlit versions
    safe_rerun()


def safe_rerun():
    """Attempt to rerun the Streamlit app in a way compatible across versions.

    Strategy:
    - If st.experimental_rerun exists, call it.
    - Otherwise, try to raise Streamlit's internal RerunException from a few known locations.
    - Final fallback: call st.stop() to end the current run (user interaction will trigger a rerun).
    """
    try:
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
            return
    except Exception:
        pass

    # Try to import and raise common RerunException locations
    possible_exc_paths = [
        ('streamlit.runtime.scriptrunner', 'RerunException'),
        ('streamlit.script_runner', 'RerunException'),
        ('streamlit.scriptrunner', 'RerunException'),
    ]
    for module_path, exc_name in possible_exc_paths:
        try:
            mod = __import__(module_path, fromlist=[exc_name])
            exc = getattr(mod, exc_name, None)
            if exc:
                raise exc()
        except Exception:
            # ignore and try next
            continue

    # Last-resort fallback
    try:
        st.stop()
    except Exception:
        # If even st.stop fails, just return
        return

# -----------------------------
# PAGE 1: Business Problem Input & Analysis
# -----------------------------
if st.session_state.current_page == "page1":
    st.markdown('<div class="page-title"><h1>🧠 Business Problem Level Classifier</h1></div>', unsafe_allow_html=True)
    
    # Account & Industry Selection
    st.markdown('<div class="section-title-box"><h3>🏢 Account & Industry Selection</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            current_account_index = ACCOUNTS.index(st.session_state.account)
        except:
            current_account_index = 0
        
        selected_account = st.selectbox(
            "Select Account:",
            options=ACCOUNTS,
            index=current_account_index,
            key="account_selector_all"
        )
        
        if selected_account != st.session_state.account:
            st.session_state.account = selected_account
            if selected_account in ACCOUNT_INDUSTRY_MAP:
                st.session_state.industry = ACCOUNT_INDUSTRY_MAP[selected_account]
                st.success(f"✅ Industry auto-mapped to: {st.session_state.industry}")
            st.rerun()
    
    with col2:
        try:
            current_industry_index = INDUSTRIES.index(st.session_state.industry)
        except:
            current_industry_index = 0
        
        if st.session_state.account == "Select Account":
            selected_industry = st.selectbox(
                "Select Industry:",
                options=INDUSTRIES,
                index=current_industry_index,
                key="industry_selector"
            )
            if selected_industry != st.session_state.industry:
                st.session_state.industry = selected_industry
        else:
            st.selectbox(
                "Industry (Auto-mapped):",
                options=INDUSTRIES,
                index=current_industry_index,
                disabled=True,
                key="industry_disabled"
            )
    
    # Business Problem Description
    st.markdown('<div class="section-title-box"><h3>📝 Business Problem Description</h3></div>', unsafe_allow_html=True)
    st.session_state.problem_text = st.text_area(
        "Describe your business problem in detail:",
        value=st.session_state.problem_text,
        height=200,
        placeholder="Enter a detailed description of your business challenge...",
        label_visibility="collapsed"
    )
    
    # Analysis Button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        analyze_btn = st.button(
            "🚀 Analyze Problem",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.problem_text.strip() and 
                         st.session_state.industry != "Select Industry" and 
                         st.session_state.account != "Select Account")
        )
        # Reset button next to analyze
        if st.button("🔁 Reset", use_container_width=False, type="secondary"):
            reset_app_state()
    
    with col2:
        # Vocabulary Button - toggle functionality
        if st.session_state.analysis_complete:
            if 'show_vocabulary' not in st.session_state:
                st.session_state.show_vocabulary = False
            
            if st.button("📚 View Vocabulary", use_container_width=True, type="secondary"):
                st.session_state.show_vocabulary = not st.session_state.show_vocabulary
                st.rerun()
    
    # Display vocabulary when toggled - COMPACT VERSION
    if st.session_state.analysis_complete and st.session_state.get('show_vocabulary', False):
        vocab_text = st.session_state.outputs.get('vocabulary', 'No vocabulary data available')
        formatted_vocab = format_vocabulary_with_bold(vocab_text)
        
        st.markdown(f'''
        <div class="vocab-display">
            <h4 style="color: var(--musigma-orange) !important; margin-bottom: 1rem; text-align: center;">Extracted Vocabulary</h4>
            {formatted_vocab}
        </div>
        ''', unsafe_allow_html=True)
    
    if analyze_btn:
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
        
        with st.spinner("🔍 Analyzing your business problem..."):
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
                "🔄 Analyzing system inputs and outputs...",
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
            status_text.success("✅ Analysis complete! All steps finished.")
            
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
                <div style="font-size: 1.2rem; font-weight: 600; opacity: 0.95; margin-bottom: 0.5rem;">Overall Difficulty Score</div>
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
                    <div class="dimension-label">{dimension_icons[i]} {dimension}</div>
                    <div class="dimension-score">{score:.2f}/5</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # SME Justification Section - FULL CONTENT in orange-bordered box
        st.markdown('<div class="section-title-box"><h3>SME Justification</h3></div>', unsafe_allow_html=True)

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
        if st.button("🔍 View In Detail Analysis →", key="in_detail_main", use_container_width=True, type="primary"):
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
    dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
    dimension_icons = ["⚡", "❓", "🔗", "🎲"]

    for i, dimension in enumerate(dimensions):
        with col1 if i < 2 else col2:
            score = st.session_state.dimension_scores.get(dimension, 0.0)
            st.markdown(f'''
            <div class="dimension-box">
                <div class="dimension-label">{dimension_icons[i]} {dimension}</div>
                <div class="dimension-score">{score:.2f}/5</div>
            </div>
            ''', unsafe_allow_html=True)

            if st.button(f"View {dimension} Details →", key=f"dim_{dimension}", use_container_width=True):
                st.session_state.current_page = f"dimension_{dimension.lower()}"
                st.rerun()

    # Navigation
    st.markdown("---")
    if st.button("📊 View Hardness Summary →", use_container_width=True, type="primary"):
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
    
    # Back button
    if st.button("← Back to System Overview", use_container_width=False):
        st.session_state.current_page = "page2"
        st.rerun()
    
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
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    if dimension_name == "Volatility":
        with col3:
            if st.button("Next → Ambiguity", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_ambiguity"
                st.rerun()
    elif dimension_name == "Ambiguity":
        with col3:
            if st.button("Next → Interconnectedness", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_interconnectedness"
                st.rerun()
    elif dimension_name == "Interconnectedness":
        with col3:
            if st.button("Next → Uncertainty", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_uncertainty"
                st.rerun()
    elif dimension_name == "Uncertainty":
        with col3:
            if st.button("View Hardness Summary →", use_container_width=True, type="primary"):
                st.session_state.current_page = "hardness_summary"
                st.rerun()

# -----------------------------
# HARDNESS SUMMARY PAGE
# -----------------------------
elif st.session_state.current_page == "hardness_summary":
    st.markdown('''
    <div class="page-title">
        <h1>📊 Hardness Summary Analysis</h1>
    </div>
    ''', unsafe_allow_html=True)
    
    # Business Problem
    st.markdown('''
    <div class="section-title-box">
        <h3>📋 Business Problem</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="problem-display">
        <p>{st.session_state.problem_text}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Uncertainty Analysis", use_container_width=False):
        st.session_state.current_page = "dimension_uncertainty"
        st.rerun()
    
    # Display Scores Summary
    st.markdown('''
    <div class="section-title-box">
        <h3>📈 Score Breakdown</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Question Scores
    if st.session_state.question_scores:
        st.markdown('''
        <div class="section-title-box">
            <h4>Individual Question Scores</h4>
        </div>
        ''', unsafe_allow_html=True)
        
        scores_html = '<div class="info-card"><div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">'
        for q, score in sorted(st.session_state.question_scores.items(), key=lambda x: int(x[0][1:])):
            scores_html += f'<div style="padding: 0.75rem; background: rgba(255, 107, 53, 0.05); border-radius: 8px; text-align: center;"><strong>{q}:</strong><br><span style="font-size: 1.2rem; font-weight: 700; color: var(--accent-orange);">{score:.2f}/5</span></div>'
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
        dimensions_html += f'<div style="padding: 1rem; margin-bottom: 0.75rem; background: rgba(255, 107, 53, 0.05); border-radius: 8px; border-left: 3px solid var(--accent-orange);"><strong style="color: var(--accent-orange); font-size: 1.1rem;">{dimension}</strong><br><span style="color: var(--text-secondary); font-size: 0.9rem;">({q_list})</span><br><span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-orange);">{score:.2f}/5</span></div>'
    dimensions_html += '</div>'
    st.markdown(dimensions_html, unsafe_allow_html=True)
    
    # Overall Score and Level
    st.markdown('''
    <div class="section-title-box">
        <h3>🎯 Overall Classification</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        <div class="score-badge" style="margin-bottom: 1rem;">
            <div style="font-size: 1rem; font-weight: 500; opacity: 0.9; margin-bottom: 0.5rem;">Overall Difficulty Score</div>
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
    
    # Comprehensive Analysis (Everything EXCEPT scores and SME Justification)
    st.markdown('''
    <div class="section-title-box">
        <h3>📝 Comprehensive Analysis</h3>
    </div>
    ''', unsafe_allow_html=True)

    if st.session_state.hardness_summary_text:
        hs_text = st.session_state.hardness_summary_text

        # Extract the filtered comprehensive analysis (everything except score calculations and SME justification)
        comprehensive_analysis = extract_comprehensive_analysis(hs_text)

        # If there's any content left after filtering, display it exactly as-is. This will include Summary/Key Takeaways
        # if the API returned them (we don't strip them out here).
        if comprehensive_analysis and comprehensive_analysis.strip():
            st.markdown(f'<div class="info-card">{comprehensive_analysis}</div>', unsafe_allow_html=True)
        else:
            # If nothing remains after removing calculations and SME Justification, show SME Justification as fallback
            sme = st.session_state.get('summary') or extract_full_sme_justification(hs_text)
            if sme:
                st.markdown(f'<div class="info-card">{sme}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-card">No comprehensive analysis or SME justification available.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-card">No hardness summary data available.</div>', unsafe_allow_html=True)

    # Back to start button (always visible on the hardness_summary page)
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🏠 Back to Main Analysis", use_container_width=True, type="primary"):
            st.session_state.current_page = "page1"
            st.rerun()
    with col2:
        # Build a plain text report and provide a download button
        report_lines = []
        report_lines.append("Business Problem:\n")
        report_lines.append(st.session_state.problem_text or "(no problem provided)")
        report_lines.append("\n\nContext:\n")
        report_lines.append(f"Industry: {st.session_state.get('industry','')}")
        report_lines.append(f"\nAccount: {st.session_state.get('account','')}")
        report_lines.append("\n\nCurrent System:\n")
        report_lines.append(st.session_state.get('current_system_full','') or "No current system details")
        report_lines.append("\n\nInputs:\n")
        report_lines.append(st.session_state.get('input_text','') or "No inputs available")
        report_lines.append("\n\nOutputs:\n")
        report_lines.append(st.session_state.get('output_text','') or "No outputs available")
        report_lines.append("\n\nPain Points:\n")
        report_lines.append(st.session_state.get('pain_points_text','') or "No pain points identified")
        report_lines.append("\n\nHardness Summary (raw):\n")
        report_lines.append(st.session_state.get('hardness_summary_text','') or "No hardness summary available")

        report_content = "\n".join(report_lines)
        try:
            st.download_button(label="⬇️ Download Report (TXT)", data=report_content, file_name="hardness_report.txt", mime="text/plain")
        except Exception:
            st.markdown("<div class='info-card'>Unable to create download at this time.</div>", unsafe_allow_html=True)

# Mu-Sigma Logo - Base64 Version (Guaranteed to Work)
st.markdown("""
<style>
/* Mu-Sigma Logo Styles */
.musigma-logo {
    position: fixed;
    top: 14px;
    right: 14px;
    width: 80px;
    height: 80px;
    border-radius: 10px;
    border: 2px solid rgba(255,255,255,0.9);
    box-shadow: 0 8px 28px rgba(0,0,0,0.18);
    z-index: 999999;
    background: white !important;
    opacity: 0.99;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.musigma-logo:hover { 
    transform: translateY(-4px) scale(1.02); 
    box-shadow: 0 12px 36px rgba(0,0,0,0.22);
}

@media (max-width: 640px) { 
    .musigma-logo { 
        display: none !important; 
    } 
}

.musigma-logo img {
    width: 100% !important;
    height: 100% !important;
    object-fit: contain !important;
    display: block !important;
    background: white !important;
    padding: 8px !important;
    border-radius: 6px !important;
}

.musigma-logo-link {
    text-decoration: none !important;
    display: inline-block !important;
}

/* Ensure logo stays on top */
[data-testid="stAppViewContainer"] .musigma-logo {
    z-index: 999999 !important;
}
</style>
""", unsafe_allow_html=True)

# Mu-Sigma Logo with working URL
st.markdown(f'''
<a href="#" class="musigma-logo-link">
    <div class="musigma-logo">
        <img src="https://yt3.googleusercontent.com/ytc/AIdro_k-7HkbByPWjKpVPO3LCF8XYlKuQuwROO0vf3zo1cqgoaE=s900-c-k-c0x00ffffff-no-rj" alt="Mu-Sigma Logo">
    </div>
</a>
''', unsafe_allow_html=True)

# Alternative: If URLs don't work, use this SVG version instead
st.markdown("""
<script>
// Check if logo loaded properly after 2 seconds
setTimeout(function() {
    const logo = document.querySelector('.musigma-logo img');
    if (logo && (logo.naturalWidth === 0 || logo.complete === false)) {
        // Replace with SVG fallback
        const logoContainer = document.querySelector('.musigma-logo');
        if (logoContainer) {
            logoContainer.innerHTML = `
                <div class="musigma-text-fallback">
                    μσ
                </div>
            `;
        }
    }
}, 2000);
</script>
""", unsafe_allow_html=True)
# Inject JS/CSS: hide logo when user scrolls down, animate on load, and show a temporary "Wow amazing!" bubble on clicks
st.markdown('''
<style>
@keyframes logoPop { 0% { transform: translateY(-12px) scale(0.6); opacity:0 } 60% { transform: translateY(4px) scale(1.05); opacity:1 } 100% { transform: translateY(0) scale(1); opacity:1 } }
@keyframes wowFloat { 0% { opacity: 1; transform: translateY(0) scale(1); } 100% { opacity: 0; transform: translateY(-24px) scale(1.06); } }
.wow-bubble { position: fixed; pointer-events: none; background: #8b1e1e; color: #fff; padding: 8px 12px; border-radius: 20px; font-weight:700; font-family: Inter, sans-serif; box-shadow: 0 8px 20px rgba(0,0,0,0.18); z-index: 99999; animation: wowFloat 1.1s ease forwards; transform-origin: center; }
</style>
<script>
(function(){
    try{
        const logo = document.querySelector('.musigma-logo');
        if(logo){
            // initial pop animation
            logo.style.animation = 'logoPop 0.6s ease forwards';
            logo.style.transition = 'opacity 0.18s ease, transform 0.18s ease';
            // ensure visible when at top
            if(window.scrollY > 50){ logo.style.opacity = '0'; logo.style.pointerEvents='none'; }
            window.addEventListener('scroll', function(){
                if(window.scrollY > 50){ logo.style.opacity = '0'; logo.style.pointerEvents='none'; logo.style.transform='translateY(-10px) scale(0.98)'; }
                else { logo.style.opacity = '1'; logo.style.pointerEvents='auto'; logo.style.transform='translateY(0) scale(1)'; }
            }, {passive:true});
        }

        // Click-triggered bubble
        document.addEventListener('click', function(e){
            try{
                const bubble = document.createElement('div');
                bubble.className = 'wow-bubble';
                bubble.textContent = 'Wow amazing!';
                document.body.appendChild(bubble);
                // position with some offset so it doesn't sit directly under cursor
                const x = Math.max(8, Math.min(window.innerWidth - 120, e.clientX - 50));
                const y = Math.max(8, Math.min(window.innerHeight - 40, e.clientY - 30));
                bubble.style.left = x + 'px';
                bubble.style.top = y + 'px';
                setTimeout(function(){ if(bubble && bubble.parentNode){ bubble.parentNode.removeChild(bubble); } }, 1200);
            } catch(err){ console.error(err); }
        }, false);
    } catch(e){ console.error(e); }
})();
</script>
''', unsafe_allow_html=True)





