import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 CityMind Access")
    pw = st.text_input("Enter password to continue:", type="password")

    # ✅ DEBUG PRINT
    print("Entered:", pw)
    print("Expected:", st.secrets.get("app_password"))

    if pw and pw == st.secrets.get("app_password", ""):
        st.session_state.authenticated = True
        st.rerun()
    elif pw:
        st.error("❌ Incorrect password. Please try again.")

    if not st.session_state.authenticated:
        st.stop()
