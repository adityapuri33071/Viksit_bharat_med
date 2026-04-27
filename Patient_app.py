import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- SUPER-CLEAN FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        raw_json = st.secrets["textkey"]
        key_dict = json.loads(raw_json)
        if "private_key" in key_dict:
            p_key = key_dict["private_key"]
            # Dot aur kachra saaf karna
            start_marker = "-----BEGIN PRIVATE KEY-----"
            if start_marker in p_key:
                p_key = p_key[p_key.find(start_marker):]
            p_key = p_key.replace("\\n", "\n")
            key_dict["private_key"] = p_key
        #cred = credentials.Certificate(key_dict)
        # Purane code ki jagah ye replace karo
try:
    # Key dict se private key ke newlines (\n) ko sahi karne ke liye
    key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(key_dict)
except Exception as e:
    st.error(f"Credential Error: {e}")
           firebase_admin.initialize_app(cred)
except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

db = firestore.client()

# --- PREMIUM ELDERLY CSS ---
st.markdown("""
    <style>
    html, body, [class*="st-"] { font-size: 24px !important; font-weight: 600; }
    h1 { color: #1E3A8A !important; font-size: 55px !important; text-align: center; font-weight: 800; }
    h3 { font-size: 35px !important; color: #111827 !important; }
    .stButton > button {
        width: 100%; height: 80px !important;
        background-color: #059669 !important; color: white !important;
        font-size: 28px !important; border-radius: 20px !important;
        font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="element-container"] {
        background-color: white; border-radius: 25px; padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 Meri Dawai")

# Data Fetching
docs = db.collection("medications").stream()
meds_found = False

for doc in docs:
    meds_found = True
    med = doc.to_dict()
    with st.container(border=True):
        st.subheader(f"💊 {med['name']}")
        st.write(f"⏰ Time: **{med['time']}**")
        st.write(f"Status: **{med['status']}**")
        
        if med['status'] == "Pending":
            if st.button("Dawai Le Li ✅", key=doc.id):
                db.collection("medications").document(doc.id).update({"status": "Taken ✅"})
                st.toast("Shabaash! Dawai le li gayi hai.")
                st.rerun()

if not meds_found:
    st.info("Abhi koi dawai set nahi hai. Caregiver se check karein.")
    
