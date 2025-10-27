// File: frontend/src/components/FileUploadComponent.jsx

import React, { useState, useRef } from 'react';
import {
  Box, Typography, Stack, Button, LinearProgress, Paper,
  CircularProgress, Snackbar, Alert, useTheme,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import axios from 'axios';

const FileUploadComponent = ({ onUploadSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('info');
  const fileInputRef = useRef();
  const theme = useTheme();

  const handleFileChange = (event) => {
    setSelectedFiles(event.target.files);
    setUploadProgress(0);
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
        showSnackbar('Please select files to upload.', 'warning');
        return;
      }
      const formData = new FormData();
      for (let i = 0; i < selectedFiles.length; i++) {
        formData.append('files', selectedFiles[i]);
      }
      setIsUploading(true);
      setUploadProgress(0);
      try {
        // --- Make sure backend URL is correct ---
        const response = await axios.post('http://127.0.0.1:8000/upload/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          },
        });
        showSnackbar(response.data.message, 'success');
        setSelectedFiles(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = ''; // Clear file input
        }
        onUploadSuccess(); // Notify parent
      } catch (error) {
        console.error('Upload error:', error);
        showSnackbar(error.response?.data?.detail || 'An unexpected error occurred during upload.', 'error');
      } finally {
        setIsUploading(false);
        setTimeout(() => setUploadProgress(0), 1500); // Reset progress bar after a delay
      }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'medium' }}>
        1. Upload Documents
      </Typography>
      <Stack spacing={2} mt={2}>
         <Button
            component="label" variant="outlined" startIcon={<UploadFileIcon />}
            disabled={isUploading} fullWidth sx={{ borderStyle: 'dashed', py: 2 }}
          >
            {selectedFiles && selectedFiles.length > 0
              ? `${selectedFiles.length} file(s) selected`
              : 'Choose Files'}
            <input
              type="file" hidden multiple onChange={handleFileChange}
              accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg" ref={fileInputRef}
            />
          </Button>
          {isUploading ? (
             <LinearProgress variant="determinate" value={uploadProgress} sx={{ height: 8, borderRadius: 4 }}/>
          ) : selectedFiles && selectedFiles.length > 0 && (
             <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', mt: 1, wordBreak: 'break-word' }}>
                Selected: {Array.from(selectedFiles).map(f => f.name).join(', ')}
             </Typography>
          )}
        <Button
          variant="contained" color="primary" onClick={handleUpload}
          disabled={isUploading || !selectedFiles || selectedFiles.length === 0}
          startIcon={isUploading ? <CircularProgress size={20} color="inherit" /> : null}
          size="large" fullWidth
        >
          {isUploading ? 'Processing...' : 'Upload and Process'}
        </Button>
      </Stack>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={() => setSnackbarOpen(false)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
           <Alert onClose={() => setSnackbarOpen(false)} severity={snackbarSeverity} variant="filled" sx={{ width: '100%' }}>
               {snackbarMessage}
           </Alert>
       </Snackbar>
    </Paper>
  );
};
export default FileUploadComponent;