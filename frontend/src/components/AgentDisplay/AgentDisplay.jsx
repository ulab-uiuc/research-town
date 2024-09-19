import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import AgentList from "./AgentList";
import GraphVisualizer from "./GraphVisualizer";

function AgentDisplay() {
  return (
    <>
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
