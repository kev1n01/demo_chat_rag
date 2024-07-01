import openai
from streamlit_mic_recorder import speech_to_text
import streamlit as st
import base64
from gtts import gTTS
import uuid, os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# init openai
def setup_client_elevenlabs(api_key): 
    return ElevenLabs(api_key=api_key)
    
def text_to_speech_eleven(client, text):
    response = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    path = os.getcwd() + '/audios/'
    if os.path.exists(path) is False:
        os.mkdir('audios')

    filename = f'{os.getcwd()}/audios/{str(uuid.uuid4())}.mp3'
    with open(filename, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    return filename

# init openai
def setup_client_openai(api_key): 
    return openai.OpenAI(api_key=api_key)

# convert audio to text
def audio_to_text():
    text = speech_to_text(
        language='es',
        start_prompt="Click para grabar audio 🎙️",
        stop_prompt="Click para enviar audio ⬆️",
        just_once=False,
        callback=None,
        key=None,
        use_container_width=True,
        args=(),
        kwargs={},
    )
    return text
    
# convert text to audio with tts-1 openai
def text_to_audio(client, text): # convert text to audio 
    res = client.audio.speech.create(model="tts-1",voice="echo", input=text)
    filename = f'{os.getcwd()}/audios/{str(uuid.uuid4())}.mp3'
    res.stream_to_file(filename)

# convert text to audio with gtts
def tts(text): 
    tts = gTTS(text=text, lang='es', slow=False, lang_check=False, tld='es')
    filename = f'{os.getcwd()}/audios/{str(uuid.uuid4())}.mp3'
    tts.save(filename)
    return filename

# autoplay config into audio
def autoplay(audio_file):
    with open(audio_file, "rb") as audio_file:
        bytes = audio_file.read()
    
    base64_audio = base64.b64encode(bytes).decode("utf-8")
    html_audio = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay style="display: none"> '
    st.markdown(html_audio, unsafe_allow_html=True)
