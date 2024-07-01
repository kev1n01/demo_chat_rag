from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os
from supabase import create_client, Client
from langchain.vectorstores.supabase import SupabaseVectorStore

def get_client_supabase():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase

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

# almacena los embeedings en una db vector
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl')
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_vectorstore_supabase():
    embeddings = OpenAIEmbeddings()
    vector_store = SupabaseVectorStore(
        embedding = embeddings,
        client = get_client_supabase(),
        table_name="documents",
        query_name="match_documents",
    )
    return vector_store

# create conversacion entre llm y db vector
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return conversation_chain

# def pinecone(docs):
#     # inicializar pinecone
#     pinecone.init(
#         api_key= os.getenv('PINECONE_API_KEY'),
#         environment='gcp-starter'
#     )

#     index_name = "langchain-demo"
#     embeddings = ''
#     # revisando 
#     if index_name not in pinecone.list_indexes():
#     # Create new Index
#         pinecone.create_index(name=index_name, metric="cosine", dimension=768)
#         docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)
#     else:
#         # Link to the existing index
#         docsearch = Pinecone.from_existing_index(index_name, embeddings)
