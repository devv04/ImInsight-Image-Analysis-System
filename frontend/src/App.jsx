import React from 'react';
import Upload from './upload';
import './index.css';

export default function App() {
  return (
    <div className="app-root">
      <Header />
      <main className="main-container">
        <Upload label="Naval Image Intelligence" />
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="header-bar">
      <div className="logo-side">
        <img src="/wesee.png" alt="WeSee Logo Left" className="logo-img" />
      </div>
      <div className="title-block">
        <h1>IMInsight</h1>
        <p className="subtitle">Naval Image Intelligence</p>
      </div>
      <div className="logo-side">
        <img src="/wesee.png" alt="WeSee Logo Right" className="logo-img" />
      </div>
    </header>
  );
}
