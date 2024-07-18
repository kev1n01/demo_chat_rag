import time
import streamlit as st
from services.db_service import insertData

def stream_data(text, speed=0.08):
    for w in text.split(" "):
        yield w + " "
        time.sleep(speed)

def sendMessageToUser(message):
    if st.session_state['user_role'] == "user":
        response = insertData(table="messages", data={"user_id": st.session_state['user_id'], "content": message})
        st.session_state['message_id'] = response.data[0]['id']

def sendReplyToUser(message):
    if st.session_state['user_role'] == "user":
        insertData(table="replies", data={"message_id": st.session_state['message_id'], "content": message})