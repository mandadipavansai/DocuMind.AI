// File: frontend/src/components/ChatComponent.jsx

import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Typography, Stack, TextField, Paper, CircularProgress,
  Snackbar, Alert, IconButton, List, ListItem, Avatar, useTheme,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import AssistantIcon from '@mui/icons-material/Assistant';
import axios from 'axios';

const ChatComponent = ({ isReady }) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('error');
  const chatEndRef = useRef(null);
  const theme = useTheme();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const showSnackbar = (message, severity = 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSendMessage = async () => {
     if (!message.trim() || !isReady) {
            if (!isReady) showSnackbar('Please upload and process documents first.', 'warning');
            return;
        }
        const userMessage = { role: 'user', content: message };
        setChatHistory((prev) => [...prev, userMessage]);
        setMessage('');
        setIsLoading(true);
        try {
          const response = await axios.post('http://127.0.0.1:8000/chat/', { query: userMessage.content });
          const aiMessage = { role: 'ai', content: response.data.answer };
          setChatHistory((prev) => [...prev, aiMessage]);
        } catch (error) {
          console.error('Chat error:', error);
          const errorText = `Error: ${error.response?.data?.detail || 'Could not get response from assistant.'}`;
          const errorMessage = { role: 'ai', content: errorText };
          setChatHistory((prev) => [...prev, errorMessage]);
          showSnackbar(errorText, 'error');
        } finally {
          setIsLoading(false);
        }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  return (
    // Main Paper container for the chat component
    // *** Use minHeight and height: 100% to fill parent ***
    <Paper elevation={3} sx={{
        p: 3,
        borderRadius: 2,
        display: 'flex',
        flexDirection: 'column',
        minHeight: '450px', // Set a reasonable minimum height
        height: '100%', // Crucial: Allow Paper to fill the height of its parent Box/Grid item container
        flexGrow: 1 // Ensure it tries to grow if parent allows
     }}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'medium' }}>
        3. Chat with Assistant
      </Typography>
      {/* Chat History Area - flexGrow allows this to take up available space */}
      <List sx={{ flexGrow: 1, overflowY: 'auto', mb: 2, pr: 1, bgcolor: theme.palette.grey[50], borderRadius: 1 }}>
        {!isReady && (
            <ListItem>
                <Alert severity="info" sx={{ width: '100%' }}>Upload documents to start chatting.</Alert>
            </ListItem>
        )}
        {/* Map through chat history */}
        {chatHistory.map((chat, index) => (
          <ListItem key={index} sx={{ display: 'flex', justifyContent: chat.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {chat.role === 'ai' && <Avatar sx={{ bgcolor: theme.palette.grey[300], mr: 1 }}><AssistantIcon fontSize="small"/></Avatar>}
            <Box
              sx={{
                p: 1.5,
                bgcolor: chat.role === 'user' ? 'primary.main' : 'background.paper',
                color: chat.role === 'user' ? 'primary.contrastText' : 'text.primary',
                borderRadius: chat.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                maxWidth: '80%', whiteSpace: 'pre-wrap', boxShadow: 1,
              }}
            >
              <Typography variant="body1">{chat.content}</Typography>
            </Box>
            {chat.role === 'user' && <Avatar sx={{ bgcolor: 'primary.light', ml: 1 }}><PersonIcon fontSize="small"/></Avatar>}
          </ListItem>
        ))}
        {/* Loading Indicator */}
        {isLoading && (
          <ListItem sx={{ justifyContent: 'flex-start' }}>
             <Avatar sx={{ bgcolor: theme.palette.grey[300], mr: 1 }}><AssistantIcon fontSize="small"/></Avatar>
             <CircularProgress size={20} sx={{ mr: 1 }}/>
             <Typography variant="body2" color="text.secondary">Assistant is thinking...</Typography>
          </ListItem>
        )}
        {/* Invisible div to scroll to */}
        <div ref={chatEndRef} />
      </List>
      {/* Input Area - mt: 'auto' pushes this to the bottom */}
      <Paper elevation={2} sx={{ p: 1.5, display: 'flex', mt: 'auto', borderRadius: 2, flexShrink: 0 /* Prevent input area shrinking */ }}>
        <TextField
          fullWidth variant="outlined"
          placeholder={isReady ? "Ask a question..." : "Upload documents first..."}
          value={message} onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress} disabled={isLoading || !isReady}
          size="small"
        />
        <IconButton
          color="primary" onClick={handleSendMessage}
          disabled={isLoading || !message.trim() || !isReady} sx={{ ml: 1 }}
          aria-label="send message"
        >
          {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
        </IconButton>
      </Paper>
       {/* Snackbar for errors/info */}
       <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={() => setSnackbarOpen(false)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
           <Alert onClose={() => setSnackbarOpen(false)} severity={snackbarSeverity} variant="filled" sx={{ width: '100%' }}>
               {snackbarMessage}
           </Alert>
       </Snackbar>
    </Paper>
  );
};
export default ChatComponent;