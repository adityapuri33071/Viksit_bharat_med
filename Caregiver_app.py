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


# --- PREMIUM DASHBOARD CSS ---
st.markdown("""
    <style>
    .main { background-color: #F8F9FC; }
    .header-style { font-size: 40px; font-weight: 800; color: #1E3A8A; text-align: center; }
    [data-testid="stMetricValue"] { color: #1E3A8A; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #E2E8F0; border-radius: 10px; padding: 10px 20px;
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
