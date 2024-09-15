// OutputDisplay.js

import React from 'react';
import ReactMarkdown from 'react-markdown';
import '../styles/OutputDisplay.css'; // Create this CSS file for styling

function OutputDisplay({ output }) {
  return (
    <div className="output-display">
      {output.map((item, index) => {
        switch (item.type) {
          case 'insight':
          case 'idea':
          case 'rebuttal':
            return (
              <div key={index} className="item-container">
                <div className="item-label">
                  {item.type.charAt(0).toUpperCase() + item.type.slice(1)}:
                </div>
                <div className="item-content">
                  <ReactMarkdown>{item.content}</ReactMarkdown>
                </div>
              </div>
            );
          case 'proposal':
            return (
              <div key={index} className="item-container">
                <div className="item-label">Proposal:</div>
                {['q1', 'q2', 'q3', 'q4', 'q5'].map((q) => (
                  <div key={q} className="sub-item">
                    <div className="sub-item-label">{q.toUpperCase()}:</div>
                    <div className="sub-item-content">
                      <ReactMarkdown>{item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
            );
          case 'review':
          case 'metareview':
            return (
              <div key={index} className="item-container">
                <div className="item-label">
                  {item.type.charAt(0).toUpperCase() + item.type.slice(1)}:
                </div>
                {['summary', 'strength', 'weakness', 'ethical_concerns'].map((field) => (
                  <div key={field} className="sub-item">
                    <div className="sub-item-label">
                      {field.replace('_', ' ').toUpperCase()}:
                    </div>
                    <div className="sub-item-content">
                      <ReactMarkdown>{item[field]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
                <div className="sub-item">
                  <div className="sub-item-label">
                    {item.type === 'review' ? 'Score' : 'Decision'}:
                  </div>
                  <div className="sub-item-content">
                    {item[item.type === 'review' ? 'score' : 'decision']}
                  </div>
                </div>
              </div>
            );
          case 'error':
            return (
              <div key={index} className="item-container">
                <p style={{ color: 'red' }}>{item.content}</p>
              </div>
            );
          default:
            return (
              <div key={index} className="item-container">
                <p>Unknown item type.</p>
              </div>
            );
        }
      })}
    </div>
  );
}

export default OutputDisplay;
