import streamlit as st
from supabase import Client, create_client
import secrets
@st.cache_resource
def init_connection() -> Client:
    try:
        return create_client(
            st.secrets["connections"]["supabase"]["SUPABASE_URL"],
            st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
        )
    except KeyError:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def login_success(message: str, username: str, token: str = None, user_role: str = None, user_id: str = None) -> None:
    st.success(message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["token_user"] = token
    st.session_state["user_role"] = user_role
    st.session_state["user_id"] = user_id
    st.rerun()

# Create the python function that will be called
def login_form(
    *,
    title: str = "Ingresar a Deache Bot",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    token_col: str = "token",
    role_col: str = "role",
    id_col: str = "id",
    create_title: str = "Crear nueva cuenta ",
    login_title: str = "Iniciar sesión ",
    allow_guest: bool = False,
    allow_create: bool = True,
    guest_title: str = "Ingresar como invitado(a) :ninja: ",
    create_username_label: str = "Crear un unico correo",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_password_label: str = "Crear una contraseña",
    create_password_placeholder: str = None,
    create_submit_label: str = "Crear cuenta",
    create_success_message: str = "Cuenta creada :tada:",
    login_username_label: str = "Ingresa tu correo",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Ingresa tu contraseña",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = "Ingresar",
    login_success_message: str = "Inicio de sesión con exito :tada:",
    login_error_message: str = "Contraseña y/o correo incorrecto :x: ",
) -> Client:

    # Initialize supabase connection
    client = init_connection()

    # User Authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None
        
    if "token_user" not in st.session_state:
        st.session_state["token_user"] = None

    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
        
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    with st.container():
        if allow_guest:
            if allow_create:
                create_tab, login_tab, guest_tab = st.tabs(
                    [
                        create_title,
                        login_title,
                        guest_title,
                    ]
                )
            else:
                login_tab, guest_tab = st.tabs([login_title, guest_title])
        elif allow_create:
            create_tab, login_tab = st.tabs(
                [
                    create_title,
                    login_title,
                ]
            )
        else:
            login_tab = st.container()

        # Create new account
        if allow_create:
            with create_tab:
                with st.form(key="create"):
                    username = st.text_input(
                        label=create_username_label,
                        placeholder=create_username_placeholder,
                        help=create_username_help,
                        disabled=st.session_state["authenticated"],
                    )

                    password = st.text_input(
                        label=create_password_label,
                        placeholder=create_password_placeholder,
                        type="password",
                        disabled=st.session_state["authenticated"],
                    )

                    if st.form_submit_button(
                        label=create_submit_label,
                        type="primary",
                        disabled=st.session_state["authenticated"],
                    ):
                        token = secrets.token_hex(30)
                        try:
                            client.table(user_tablename).insert(
                                {username_col: username, password_col: password, token_col: token, role_col: "user"},
                            ).execute()
                            
                            response = (
                                client.table(user_tablename)
                                .select(f"{username_col}, {password_col}, {token_col}, {role_col}, {id_col}",)
                                .eq(username_col, username)
                                .eq(password_col, password)
                                .execute()
                            )
                        except Exception as e:
                            st.error(e)
                            st.session_state["authenticated"] = False
                        else:
                            login_success(create_success_message, username, token, response.data[0][role_col], response.data[0][id_col])
        # Login to existing account
        with login_tab:
            with st.form(key="login"):
                username = st.text_input(
                    label=login_username_label,
                    placeholder=login_username_placeholder,
                    help=login_username_help,
                    disabled=st.session_state["authenticated"],
                )

                password = st.text_input(
                    label=login_password_label,
                    placeholder=login_password_placeholder,
                    help=login_password_help,
                    type="password",
                    disabled=st.session_state["authenticated"],
                )

                if st.form_submit_button(
                    label=login_submit_label,
                    disabled=st.session_state["authenticated"],
                    type="primary",
                ):
                    response = (
                        client.table(user_tablename)
                        .select(f"{username_col}, {password_col}, {token_col}, {role_col}, {id_col}",)
                        .eq(username_col, username)
                        .eq(password_col, password)
                        .execute()
                    )

                    if len(response.data) > 0:
                        login_success(login_success_message, username, response.data[0][token_col], response.data[0][role_col], response.data[0][id_col])
                    else:
                        st.error(login_error_message)
                        st.session_state["authenticated"] = False
                        

def main() -> None:
    login_form()

if __name__ == "__main__":
    main()
