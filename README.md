# HealthDoc Assistant AI 🩺📄

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ## 👋 Introduction

Hi there! I'm **[Your Name/Mandadipavansai]**, and welcome to the **HealthDoc Assistant AI**.

This project aims to simplify how healthcare professionals interact with complex medical documents. In today's world, managing information scattered across PDFs, reports, images, and various file types can be overwhelming. This AI assistant provides a unified platform to:

1.  **Ingest** diverse medical documents.
2.  **Understand** the content through intelligent conversation (Q&A).
3.  **Synthesize** key information into structured, downloadable reports.

It leverages Retrieval-Augmented Generation (RAG) for accurate, context-aware answers and an agentic workflow for sophisticated report creation.

---

## ✨ Features

* 📄 **Multi-Format Document Handling:** Seamlessly upload and process PDFs, DOCX files, and images (PNG, JPG) containing text, tables, or charts.
* 💬 **Intelligent Q&A:** Chat directly with your documents. Get accurate answers grounded in the provided content using a RAG pipeline.
* 📊 **Agentic Report Generation:** Request structured PDF reports containing specific sections like Introduction, Clinical Findings, Prevalence Data, Risk Factors, Figures, Tables, and Summaries.
* 🧠 **Advanced Agent Workflow:** Utilizes LangGraph to orchestrate specialized agents (e.g., extraction, summarization, assembly) for reliable report building.
* 💾 **Local Vector Storage:** Employs ChromaDB for efficient local storage and retrieval of document embeddings.
* 💻 **Local LLM Powered:** Integrates with Ollama (specifically tested with `llama3:8b`) for privacy and control over language processing.
* 🌐 **Simple Web Interface:** An intuitive frontend allows for easy document upload, interactive chat, and report downloading.

---



## 🛠️ Tech Stack

This project combines several powerful technologies:

* **Backend:**
    * **Language:** Python 3.11+
    * **API Framework:** FastAPI
    * **ASGI Server:** Uvicorn
    * **AI/LLM Framework:** LangChain (Core, Community, Text Splitters), LangGraph
    * **LLM Provider:** Ollama (using `llama3:8b`)
    * **Embeddings:** HuggingFace Sentence Transformers (`all-MiniLM-L6-v2`) via `langchain-community`
    * **Vector Database:** ChromaDB (local persistence)
    * **PDF Generation:** ReportLab
    * **OCR:** Pytesseract (requires system Tesseract installation)
    * **File Handling:** `python-multipart`, `unstructured[pdf]`, `tqdm`
* **Frontend:**
    * **Framework/Library:** React (using Vite)
    * **UI Components:** Material UI (`@mui/material`, `@mui/icons-material`)
    * **Styling:** Emotion (`@emotion/react`, `@emotion/styled`)
    * **API Communication:** Axios
    * **Build Tool:** Vite
* **Environment:** Python Virtual Environment (`venv`), Node.js/npm for frontend

---

## 🏗️ Architecture

[Insert Your Architecture Diagram Here - e.g., an image file linked]

**Brief Workflow:**

1.  **User Interaction (Frontend):** Uploads documents or sends messages via the React interface.
2.  **API Request (FastAPI):** Backend receives requests at defined endpoints (`/upload`, `/chat`, `/generate_report`).
3.  **Document Ingestion (`rag_module.py`):** On upload, files are processed, text/data is extracted (using Pytesseract/Unstructured if needed), chunked, embedded (HuggingFace), and stored in ChromaDB.
4.  **Q&A (`rag_module.py`):** Chat messages trigger RAG pipeline -> Retrieve relevant chunks from ChromaDB -> Augment prompt -> Generate answer using Ollama -> Send response.
5.  **Report Generation (`graph.py`):** Report requests initiate LangGraph workflow -> Orchestrator agent plans steps -> Calls tools (extraction, summarization via RAG/Ollama) -> Compiles structured data.
6.  **PDF Creation (`report_generator.py`):** Receives structured data -> Renders PDF using ReportLab.
7.  **API Response (FastAPI):** Sends chat answers or the generated PDF file back to the frontend.

---

## ⚙️ Setup & Installation

**Prerequisites:**

* Python 3.11+ ([python.org](https://www.python.org/))
* Git ([git-scm.com](https://git-scm.com/))
* Node.js and npm ([nodejs.org](https://nodejs.org/))
* Ollama installed and running ([ollama.com](https://ollama.com/))
* Tesseract OCR engine installed and added to your system PATH ([Tesseract GitHub](https://github.com/tesseract-ocr/tesseract#installing-tesseract))

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/mandadipavansai/health_doc_assist.ai.git](https://github.com/mandadipavansai/health_doc_assist.ai.git) # Use your actual repo URL
    cd health_doc_assist.ai
    ```
2.  **Set up Backend:**
    ```bash
    # Create and activate virtual environment
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1 # Windows PowerShell
    # source .venv/bin/activate # Linux/macOS/Git Bash

    # Install dependencies
    cd backend
    pip install -r requirements.txt
    cd ..
    ```
3.  **Download LLM:**
    ```bash
    ollama pull llama3:8b
    ```
    *(Ensure Ollama server is running)*
4.  **Set up Frontend:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

---

## 🚀 Usage

1.  **Ensure Ollama server is running.**
2.  **Start the Backend Server:**
    ```bash
    cd backend
    uvicorn main:app --reload
    ```
    *(API will be live at `http://127.0.0.1:8000`)*
3.  **Start the Frontend Development Server:**
    ```bash
    cd frontend
    npm run dev
    ```
    *(Access the application via the URL provided by Vite, usually `http://localhost:5173` or similar)*
4.  **Interact:**
    * Upload documents using the UI.
    * Ask questions in the chat.
    * Request reports (e.g., "Generate a report with Introduction and Summary"). Download the resulting PDF.

---

## 💡 Future Work / Improvements

* Implement robust, non-placeholder logic for `extract_figures_tables` tool.
* Improve error handling and user feedback mechanisms.
* Add user authentication and document management.
* Enhance prompt engineering for more reliable agent behavior and report quality.
* Optimize embedding and retrieval strategies.
* Implement persistent chat history.
* Explore deploying the application using Docker.

---

## 👋 About Me

Hi, I'm **Mandadi pavan sai kumar **! I'm passionate about exploring the intersection of Artificial Intelligence and practical applications, especially in areas like healthcare technology and natural language processing. This project was an exciting challenge to build a full-stack application integrating RAG, agentic workflows with LangGraph, and local LLMs.

I'm always learning and looking for ways to improve. Feel free to connect or check out my other projects!

* **GitHub:** [github.com/mandadipavansai](https://github.com/mandadipavansai)
* **[Optional: LinkedIn Profile URL]**
* **[Optional: Portfolio URL]**

---

## 📄 License

[Choose a license like MIT, Apache 2.0, or state 'Proprietary' if applicable. If open source, you might add:]
Licensed under the MIT License. See the `LICENSE` file for details.
