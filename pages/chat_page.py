import streamlit as st
from rag import get_conversation_chain, get_vectorstore_supabase
from services.tts_service import audio_to_text, autoplay, text_to_audio, setup_client_openai, tts, setup_client_elevenlabs, text_to_speech_eleven
from template_chat import css_all
from utils import stream_data, sendMessageToUser, sendReplyToUser
from services.db_service import getDataWhere

def play_audio(text):
    if st.session_state.tts_model == 'openai':
        client = setup_client_openai(st.secrets["connections"]["openai"]["OPENAI_API_KEY"])
        filename_audio = text_to_audio(client, text)
        autoplay(filename_audio)
    if st.session_state.tts_model == 'gtts':
        filename_audio = tts(text)
        autoplay(filename_audio)
    if st.session_state.tts_model == 'elevenlabs':
        client = setup_client_elevenlabs(st.secrets["connections"]["elevenlabs"]["ELEVENLABS_API_KEY"])
        filename_audio = text_to_speech_eleven(client, text)
        autoplay(filename_audio)

st.markdown(css_all, unsafe_allow_html=True)

if "db_messages" not in st.session_state:
    st.session_state.db_messages = []

# initialize sidebar
with st.sidebar:
    st.header('ASISTENTE :green[DEACHE] 🤖')
    st.success('Bienvenido ' + st.session_state.username)

    st.selectbox('Selecciona modelo TTS', ('gtts','elevenlabs', 'whisper'), key="tts_model")
#initialize component microphone
text_from_audio = audio_to_text()

#get all messages from db from user logging
st.session_state.db_messages = getDataWhere(table="messages", selector="*", condition="user_id", value=st.session_state.user_id)

#iniitialize default message to bot
if "messages" not in st.session_state.keys():
    st.session_state.messages = []
    if len(st.session_state.db_messages) > 0:
        for msg in st.session_state.db_messages:
            st.session_state.messages.append({"role": "user", "content": msg['content']})
            # Fetch corresponding reply
            reply = getDataWhere(table="replies", selector="*", condition="message_id", value=msg['id'])
            if reply['data']:
                st.session_state.messages.append({"role": "assistant", "content": reply['data'][0]['content']})
    
    st.session_state.messages = [
        {"role": "assistant", "content": "Bienvenido mi nombre es Deache, ¿Qué consulta tienes?"}]
    play_audio("Bienvenido mi nombre es Deache, ¿Qué consulta tienes?")

#display messages into chat
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
                # cargar vectors del db supabase
                vectorstore = get_vectorstore_supabase()
                
                # estado que recibe la respuesta de la consulta
                chain = get_conversation_chain(vectorstore)

                # se envia la consulta
                response = chain({'question': input})

                # se reproduce la respuesta
                play_audio(response["answer"])

                # se muestra la respuesta en el chat
                st.write_stream(stream_data(response["answer"]))
        
        # se agrega la respuesta al historial de chat
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
    sendMessageToUser(input)
    sendReplyToUser(response["answer"])
    # se limpia el input
    input = None

#escribir mensaje de usuario por voz
if text_from_audio:
    st.session_state.messages.append({"role": "user", "content": text_from_audio})
    with st.chat_message("user"):
        st.write_stream(stream_data(text_from_audio))
    
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Espere un momento por favor..."):  
                # cargar vectors del db server
                vectorstore = get_vectorstore_supabase()
                
                # estado que recibe la respuesta de la consulta
                chain = get_conversation_chain(vectorstore)

                # se envia la consulta
                response = chain({'question': text_from_audio})

                # se reproduce la respuesta
                play_audio(response["answer"])

                # se muestra la respuesta en el chat
                st.write_stream(stream_data(response["answer"]))
        # se agrega la respuesta al historial de chat
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
    sendMessageToUser(text_from_audio)
    sendReplyToUser(response["answer"])
    # se limpia el input de audio
    text_from_audio = None
