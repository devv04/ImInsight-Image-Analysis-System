// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css'; // Ensure this imports global layout
import App from './App'; // Render the App component

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);