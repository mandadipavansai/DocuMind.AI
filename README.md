# HealthDoc Assistant AI 🩺📄

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

👋 Introduction

Hi, I’m Mandadi Pavan Sai Kumar — welcome to DocuMind.AI.

This project is designed to make working with any kind of document — research papers, reports, business PDFs, academic notes, or even medical files — faster and easier.
Instead of manually reading through pages, you can upload your files, chat with them, and even generate structured, professional summary reports in just a few clicks.

DocuMind.AI combines Retrieval-Augmented Generation (RAG) and an agent-based workflow to deliver accurate, context-aware answers — all running locally for speed, privacy, and full data control.

---

✨ Features

📂 Multi-Format Document Handling: Upload and process PDFs, DOCX files, and image files (PNG, JPG) containing text, tables, or charts.

💬 Intelligent Q&A: Ask any question about your document and get accurate, grounded answers using an advanced RAG pipeline.

📑 Automated Report Generation: Instantly create structured PDF reports with sections like Overview, Key Points, Insights, Figures, Tables, and Summaries.

🧠 Agentic Workflow: Uses LangGraph to manage specialized agents for extraction, summarization, and report assembly.

💾 Local Vector Storage: Uses ChromaDB for efficient local embedding storage and retrieval — keeping everything on your machine.

💻 Local LLM Integration: Powered by Ollama (tested with llama3:8b) for private, offline language processing.

🌐 User-Friendly Interface: Clean and simple web dashboard for uploading files, chatting, and downloading reports.

---



🛠️ Tech Stack

This project brings together several modern and efficient technologies:

Backend:

Language: Python 3.11+

API Framework: FastAPI

ASGI Server: Uvicorn

AI Frameworks: LangChain (Core, Community, Text Splitters), LangGraph

LLM Provider: Ollama (llama3:8b)

Embeddings: HuggingFace Sentence Transformers (all-MiniLM-L6-v2)

Vector Database: ChromaDB (local persistence)

PDF Generation: ReportLab

OCR: Pytesseract (requires system Tesseract installation)

File Handling: python-multipart, unstructured[pdf], tqdm

Frontend:

Framework: React (Vite)

UI Components: Material UI (@mui/material, @mui/icons-material)

Styling: Emotion (@emotion/react, @emotion/styled)

API Communication: Axios

Build Tool: Vite

Environment:

Python Virtual Environment (venv)

Node.js / npm for frontend

---

Architecture

[Insert Your Architecture Diagram Here]

Workflow Summary:

1) Frontend (User Interaction): Uploads documents and sends questions via the web interface.

2) API Layer (FastAPI): Handles endpoints for /upload, /chat, and /generate_report.

3) Document Ingestion (rag_module.py): Extracts text (via OCR if needed), chunks content, embeds using HuggingFace, and stores in ChromaDB.

4) Query & Answer (rag_module.py): For each question, retrieves the most relevant document chunks and generates context-aware answers using Ollama.

5) Report Generation (graph.py): LangGraph coordinates multiple agents (extraction, summarization, assembly) to build structured report content.

6) PDF Creation (report_generator.py): Converts structured content into a polished PDF using ReportLab.

7) Response Delivery (FastAPI): Returns chat responses or downloadable PDFs to the frontend.

---

⚙️ Setup & Installation

Prerequisites

Before starting, make sure the following are installed on your system:

* Python 3.11+ ([python.org](https://www.python.org/))
* Git ([git-scm.com](https://git-scm.com/))
* Node.js and npm ([nodejs.org](https://nodejs.org/))
* Ollama installed and running ([ollama.com](https://ollama.com/))
* Tesseract OCR engine installed and added to your system PATH ([Tesseract GitHub](https://github.com/tesseract-ocr/tesseract#installing-tesseract))

Installation Steps
Step 1: Clone the Repository

git clone https://github.com/mandadipavansai/health_doc_assist.ai.git
cd health_doc_assist.ai


Step 2: Set Up the Backend

# Create a virtual environment
python -m venv .venv

# Activate it
# For Windows:   .\.venv\Scripts\Activate.ps1

# For macOS/Linux:  source .venv/bin/activate

# Move into the backend folder
cd backend

# Install required Python packages
pip install -r requirements.txt

# Go back to the main directory
cd ..


Step 3: Download the LLM

ollama pull llama3:8b

Step 4: Set Up the Frontend

cd frontend
npm install
cd ..

✅ Installation Done!

You’ve now installed everything needed for DocuMind.AI.
Next — let’s run the project 🚀



---

## 🚀 Usage

Step 1: Start Ollama
Before running anything else, make sure the Ollama server is active:   ollama serve

Step 2: Run the Backend
Start the FastAPI server:

cd backend
uvicorn main:app --reload

Step 3: Run the Frontend
Open a new terminal (keep the backend running), then start the React app:

cd frontend
npm run dev


Step 4: Interact with DocuMind.AI

Open the link shown in the terminal 

Upload a PDF, DOCX, or image file.

Ask any question like:

“Summarize this document.”

“List all key points.”

“Extract data from the table.”

Generate structured reports and download them as PDFs.

🎯 Everything runs locally — no internet upload, no data leaks.

---

💡 Future Work / Improvements

Improve figure and table extraction for research papers.

Enhance report formatting with templates and styles.

Add user authentication and document management dashboard.

Integrate persistent chat history.

Fine-tune retrieval logic for large or mixed-format documents.

Add Docker support for one-step deployment.

---



👤 About Me

Hi, I’m Mandadi Pavan Sai Kumar — a developer passionate about building real-world AI tools that solve practical problems.

This project started as a healthcare assistant but evolved into a universal document intelligence tool. I wanted to create something that helps anyone — students, researchers, analysts, or professionals — get instant insights from complex files without having to read them line by line.

I’m constantly exploring how LLMs and agent systems can make knowledge extraction more natural and accessible.

* GitHub: github.com/mandadipavansai
* LinkedIn: https://www.linkedin.com/in/pavan-sai-kumar-mandadi-533371266/

  
---
