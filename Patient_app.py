import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase Secrets Setup (Streamlit Cloud ke liye)
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("📱 Patient Medicine Tracker")

# Data Fetching
docs = db.collection("medications").stream()
for doc in docs:
    med = doc.to_dict()
    with st.container(border=True):
        st.subheader(f"💊 {med['name']}")
        st.write(f"Time: {med['time']} | Status: {med['status']}")
        if med['status'] == "Pending":
            if st.button("Taken", key=doc.id):
                db.collection("medications").document(doc.id).update({"status": "Taken ✅"})
                st.rerun()
  
