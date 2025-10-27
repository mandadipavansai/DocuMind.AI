import os
import shutil
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


DATA_PATH = "../sample_data" 

CHROMA_PATH = "chroma_db" 


PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
---
Answer the question based on the above context: {question}
"""

def main():
    print("Starting the local RAG pipeline...")


    print(f"Loading documents from {DATA_PATH}...")
    loader = DirectoryLoader(DATA_PATH, glob="**/*", show_progress=True, use_multithreading=True)
    documents = loader.load()
    if not documents:
        print("No documents found. Please check your DATA_PATH.")
        return

    print(f"Loaded {len(documents)} document(s).") 


    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")


    print("Creating local embeddings... (This may take a moment)")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


    if os.path.exists(CHROMA_PATH):
        print("Clearing old database.")
        shutil.rmtree(CHROMA_PATH)


    db = Chroma.from_documents(
        splits, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved embeddings to {CHROMA_PATH}.")


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


    print("\n--- RAG Test ---")
    

    test_question = "What is the main finding in the clinical report?" 

    print(f"Question: {test_question}")
    

    answer = rag_chain.invoke(test_question)
    
    print("Answer:")
    print(answer)
    print("------------------")
    print("RAG pipeline test complete.")

if __name__ == "__main__":
    main()