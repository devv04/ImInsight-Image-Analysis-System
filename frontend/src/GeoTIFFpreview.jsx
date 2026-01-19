
// frontend/src/App.jsx
import Upload from './upload';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="navy-header">
        <h1>IMInsight Image Analysis System</h1>
      </header>
      <main className="content-container">
        <Upload />
      </main>
    </div>
  );
}

export default App;
