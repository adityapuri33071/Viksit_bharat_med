import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import pandas as pd

# --- FIREBASE SETUP (Bulletproof Version) ---
if not firebase_admin._apps:
    try:
        # 1. Secret fetch karna
        raw_json = st.secrets["textkey"]
        key_dict = json.loads(raw_json)
        
        # 2. PRIVATE KEY CLEANING (Sabse Zaroori Step)
        if "private_key" in key_dict:
            p_key = key_dict["private_key"]
            # Aage-piche ke faltu spaces ya dots hatana
            p_key = p_key.strip() 
            # Double backslashes ko asli newline mein badalna
            p_key = p_key.replace("\\n", "\n")
            key_dict["private_key"] = p_key
            
        # 3. Initialize
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
        
    except Exception as e:
        st.error(f"❌ Firebase Setup Fail: {e}")
        st.info("Check karo: Kya Secrets mein 'private_key' ke shuruat mein koi dot (.) ya space toh nahi reh gaya?")
        st.stop() # Error aane par app ko yahin rok do

db = firestore.client()
        

db = firestore.client()

# --- PREMIUM CAREGIVER CSS ---
st.markdown("""
    <style>
    /* Main Layout */
    .main { background-color: #F0F2F6; }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] { font-size: 35px !important; font-weight: bold; color: #1E3A8A; }
    
    /* Card Styling */
    .med-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #1E3A8A;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    
    /* Header Section */
    .header-style {
        font-size: 45px !important;
        font-weight: 800;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="header-style">👨‍⚕️ Caregiver Control Panel</p>', unsafe_allow_html=True)

# --- DATA PROCESSING & AI INSIGHTS ---
docs = db.collection("medications").stream()
meds_data = [{"id": doc.id, **doc.to_dict()} for doc in docs]

# Adherence Score Logic (AI Insight)
if meds_data:
    total = len(meds_data)
    taken = len([m for m in meds_data if "Taken" in m['status']])
    score = (taken / total) * 100
else:
    score = 0

# --- DASHBOARD TOP SECTION (METRICS) ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Meds", len(meds_data))
col2.metric("Adherence Score", f"{score:.1f}%")
col3.metric("Status", "Stable" if score > 70 else "At Risk")

st.divider()

# --- TABS FOR ORGANIZATION ---
tab1, tab2 = st.tabs(["📊 Live Monitoring", "➕ Add New Schedule"])

with tab1:
    st.subheader("Patient's Real-time Status")
    if not meds_data:
        st.info("No medications added yet.")
    else:
        for med in meds_data:
            # Custom Card Layout
            with st.container():
                c1, c2, c3 = st.columns([3, 2, 1])
                status_emoji = "✅" if "Taken" in med['status'] else "🔴" if "Missed" in med['status'] else "⏳"
                
                c1.markdown(f"**Medicine:** {med['name']}")
                c2.markdown(f"**Time:** {med['time']} | {status_emoji} {med['status']}")
                
                if c3.button("Delete", key=f"del_{med['id']}"):
                    db.collection("medications").document(med['id']).delete()
                    st.toast(f"Removed {med['name']}")
                    st.rerun()
                st.markdown("---")

with tab2:
    st.subheader("Schedule New Medication")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Medicine Name (e.g., Aspirin 75mg)")
        time = st.text_input("Time (e.g., 09:00 AM)")
        
        submit = st.form_submit_button("Publish to Patient App")
        if submit:
            if name and time:
                db.collection("medications").add({
                    "name": name, 
                    "time": time, 
                    "status": "Pending"
                })
                st.success(f"Successfully added {name}!")
                st.rerun()
            else:
                st.error("Please fill all fields.")
