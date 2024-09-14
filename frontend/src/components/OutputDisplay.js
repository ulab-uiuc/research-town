import React from 'react';

function OutputDisplay({ output }) {
  return (
    <pre className="output-display">
      {output}
    </pre>
  );
}

export default OutputDisplay;
