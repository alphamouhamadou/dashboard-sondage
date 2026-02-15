import streamlit as st

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

def login():
    st.title("🔐 Accès Privé - Résultats Sondage")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if (
            username == st.secrets["USERNAME"]
            and password == st.secrets["PASSWORD"]
        ):
            st.session_state["authenticated"] = True
            st.success("Connexion réussie ✅")
            st.rerun()
        else:
            st.error("Identifiants incorrects ❌")

def require_authentication():
    check_authentication()
    if not st.session_state["authenticated"]:
        login()
        st.stop()

def logout():
    if st.sidebar.button("🚪 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.rerun()
