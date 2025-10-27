
import os
import sys
import shutil
import pytesseract

print(f"--- Running rag_module.py ---")
print(f"Python executable: {sys.executable}")
print(f"Initial PATH: {os.environ.get('PATH', 'PATH not set')}")

TESSERACT_DIR = r'C:\Program Files\Tesseract-OCR'
TESSDATA_DIR = os.path.join(TESSERACT_DIR, 'tessdata')
TESSERACT_EXE_PATH = os.path.join(TESSERACT_DIR, 'tesseract.exe')

if not os.path.exists(TESSERACT_EXE_PATH):
    print(f"FATAL ERROR: Tesseract executable not found at: {TESSERACT_EXE_PATH}")
else:
    print(f"Verified Tesseract executable exists at: {TESSERACT_EXE_PATH}")
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE_PATH
    print(f"Set pytesseract.tesseract_cmd to: {pytesseract.pytesseract.tesseract_cmd}")

    if TESSERACT_DIR not in os.environ.get('PATH', ''):
        print(f"Adding Tesseract directory to process PATH: {TESSERACT_DIR}")
        os.environ['PATH'] += os.pathsep + TESSERACT_DIR
        print(f"Updated PATH: {os.environ.get('PATH')}")
    else:
        print(f"Tesseract directory already in process PATH.")

    if os.path.isdir(TESSDATA_DIR):
        os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
        print(f"Set TESSDATA_PREFIX environment variable to: {os.environ['TESSDATA_PREFIX']}")
    else:
        print(f"WARNING: Tesseract tessdata directory not found at: {TESSDATA_DIR}")

    tesseract_found_path = shutil.which("tesseract")
    if tesseract_found_path:
        print(f"Tesseract command found by shutil.which: {tesseract_found_path}")
    else:
        print("WARNING: Tesseract command still not found by shutil.which after PATH modification.")

print("--- Proceeding with other imports ---")
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

DATA_PATH = "../sample_data"
CHROMA_PATH = "chroma_db"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
---
Answer the question based on the above context: {question}
"""

def load_documents():
    print(f"Loading documents from {DATA_PATH}...")
    loader = DirectoryLoader(DATA_PATH, glob="**/*", show_progress=True, use_multithreading=True)
    try:
        documents = loader.load()
        if not documents:
            print("Warning: No documents found in the specified path.")
            return []
        print(f"Loaded {len(documents)} document(s).")
        return documents
    except Exception as e:
        print(f"Error loading documents: {e}")
        raise e

def split_documents(documents):
    if not documents:
        print("No documents to split.")
        return []
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")
    return splits

def save_to_chroma(splits):
    if not splits:
        print("No document splits to save to Chroma.")
        return None
    print("Creating local embeddings... (This may take a moment)")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if os.path.exists(CHROMA_PATH):
        print("Clearing old Chroma database.")
        shutil.rmtree(CHROMA_PATH)
    db = Chroma.from_documents(splits, embeddings, persist_directory=CHROMA_PATH)
    print(f"Saved embeddings to {CHROMA_PATH}.")
    return db

def process_documents():
    try:
        documents = load_documents()
        splits = split_documents(documents)
        save_to_chroma(splits)
        print("Document processing complete.")
    except Exception as e:
        print(f"An error occurred during document processing: {e}")
        raise e

def get_rag_chain():
    print("Setting up RAG chain...")
    if not os.path.exists(CHROMA_PATH):
        print(f"Error: Chroma database not found at {CHROMA_PATH}. Please upload documents first.")
        raise FileNotFoundError(f"Chroma database not found at {CHROMA_PATH}")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatOllama(model="llama3:8b")
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain is ready.")
    return rag_chain

if __name__ != "__main__":
    if not shutil.which("tesseract"):
        print("\n*********************************************************************")
        print("WARNING: Tesseract command not found by system PATH check on import.")
        print("The application might fail if OCR is needed for document processing.")
        print("*********************************************************************\n")

