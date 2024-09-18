import React from "react";
import ProgressBar from "react-bootstrap/ProgressBar";

function ProgressVisualizer({ props }) {
  return <ProgressBar striped variant="success" now={35} key={1} />;
}

export default ProgressVisualizer;
