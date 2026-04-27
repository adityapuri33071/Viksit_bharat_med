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
            start_marker = "-----BEGIN PRIVATE KEY-----"
            if start_marker in p_key:
                p_key = p_key[p_key.find(start_marker):]
            p_key = p_key.replace("\\n", "\n")
            key_dict["private_key"] = p_key
        
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        st.stop()

db = firestore.client()

# --- PREMIUM PROFESSIONAL UI (Green & Light Blue) ---
st.markdown("""
    <style>
    /* Background and Global Font */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }
    
    /* Header Styling */
    .main-title {
        color: #1e40af;
        font-size: 50px !important;
        font-weight: 850 !important;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Medicine Card Styling */
    .med-card {
        background-color: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border-left: 10px solid #10b981;
        margin-bottom: 25px;
        transition: transform 0.3s ease;
    }
    .med-card:hover {
        transform: translateY(-5px);
    }

    /* Status Badges */
    .status-pending { color: #f59e0b; font-weight: bold; }
    .status-taken { color: #10b981; font-weight: bold; }
    .status-missed { color: #ef4444; font-weight: bold; }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 50px !important;
        transition: all 0.3s ease !important;
    }
    
    /* Taken Button (Green) */
    div[data-testid="column"]:nth-of-type(1) .stButton > button {
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Not Taken Button (Light Blue/Red Outline) */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background-color: #f8fafc !important;
        color: #ef4444 !important;
        border: 2px solid #ef4444 !important;
    }
    
    div[data-testid="column"]:nth-of-type(1) .stButton > button:hover {
        background-color: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4) !important;
    }

    div[data-testid="column"]:nth-of-type(2) .stButton > button:hover {
        background-color: #fee2e2 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">💊 Meri Dawai</h1>', unsafe_allow_html=True)

# Data Fetching
docs = db.collection("medications").stream()
meds_found = False

for doc in docs:
    meds_found = True
    med = doc.to_dict()
    
    # Custom Container for Card Look
    with st.container():
        st.markdown(f"""
            <div class="med-card">
                <h2 style="margin:0; color:#1e3a8a;">💊 {med['name']}</h2>
                <p style="font-size:18px; margin:5px 0;">⏰ Samay: <b>{med['time']}</b></p>
                <p style="font-size:18px;">Status: <span class="status-{med['status'].split()[0].lower()}">{med['status']}</span></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons
        if med['status'] == "Pending":
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Dawai Le Li ✅", key=f"yes_{doc.id}"):
                    db.collection("medications").document(doc.id).update({"status": "Taken ✅"})
                    st.toast(f"Shabaash! {med['name']} le li.")
                    st.rerun()
            
            with col2:
                if st.button("Nahi Li ❌", key=f"no_{doc.id}"):
                    db.collection("medications").document(doc.id).update({"status": "Missed ❌"})
                    st.toast(f"Dhyan rakhein! {med['name']} chhoot gayi.")
                    st.rerun()
        st.write("") # Padding between cards

if not meds_found:
    st.info("Abhi koi dawai schedule nahi hai. Relax karein!")
                    
