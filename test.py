from file_sevice import get_files_uploaded
from rag import get_pdf_text
from langchain_community.document_loaders.pdf import PyMuPDFLoader

upload_files = []
for file in get_files_uploaded():
    loader = PyMuPDFLoader("pdf/" + file)
    docs = loader.load()
    upload_files.append(docs)


print(upload_files)

