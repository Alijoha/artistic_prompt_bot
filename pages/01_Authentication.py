import streamlit as st
from auth import auth_ui
st.set_page_config(page_title="Authentication", page_icon="🔐", layout="centered")
auth_ui()