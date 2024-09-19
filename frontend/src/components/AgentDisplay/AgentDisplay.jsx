import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import AgentList from "./AgentList";
import GraphVisualizer from "./GraphVisualizer";

function AgentDisplay() {
  return (
    <>
      <Row className="mb-3" style={{ marginTop: "2em", marginBottom: "2em" }}>
        <h2>Agents</h2>
      </Row>
      <Row>
        <Col xs={10}>
          <GraphVisualizer />
        </Col>
        <Col xs={2}>
          <AgentList />
        </Col>
      </Row>
    </>
  );
}

export default AgentDisplay;
