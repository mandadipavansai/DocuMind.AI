// File: frontend/src/components/ReportComponent.jsx

import React, { useState } from 'react';
import {
    Box, Typography, Stack, TextField, Button, Paper,
    CircularProgress, Snackbar, Alert, useTheme,
} from '@mui/material';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import axios from 'axios';

const ReportComponent = ({ isReady }) => {
    const [reportRequest, setReportRequest] = useState('Generate a report with Introduction and Clinical Findings');
    const [isGenerating, setIsGenerating] = useState(false);
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');
    const [snackbarSeverity, setSnackbarSeverity] = useState('info');
    const theme = useTheme();

    const showSnackbar = (message, severity = 'info') => {
        setSnackbarMessage(message);
        setSnackbarSeverity(severity);
        setSnackbarOpen(true);
    };

    const handleGenerateReport = async () => {
        if (!reportRequest.trim() || !isReady) {
            if (!isReady) showSnackbar('Please upload documents before generating a report.', 'warning');
            return;
        }

        setIsGenerating(true);
        showSnackbar('Generating report... This may take a moment.', 'info');

        try {
            // --- Make sure backend URL is correct ---
            const response = await axios.post('http://127.0.0.1:8000/generate_report/',
                { request: reportRequest },
                { responseType: 'blob' } // Expect binary file data
            );

            const blob = new Blob([response.data], { type: 'application/pdf' });
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);

            const contentDisposition = response.headers['content-disposition'];
            let filename = `generated_report_${Date.now()}.pdf`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                if (filenameMatch && filenameMatch.length === 2)
                    filename = filenameMatch[1];
            }
            link.download = filename;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(link.href); // Clean up

            showSnackbar('Report generated and download started.', 'success');

        } catch (error) {
            console.error('Report generation error:', error);
            let errorMsg = 'An unexpected error occurred during report generation.';
            // Try reading error blob as text
             if (error.response && error.response.data instanceof Blob) {
                try {
                    // Convert blob to text and then parse as JSON
                    const errorJsonText = await error.response.data.text();
                    const errorJson = JSON.parse(errorJsonText);
                    errorMsg = errorJson.detail || errorMsg;
                } catch (parseError) {
                     // Blob wasn't JSON or couldn't be read/parsed
                     console.error("Could not parse error blob:", parseError);
                }
            } else if (error.response?.data?.detail) { // Check for standard JSON error
               errorMsg = error.response.data.detail;
            }
            showSnackbar(errorMsg, 'error');
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'medium' }}>
                2. Generate Report
            </Typography>
            <Stack spacing={2} mt={2}>
                <TextField
                    label="Report Request" variant="outlined" fullWidth multiline rows={2}
                    value={reportRequest} onChange={(e) => setReportRequest(e.target.value)}
                    disabled={!isReady || isGenerating} size="small"
                    helperText="Describe sections (e.g., 'Introduction and Findings')."
                />
                <Button
                    variant="contained" color="secondary" onClick={handleGenerateReport}
                    disabled={!isReady || isGenerating || !reportRequest.trim()}
                    startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : <FileCopyIcon />}
                    size="large" fullWidth
                >
                    {isGenerating ? 'Generating...' : 'Generate PDF Report'}
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
export default ReportComponent;