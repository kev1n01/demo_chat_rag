import streamlit as st
import os
from dotenv import load_dotenv
from template_chat import css, bot_template, user_template
from tts_service import audio_to_text, autoplay, text_to_audio, setup_client_openai, tts, setup_client_elevenlabs, text_to_speech_eleven
from file_sevice import upload_files, get_files_uploaded, load_files
from utils import stream_data
import uuid
from rag import get_pdf_text, get_text_chunks, get_vectorstore, get_conversation_chain

# display message into chatbox
def display_message(user_question):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write_stream(stream_data(user_question, 0.1))

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Consultando informacion..."):  
                response = st.session_state.conversation_chain({'question': user_question})
                st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
            play_audio(response["answer"])
            st.write_stream(stream_data(response["answer"], 0.3))


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
        
def execute_rag(files):
    # obtener texto de pdf
    raw_text = get_pdf_text(files)

    # obtener texto en trozos o chunks
    text_chunks = get_text_chunks(raw_text)                

    # crear los embeddings y almacena en db vector
    vectorstore = get_vectorstore(text_chunks)

    # estado que recibe la respuesta de la consulta
    st.session_state.conversation_chain = get_conversation_chain(vectorstore)

def main():
    load_dotenv()
    st.set_page_config(page_title='DeacheChat', page_icon='👽', layout='wide')
    st.session_state.files_uploaded = get_files_uploaded()

    #mostrar sidebar
    with st.sidebar:
        with st.form(key="Form :", clear_on_submit = False):
            st.file_uploader("Cargar archivos aquí 📁", accept_multiple_files=True, type=["pdf"], key="files")
            submit = st.form_submit_button('Guardar archivos', use_container_width=True, type="primary")
        
        if submit: # si hace click en guardar archivos
            if len(st.session_state.files) == 0:
                st.warning('No se han subido archivos')
            else:
                with st.spinner('Procesando...'):
                    upload_files(st.session_state.files)
                    st.toast('Archivos subidos correctamente', icon="✅")
        
        # mostrar lista de archivos cargados 
        st.data_editor(get_files_uploaded(), hide_index=True,use_container_width=True)
        
        text_from_audio = audio_to_text()

        # mostrar opciones 
        st.selectbox('Selecciona modelo tts', ('elevenlabs', 'gtts', 'openai'), key="tts_model")
    if st.session_state.files_uploaded is not None:
        if 'conversation_chain' not in st.session_state:
            st.session_state.conversation_chain = None
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        
        if "messages" in st.session_state != 0:
            st.session_state.messages = []

        # inicializar conversacion con saludo de deache
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [{"role": "assistant", "content": "Bienvenido mi nombre es Deache, ¿Qué consultas tienes?"}]
            for message in st.session_state.messages:
                play_audio(message["content"])
                with st.chat_message(message["role"]):
                    st.write_stream(stream_data(message["content"], 0.3))         

        # mostrar mensajes
        # if st.session_state.messages[0]["role"] != "assistant":
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write_stream(stream_data(message["content"], 0.3))    

        text_chat = st.chat_input('Ingresa tu consulta aquí')
        if text_from_audio:
            st.session_state.user_question = text_from_audio

        if text_chat:
            st.session_state.user_question = text_chat

        if st.session_state.get('user_question'):
            display_message(st.session_state.user_question)
            execute_rag(get_files_uploaded())
            st.session_state.user_question = None  # Resetear la pregunta del usuario
    else:
        st.info("Subir por lo menos un archivo")

if __name__ == '__main__':
    main()