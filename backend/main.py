
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from fastapi.responses import FileResponse
import report_generator
import time
import rag_module as rag
import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_chain = None
try:
    if os.path.exists(rag.CHROMA_PATH):
        print("ChromaDB found. Initializing RAG chain...")
        rag_chain = rag.get_rag_chain()
        print("RAG chain initialized successfully.")
    else:
        print("ChromaDB not found on startup. Upload documents to initialize.")
except Exception as e:
    print(f"Error initializing RAG chain on startup: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Healthcare AI Assistant API"}

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    print(f"Received {len(files)} files for upload.")

    if os.path.exists(rag.DATA_PATH):
        print(f"Clearing existing data path: {rag.DATA_PATH}")
        shutil.rmtree(rag.DATA_PATH)
    os.makedirs(rag.DATA_PATH)
    print(f"Created data path: {rag.DATA_PATH}")

    saved_files = []
    for file in files:
        file_path = os.path.join(rag.DATA_PATH, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Successfully saved file: {file.filename}")
            saved_files.append(file.filename)
        except Exception as e:
            print(f"Error saving file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error saving file '{file.filename}': {e}")
        finally:
            file.file.close()

    global rag_chain
    try:
        print("Starting document processing...")
        rag.process_documents()
        print("Document processing finished. Re-initializing RAG chain...")
        rag_chain = rag.get_rag_chain()
        print("RAG chain re-initialized successfully.")
    except Exception as e:
        print(f"Error processing documents or initializing RAG chain: {e}")
        rag_chain = None
        raise HTTPException(status_code=500, detail=f"Error processing documents: {e}")

    return {"message": f"Successfully uploaded and processed {len(saved_files)} files."}

class ChatRequest(BaseModel):
    query: str

@app.post("/chat/")
async def chat_with_docs(request: ChatRequest):
    global rag_chain
    if rag_chain is None:
        print("Error: /chat called but RAG chain is not initialized.")
        raise HTTPException(status_code=503, detail="Assistant is not ready. Please upload documents first.")
    print(f"Received query for /chat: {request.query}")
    try:
        answer = rag_chain.invoke(request.query)
        print(f"Generated RAG answer: {answer}")
        return {"answer": answer}
    except Exception as e:
        print(f"Error during RAG chain invocation: {e}")
        error_detail = f"Error generating response: {e}"
        if "model runner has unexpectedly stopped" in str(e):
            error_detail = "Error generating response: The language model failed, possibly due to resource limits."
            raise HTTPException(status_code=503, detail=error_detail)
        else:
            raise HTTPException(status_code=500, detail=error_detail)

class ReportRequest(BaseModel):
    request: str

@app.post("/generate_report/")
async def generate_report_endpoint(request: ReportRequest):
    print(f"Received report request for /generate_report: {request.request}")
    if rag_chain is None:
        print("Error: /generate_report called but RAG chain not initialized.")
        raise HTTPException(status_code=503, detail="Cannot generate report. Please upload documents first.")
    pdf_filepath = None
    try:
        print("Invoking agentic graph for report generation...")
        report_content_text = graph.run_graph(request.request)
        print(f"Graph generation finished. Raw content length: {len(report_content_text)}")
        report_data_for_pdf = {"report_text": report_content_text}
        timestamp = int(time.time())
        temp_dir = "temp_reports"
        os.makedirs(temp_dir, exist_ok=True)
        pdf_filename = f"report_{timestamp}.pdf"
        pdf_filepath = os.path.join(temp_dir, pdf_filename)
        print(f"Generating PDF: {pdf_filepath}")
        generated_path = report_generator.create_report_pdf(report_data_for_pdf, pdf_filepath)
        if generated_path and os.path.exists(generated_path):
            print(f"Sending PDF file: {generated_path}")
            return FileResponse(
                path=generated_path,
                media_type='application/pdf',
                filename=f"generated_report_{timestamp}.pdf",
            )
        else:
            print(f"Error: PDF file not found after generation attempt: {generated_path}")
            raise HTTPException(status_code=500, detail="Failed to generate or locate the PDF report after creation.")
    except Exception as e:
        print(f"Error during report generation endpoint: {e}")
        error_detail = f"Error generating report: {e}"
        if "model runner has unexpectedly stopped" in str(e):
            error_detail = "Error generating report: The language model failed, possibly due to resource limits."
            raise HTTPException(status_code=503, detail=error_detail)
        else:
            raise HTTPException(status_code=500, detail=error_detail)

