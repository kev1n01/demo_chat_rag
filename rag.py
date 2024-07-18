from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores.supabase import SupabaseVectorStore
from services.login_service import init_connection
import streamlit as st

# def get_client_supabase():
#     url: str = os.environ.get("SUPABASE_URL")
#     key: str = os.environ.get("SUPABASE_KEY")
#     supabase: Client = create_client(url, key)
#     return supabase

# lee el pdf y convierte a texto
def get_pdf_text(files):
    text = ''
    for file in files:
        pdf_reader = PdfReader('pdf/'+file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# hace el proceso de split del texto
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore_supabase():
 
    embeddings = OpenAIEmbeddings(api_key=st.secrets["connections"]["openai"]["OPENAI_API_KEY"])
    vector_store = SupabaseVectorStore(
        embedding = embeddings,
        client = init_connection(),
        table_name="documents",
        query_name="match_documents",
    )
    return vector_store

# create conversacion entre llm y db vector
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=st.secrets["connections"]["openai"]["OPENAI_API_KEY"])
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return conversation_chain