import React, { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import InputForm from "./components/InputForm";
import OutputDisplay from "./components/OutputDisplay";

import "./styles/App.css";

const Home = () => {
  const [url, setUrl] = useState("");
  const [output, setOutput] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setOutput([]);
    setIsProcessing(true);

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n");
        buffer = parts.pop(); // Keep the last partial JSON string

        for (const part of parts) {
          if (part.trim()) {
            const data = JSON.parse(part);
            setOutput((prevOutput) => [...prevOutput, data]);
          }
        }
      }

      // Handle any remaining data in the buffer
      if (buffer.trim()) {
        const data = JSON.parse(buffer);
        setOutput((prevOutput) => [...prevOutput, data]);
      }
    } catch (error) {
      setOutput([
        { type: "error", content: `An error occurred: ${error.message}` },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };
  return (
    <div className="app-container">
      <h1>Research Town</h1>
      <InputForm url={url} setUrl={setUrl} handleSubmit={handleSubmit} />
      {isProcessing && <p>Processing...</p>}
      <OutputDisplay output={output} />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter basename={"/"}>
      <Routes>
        <Route path="/" element={<Home />} exact />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
