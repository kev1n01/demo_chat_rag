import streamlit as st
from file_sevice import upload_files, get_files_uploaded
from dotenv import load_dotenv
import openai
from langchain.vectorstores.pinecone import Pinecone
import pinecone
from rag import get_conversation_chain 
import os
from rag import  get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain
from tts_service import audio_to_text, autoplay, text_to_audio, setup_client_openai, tts, setup_client_elevenlabs, text_to_speech_eleven
from file_sevice import upload_files, get_files_uploaded, load_files, delete_audio, delete_files
from utils import stream_data
from template_chat import css_all

def execute_rag(files):
    # obtener texto de pdf
    raw_text = get_pdf_text(files)

    # obtener texto en trozos o chunks
    text_chunks = get_text_chunks(raw_text)       

    # cargar vectors del db server
    vectorstore = get_vectorstore(text_chunks)
    
    # estado que recibe la respuesta de la consulta
    st.session_state.conversation_chain = get_conversation_chain(vectorstore)

def play_audio(text):
    if st.session_state.tts_model == 'openai':
        client = setup_client_openai(os.environ.get("OPENAI_API_KEY"))
        filename_audio = text_to_audio(client, text)
        autoplay(filename_audio)
    if st.session_state.tts_model == 'gtts':
        filename_audio = tts(text)
        autoplay(filename_audio)
    if st.session_state.tts_model == 'elevenlabs':
        client = setup_client_elevenlabs(os.environ.get("ELEVENLABS_API_KEY"))
        filename_audio = text_to_speech_eleven(client, text)
        autoplay(filename_audio)


def streamlit():
    load_dotenv()
    st.set_page_config(page_title='Deache Chat', page_icon='👽', layout='wide')
    st.markdown(css_all, unsafe_allow_html=True)
    if "files_uploaded" not in st.session_state:
            st.session_state.files_uploaded = get_files_uploaded()

    with st.sidebar:
        st.header('Chatbot :green[DEACHE] :sunglasses:')
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
        text_from_audio = audio_to_text()
        st.selectbox('Selecciona modelo tts', ('gtts','elevenlabs', 'gtts', 'openai'), key="tts_model")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenido mi nombre es Deache, ¿Qué consulta tienes?"}]
        play_audio("Bienvenido mi nombre es Deache, ¿Qué consulta tienes?")

        
    #mostrar mensaajes del chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    #escribir mensaje de usuario por input chat
    if input := st.chat_input("Ingrese su consulta aquí"):
        st.session_state.messages.append({"role": "user", "content": input})
        with st.chat_message("user"):
            st.write(input)
    
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Espere un momento por favor..."):  
                    # obtener texto de pdf
                    raw_text = get_pdf_text(get_files_uploaded())

                    # obtener texto en trozos o chunks
                    text_chunks = get_text_chunks(raw_text)       

                    # cargar vectors del db server
                    vectorstore = get_vectorstore(text_chunks)
                    
                    # estado que recibe la respuesta de la consulta
                    chain = get_conversation_chain(vectorstore)

                    response = chain({'question': input})
                    play_audio(response["answer"])
                    st.write_stream(stream_data(response["answer"]))
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
        input = None

    #escribir mensaje de usuario por voz
    if text_from_audio:
        st.session_state.messages.append({"role": "user", "content": text_from_audio})
        with st.chat_message("user"):
            st.write_stream(stream_data(text_from_audio))
        
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Espere un momento por favor..."):  
                    # obtener texto de pdf
                    raw_text = get_pdf_text(get_files_uploaded())

                    # obtener texto en trozos o chunks
                    text_chunks = get_text_chunks(raw_text)       

                    # cargar vectors del db server
                    vectorstore = get_vectorstore(text_chunks)
                    
                    # estado que recibe la respuesta de la consulta
                    chain = get_conversation_chain(vectorstore)

                    response = chain({'question': text_from_audio})
                    play_audio(response["answer"])
                    st.write_stream(stream_data(response["answer"]))
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
        text_from_audio = None

    
if __name__ == '__main__':
    streamlit()