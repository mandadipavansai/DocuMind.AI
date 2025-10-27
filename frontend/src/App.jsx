

import React, { useState } from 'react';

import {
  AppBar, Toolbar, Box, Typography, useTheme,
  Paper, Divider 
} from '@mui/material';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import InfoIcon from '@mui/icons-material/Info';


import FileUploadComponent from './components/FileUploadComponent';
import ChatComponent from './components/ChatComponent';
import ReportComponent from './components/ReportComponent';


import './App.css';

function App() {
  const [isBackendReady, setIsBackendReady] = useState(false);
  const theme = useTheme(); 

  const handleUploadSuccess = () => {
      setIsBackendReady(true);
  }

  return (

    <div className="app-container">

      <AppBar position="static" elevation={1} className="app-header">

        <Toolbar disableGutters sx={{ paddingLeft: '24px', paddingRight: '24px' }}>
          <LocalHospitalIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Healthcare AI Assistant
          </Typography>
        </Toolbar>
      </AppBar>


      <main className="main-section">


        <div className="left-panel">


          <FileUploadComponent onUploadSuccess={handleUploadSuccess} />
          <ReportComponent isReady={isBackendReady} />

          <ChatComponent isReady={isBackendReady} />
        </div>


        <div className="right-panel">

           <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
             <InfoIcon color="primary" sx={{ fontSize: '1.75rem' }}/>
             <h2>About the AI Assistant</h2>
           </Box>
           <Divider sx={{ mb: 2 }}/>
           <p>
             This application demonstrates a Retrieval-Augmented Generation (RAG) system designed for healthcare documents. It uses local AI models to ensure data privacy while allowing interaction with uploaded files.
           </p>

           <div className="content-box box-how">
             <h3>How It Works</h3>
             <ol>
               <li><p><strong>Document Processing:</strong> Uploaded files (PDF, DOCX, etc.) are loaded, split into manageable chunks, and converted into numerical representations (embeddings) that capture semantic meaning.</p></li>
               <li><p><strong>Vector Storage:</strong> These embeddings are stored locally in a specialized vector database (ChromaDB) for efficient similarity searching.</p></li>
               <li><p><strong>Chat Interaction (RAG):</strong> When you ask a question, it's also embedded. The system searches the database for document chunks with similar meaning. These relevant chunks are then provided as context to the local Large Language Model (Phi-3 Mini via Ollama) along with your question, enabling grounded answers.</p></li>
               <li><p><strong>Report Generation:</strong> When requesting a report, an agentic workflow determines which information is needed (e.g., specific sections). Tools are called (currently using placeholders) to extract this information, which is then formatted into a downloadable PDF.</p></li>
             </ol>
           </div>

           <div className="content-box box-usage">
             <h3>Usage Guide</h3>
             <ul>
               <li><p>Use <strong>'Upload Documents'</strong> first. Select files and click <strong>'Upload and Process'</strong>.</p></li>
               <li><p>Use <strong>'Generate Report'</strong> (optional) to request a PDF summary. Describe desired sections.</p></li>
               <li><p>Use <strong>'Chat with Assistant'</strong> to ask questions about the uploaded content once processing is complete.</p></li>
             </ul>
           </div>

           <p className="note">
             Ensure Ollama is running with the required model (Phi-3 Mini). Performance depends on local hardware. Report generation uses placeholders.
           </p>
        </div>

      </main> 


      <footer className="app-footer">
        <p>GenAI Engineer Task - {new Date().getFullYear()}</p>
      </footer>
    </div> 
  );
}
export default App;