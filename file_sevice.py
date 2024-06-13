import os 
from langchain_community.document_loaders.pdf import PyMuPDFLoader

def load_files():
    upload_files = []
    for file in get_files_uploaded():
        loader = PyMuPDFLoader("pdf/" + file)
        docs = loader.load()
        upload_files.append(docs)
    return upload_files

def upload_files(files):
    for file in files:
        with open(os.getcwd() + '/pdf/' + file.name, mode='wb') as f:
            f.write(file.getbuffer())

def get_files_uploaded():
    path = os.getcwd() + '/pdf/'
    if os.path.exists(path) is False:
        os.mkdir('pdf')
    files = os.listdir(path)
    return files

def delete_audio():
    files = os.listdir(os.getcwd() + '/audios/')
    for f in files:
        os.remove(os.getcwd() + '/audios/' + f)

def delete_files():
    files = os.listdir(os.getcwd() + '/pdf/')
    for f in files:
        os.remove(os.getcwd() + '/pdf/' + f)