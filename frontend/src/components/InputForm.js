import React from 'react';

function InputForm({ url, setUrl, handleSubmit }) {
  return (
    <form onSubmit={handleSubmit} className="input-form">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL"
        required
        className="url-input"
      />
      <button type="submit" className="submit-button">Process</button>
    </form>
  );
}

export default InputForm;
