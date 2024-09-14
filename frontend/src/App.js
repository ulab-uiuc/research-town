import React, { useState } from 'react';
import InputForm from './components/InputForm';
import OutputDisplay from './components/OutputDisplay';
import './styles/App.css';

function App() {
  const [url, setUrl] = useState('');
  const [output, setOutput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setOutput('');
    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        setOutput((prevOutput) => prevOutput + chunk);
      }
    } catch (error) {
      setOutput(`An error occurred: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="app-container">
      <h1>Arxiv Paper Link</h1>
      <InputForm url={url} setUrl={setUrl} handleSubmit={handleSubmit} />
      {isProcessing && <p>Processing...</p>}
      <OutputDisplay output={output} />
    </div>
  );
}

export default App;
