from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms.huggingface_hub import HuggingFaceHub

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

# create conversacion entre llm y db vector
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    # llm = HuggingFaceHub()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )
    return conversation_chain
