import streamlit as st

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False 

if "user_role" not in st.session_state:
    st.session_state.user_role = None    

def logout():
        st.session_state.user_role = None
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.username = None
        st.session_state.token_user = None
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.rerun()

role = st.session_state.user_role

logout_page = st.Page(
    logout, title="Cerrar sesión", icon=":material/logout:"
)

login_page = st.Page(
    "pages/login_page.py", title="Iniciar de sesión", icon=":material/login:"
)

chat_page = st.Page(
    "pages/chat_page.py", title="Deache Chat", icon=":material/chat:", default=True
)

admin_dashboard = st.Page(
    "pages/admin_page.py", title="Dashboard", icon=":material/dashboard:"
)

account_pages = [chat_page, logout_page]
admin_pages = [admin_dashboard, chat_page, logout_page ]


page_dict = {}

if st.session_state.user_role == "user":
    page_dict["user"] = account_pages

if st.session_state.user_role == "admin":
    page_dict["admin"] = admin_pages
    
if len(page_dict) > 0:
    pg = st.navigation(page_dict)
else:
    pg = st.navigation([login_page])

st.set_page_config(page_title="Deache Bot", page_icon="🤖", layout="centered")
st.logo("logo_ubiponi.png", icon_image="logo_ubiponi.png")
pg.run()