import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import pandas as pd

# --- SUPER-CLEAN FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        raw_json = st.secrets["textkey"]
        key_dict = json.loads(raw_json)
        if "private_key" in key_dict:
            p_key = key_dict["private_key"]
            start_marker = "-----BEGIN PRIVATE KEY-----"
            if start_marker in p_key:
                p_key = p_key[p_key.find(start_marker):]
            p_key = p_key.replace("\\n", "\n")
            key_dict["private_key"] = p_key
        
        # Ab yahan koi dusra 'try' nahi hona chahiye
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred) # Ye line ab ek hi 'try' ke andar hai

    except Exception as e: # Ye except ab upar wale 'try' (Line 9) se connect ho gaya
        st.error(f"❌ Connection Error: {e}")
        st.stop()

db = firestore.client()


# --- PREMIUM MEDICAL DASHBOARD CSS ---
st.markdown("""
    <style>
    /* Main Background & Fonts */
    [data-testid="stAppViewContainer"] { 
        background-color: #F2F7F9; /* Soft Medical Light Blue */
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    [data-testid="stHeader"] { background-color: transparent; }
    
    /* Premium Header Gradient */
    .header-style { 
        font-size: 42px; 
        font-weight: 900; 
        background: -webkit-linear-gradient(135deg, #004D7A, #008793, #00BF72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; 
        padding: 10px 0 20px 0;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }

    /* Floating Metric Cards */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #E8F0F2;
        text-align: center;
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #5C7285;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] { 
        color: #008793; 
        font-weight: 800; 
        font-size: 34px;
    }

    /* Stylish Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 12px; 
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px; 
        background-color: #FFFFFF; 
        border-radius: 8px; 
        padding: 10px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        border: 1px solid #E8F0F2;
        color: #5C7285;
        font-weight: 600;
        transition: all 0.3s ease-in-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #008793;
        border-color: #008793;
    }
    .stTabs [aria-selected="true"] {
        background-color: #008793 !important;
        color: #FFFFFF !important;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 135, 147, 0.3);
    }

    /* Modern Buttons (Del & Add) */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #008793;
        color: #008793;
        font-weight: 600;
        background-color: #FFFFFF;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #008793;
        color: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 135, 147, 0.2);
    }
    
    /* Clean Form Layout */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #E8F0F2;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #D1D5DB;
        padding: 10px 15px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #008793;
        box-shadow: 0 0 0 1px #008793;
    }
    
    /* Elegant Dividers */
    hr {
        border-color: #E8F0F2;
        margin: 1.5em 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="header-style">👨‍⚕️ Caregiver Command Center</p>', unsafe_allow_html=True)

# Data Processing
docs = db.collection("medications").stream()
meds_list = [{"id": doc.id, **doc.to_dict()} for doc in docs]

# AI Score Calculation
if meds_list:
    total = len(meds_list)
    taken = len([m for m in meds_list if "Taken" in m['status']])
    score = (taken / total) * 100
else:
    score = 0

# Metrics Section
c1, c2, c3 = st.columns(3)
c1.metric("Active Meds", len(meds_list))
c2.metric("Adherence Score", f"{score:.1f}%")
c3.metric("Patient Health", "Stable" if score > 75 else "Needs Check")

st.divider()

tab1, tab2 = st.tabs(["📊 Live Monitor", "➕ Set New Schedule"])

with tab1:
    if not meds_list:
        st.info("No medications added.")
    else:
        for med in meds_list:
            with st.container():
                col_a, col_b, col_c = st.columns([3,2,1])
                col_a.write(f"**{med['name']}**")
                col_b.write(f"🕒 {med['time']} | {med['status']}")
                if col_c.button("Del", key=f"del_{med['id']}"):
                    db.collection("medications").document(med['id']).delete()
                    st.rerun()
                st.markdown("---")

with tab2:
    with st.form("new_med"):
        m_name = st.text_input("Dawai ka Naam")
        m_time = st.text_input("Samay (e.g., 08:00 AM)")
        if st.form_submit_button("Add to Patient App"):
            if m_name and m_time:
                db.collection("medications").add({"name": m_name, "time": m_time, "status": "Pending"})
                st.success("Nayi dawai add kar di gayi hai!")
                st.rerun()
