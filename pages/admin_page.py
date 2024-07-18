import streamlit as st
from services.file_sevice import upload_files, get_files_uploaded, delete_files

if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = get_files_uploaded()

with st.container():
    with st.form(key="Form :", clear_on_submit = False):
            st.file_uploader("Cargar archivos aquí 📁", accept_multiple_files=True, type=["pdf"], key="files")
            submit = st.form_submit_button('Guardar archivos', use_container_width=True, type="primary", )
        
            if submit:
                if len(st.session_state.files) == 0:
                    st.warning('No se han subido archivos')
                else:
                    upload_files(st.session_state.files)
                    st.session_state.files_uploaded = get_files_uploaded()
                    st.toast('Archivos subidos con éxito', icon="✅")

    st.subheader("Lista de archivos cargados")
    st.data_editor(st.session_state.files_uploaded, hide_index=True,use_container_width=True)
    
    button_delete = st.button("Eliminar archivos cargados")
    if button_delete:
        delete_files()
        st.session_state.files_uploaded = get_files_uploaded()
        st.toast('Archivos eliminados con éxito', icon="✅")
        st.rerun()