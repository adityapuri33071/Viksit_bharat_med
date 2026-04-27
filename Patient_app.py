import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- FIREBASE SETUP (CODE SAME RAKHA HAI) ---
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- PREMIUM ELDERLY-FRIENDLY CSS ---
st.markdown("""
    <style>
    /* Main Background aur Font */
    .main {
        background-color: #F8F9FA;
    }
    
    /* Sabhi text ko bada aur bold banaya */
    html, body, [class*="st-"] {
        font-size: 22px !important; 
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }

    /* Titles ko aur zyada prominent kiya */
    h1 {
        color: #1E3A8A !important; /* Dark Blue - Trustworthy color */
        font-size: 50px !important;
        font-weight: 800 !important;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Medicine Card/Container styling */
    [data-testid="stVerticalBlock"] > div > div > div[data-testid="element-container"] {
        background-color: white;
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }

    /* Subheaders (Medicine Name) */
    h3 {
        font-size: 32px !important;
        color: #111827 !important;
        margin-bottom: 0px !important;
    }

    /* Buttons ko bada aur touch-friendly banaya */
    .stButton > button {
        width: 100%;
        height: 70px !important;
        background-color: #059669 !important; /* Premium Green */
        color: white !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stButton > button:hover {
        background-color: #047857 !important;
        transform: scale(1.02);
    }

    /* Status Text */
    .stMarkdown p {
        font-size: 24px !important;
        color: #4B5563;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP INTERFACE (CODE SAME RAKHA HAI) ---
st.title("📱 My Medicine") # Short & simple title

# Data Fetching
docs = db.collection("medications").stream()
for doc in docs:
    med = doc.to_dict()
    with st.container(border=True):
        st.subheader(f"💊 {med['name']}")
        st.write(f"⏰ Time: **{med['time']}**")
        st.write(f"Status: **{med['status']}**")
        
        if med['status'] == "Pending":
            if st.button(f"Mark as Taken", key=doc.id):
                db.collection("medications").document(doc.id).update({"status": "Taken ✅"})
                st.rerun()
        
