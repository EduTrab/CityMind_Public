import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔐 CityMind Access 1.3")
    
    st.write("Please authenticate using your username formatted as name_surname_birthyear")
    

    st.write("Username format: name_surname_birthyear")
    username = st.text_input("Enter username:", placeholder="john_doe_1990")
    
    if username:
    # ✅ DEBUG PRINT
        st.session_state.username= username
        st.write(f"your username is {st.session_state.username}")
        print("Entered username:", username)
        
        st.session_state.authenticated = True
        st.rerun()
        






    if not st.session_state.authenticated:
        st.stop()
