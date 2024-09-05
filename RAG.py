from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.faiss import FAISS
import os
os.environ['LANGCHAIN_TRACING_V2']='true'
os.environ['LANGCHAIN_API_KEY']='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'
def getRetriever(filePath=None):
    print('document Loading...')
    loader=PyPDFLoader('Requirements.pdf')
    doc=loader.load()
    print('document Loading Done')
    print('document Embedding Start...')
    vectorStore=FAISS.from_documents(documents=doc,embedding=OllamaEmbeddings(model='gemma2:2b'))
    print('document Embedding Done')
    vectorStore.save_local('faiss.index')
    return vectorStore.as_retriever()
def getRequirements(filePath:str=None)->str:
    loader=PyPDFLoader('Requirements.pdf')
    doc=loader.load()
    return doc
   
