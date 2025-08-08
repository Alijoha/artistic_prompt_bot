# auth.py
import streamlit as st
from supabase import create_client, Client

# Read Supabase creds from Streamlit secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

sb = get_supabase()

# ---- Session helpers ---------------------------------------------------------

def _set_user(user):
    st.session_state["user"] = user

def get_user():
    return st.session_state.get("user")

def sign_out():
    try:
        sb.auth.sign_out()
    finally:
        _set_user(None)

# ---- UI widgets --------------------------------------------------------------

def auth_ui():
    """Renders Sign In / Sign Up UI and updates st.session_state['user'] on success."""
    st.markdown("## 🔐 Sign in or create an account")

    if "user" not in st.session_state:
        st.session_state["user"] = None

    # NEW: nonce so form keys are always unique (prevents duplicate-key crash)
    nonce = st.session_state.get("auth_nonce", 0)
    st.session_state["auth_nonce"] = nonce + 1

    tab_login, tab_signup = st.tabs(["Sign in", "Create account"])

    with tab_login:
        # 🔑 make the form + inputs unique per render
        with st.form(f"login_form_{nonce}", clear_on_submit=False):
            email = st.text_input("Email", key=f"li_email_{nonce}", autocomplete="email")
            password = st.text_input("Password", key=f"li_pw_{nonce}", type="password")
            submitted = st.form_submit_button("Sign in")
        if submitted:
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                try:
                    res = sb.auth.sign_in_with_password({"email": email, "password": password})
                    _set_user(res.user)
                    st.success(f"Welcome back, {res.user.email}!")
                except Exception as e:
                    st.error(f"Sign-in failed: {e}")

    with tab_signup:
        # 🔑 make the form + inputs unique per render
        with st.form(f"signup_form_{nonce}", clear_on_submit=False):
            email_su = st.text_input("Email ", key=f"su_email_{nonce}", autocomplete="email")
            password_su = st.text_input("Password ", key=f"su_pw_{nonce}", type="password")
            submitted_su = st.form_submit_button("Create account")
        if submitted_su:
            if not email_su or not password_su:
                st.error("Please enter email and password.")
            else:
                try:
                    res = sb.auth.sign_up({"email": email_su, "password": password_su})
                    # Depending on your project settings, a confirmation email may be required.
                    _set_user(res.user)
                    st.success("Account created! Check your email if confirmation is required.")
                except Exception as e:
                    st.error(f"Sign-up failed: {e}")

    if get_user():
        col1, col2 = st.columns([1,1])
        with col1:
            st.info(f"Signed in as **{get_user().email}**")
        with col2:
            if st.button("Sign out"):
                sign_out()
                st.toast("Signed out")

def require_user() -> bool:
    """Call at the top of protected pages; returns True if a user is signed in."""
    user = get_user()
    if user is None:
        st.warning("Please sign in to use this page.")
        auth_ui()
        return False
    return True