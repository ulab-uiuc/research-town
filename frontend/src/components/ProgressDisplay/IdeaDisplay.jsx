import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Accordion from "react-bootstrap/Accordion";

function IdeaDisplay() {
  return (
    <>
      {" "}
      <Row className="mb-3">
        <Col>
          <h2>Ideas</h2>
        </Col>
      </Row>
      <Row>
        <Accordion>
          <Accordion.Item eventKey="0">
            <Accordion.Header>Idea #1</Accordion.Header>
            <Accordion.Body style={{ textAlign: "left" }}>
              <b>Application of GNNs to Multi-Table Databases</b>: Investigate
              the use of GNNs to model relationships in complex multi-table
              databases, developing specialized architectures to effectively
              capture the relational structure inherent in such databases.
            </Accordion.Body>
          </Accordion.Item>
          <Accordion.Item eventKey="1">
            <Accordion.Header>Idea #2</Accordion.Header>
            <Accordion.Body style={{ textAlign: "left" }}>
              <b>Hybrid Physics-Based Neural Networks</b>: Explore the
              integration of physical models, such as fluid dynamics or
              thermodynamics, into neural network architectures to create hybrid
              models that enhance interpretability and performance in
              applications like environmental modeling or material science.
            </Accordion.Body>
          </Accordion.Item>
        </Accordion>
      </Row>
    </>
  );
}

export default IdeaDisplay;
