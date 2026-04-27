import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase Secrets Setup
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["textkey"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("👨‍⚕️ Caregiver Dashboard")

# Add Medication Form
with st.form("add_form"):
    name = st.text_input("Medicine Name")
    time = st.text_input("Time")
    if st.form_submit_button("Add Schedule"):
        db.collection("medications").add({"name": name, "time": time, "status": "Pending"})
        st.success("Added!")

# Monitor Status
st.divider()
docs = db.collection("medications").stream()
for doc in docs:
    med = doc.to_dict()
    st.write(f"**{med['name']}** - {med['status']}")
      
