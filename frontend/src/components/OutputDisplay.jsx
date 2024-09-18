import React from "react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Accordion from "react-bootstrap/Accordion";
import ListGroup from "react-bootstrap/ListGroup";
import Card from "react-bootstrap/Card";
import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

import ExpandableCard from "./ExpandableCard";
import GraphVisualizer from "./GraphVisualizer";
import ProgressVisualizer from "./ProgressVisualizer";

function OutputDisplay({ output }) {
  const [key, setKey] = useState("insights");
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const insightsList = [
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
  ];

  return (
    <div>
      {output.map((item, index) => {
        switch (item.type) {
          case "insight":
          case "idea":
          case "rebuttal":
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
          case "proposal":
            return (
              <div key={index} className="item-container">
                <div className="item-label">Proposal:</div>
                {["q1", "q2", "q3", "q4", "q5"].map((q) => (
                  <div key={q} className="sub-item">
                    <div className="sub-item-label">{q.toUpperCase()}:</div>
                    <div className="sub-item-content">
                      <ReactMarkdown>{item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
            );
          case "review":
          case "metareview":
            return (
              <div key={index} className="item-container">
                <div className="item-label">
                  {item.type.charAt(0).toUpperCase() + item.type.slice(1)}:
                </div>
                {["summary", "strength", "weakness", "ethical_concerns"].map(
                  (field) => (
                    <div key={field} className="sub-item">
                      <div className="sub-item-label">
                        {field.replace("_", " ").toUpperCase()}:
                      </div>
                      <div className="sub-item-content">
                        <ReactMarkdown>{item[field]}</ReactMarkdown>
                      </div>
                    </div>
                  )
                )}
                <div className="sub-item">
                  <div className="sub-item-label">
                    {item.type === "review" ? "Score" : "Decision"}:
                  </div>
                  <div className="sub-item-content">
                    {item[item.type === "review" ? "score" : "decision"]}
                  </div>
                </div>
              </div>
            );
          case "error":
            return (
              <div key={index} className="item-container">
                <p style={{ color: "red" }}>{item.content}</p>
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
      <Container>
        <ProgressVisualizer style={{ marginTop: "2em", marginBottom: "2em" }} />
        <Row className="mb-3" style={{ marginTop: "2em", marginBottom: "2em" }}>
          <h2>Agents</h2>
        </Row>
        <Row>
          <Col xs={10}>
            <GraphVisualizer />
          </Col>
          <Col xs={2}>
            <Card>
              <ListGroup variant="flush">
                <ListGroup.Item>
                  <Button variant="text" onClick={handleShow}>
                    Agent 1
                  </Button>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Button variant="text" onClick={handleShow}>
                    Agent 2
                  </Button>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Button variant="text" onClick={handleShow}>
                    Agent 3
                  </Button>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Button variant="text" onClick={handleShow}>
                    Agent 4
                  </Button>
                </ListGroup.Item>
                <ListGroup.Item>
                  <Button variant="text" onClick={handleShow}>
                    Agent 5
                  </Button>
                </ListGroup.Item>
              </ListGroup>
            </Card>
          </Col>
        </Row>
        <>
          <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Agent Information</Modal.Title>
            </Modal.Header>
            <Modal.Body>Agent Information</Modal.Body>
            <Modal.Footer>
              <Button variant="primary" onClick={handleClose}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </>
        <Tabs
          id="fill-tab-example"
          activeKey={key}
          fill
          onSelect={(k) => setKey(k)}
          className="mb-3"
          style={{ marginTop: "2em", marginBottom: "2em" }}
        >
          <Tab eventKey="insights" title="Insights">
            <Row className="mb-3">
              <Col>
                <h2>Insights</h2>
              </Col>
            </Row>
            <Row>
              {insightsList.map((insight, index) => (
                <Col xs={4}>
                  <ExpandableCard
                    key={index}
                    type={insight.type}
                    summary={insight.summary}
                    content={insight.content}
                  />
                </Col>
              ))}
            </Row>
          </Tab>
          <Tab eventKey="ideas" title="Ideas">
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
                    <b>Application of GNNs to Multi-Table Databases</b>:
                    Investigate the use of GNNs to model relationships in
                    complex multi-table databases, developing specialized
                    architectures to effectively capture the relational
                    structure inherent in such databases.
                  </Accordion.Body>
                </Accordion.Item>
                <Accordion.Item eventKey="1">
                  <Accordion.Header>Idea #2</Accordion.Header>
                  <Accordion.Body style={{ textAlign: "left" }}>
                    <b>Hybrid Physics-Based Neural Networks</b>: Explore the
                    integration of physical models, such as fluid dynamics or
                    thermodynamics, into neural network architectures to create
                    hybrid models that enhance interpretability and performance
                    in applications like environmental modeling or material
                    science.
                  </Accordion.Body>
                </Accordion.Item>
              </Accordion>
            </Row>
          </Tab>
          <Tab eventKey="proposal" title="Proposal">
            <Row className="mb-3">
              <Col>
                <h2>Proposal</h2>
              </Col>
            </Row>
            <Row>
              <Card>
                <Card.Body style={{ textAlign: "left" }}>
                  <b>What is the problem?</b> The increasing complexity of
                  multi-table databases presents significant challenges in
                  effectively modeling the intricate relationships among data
                  entities. Traditional methods often fail to capture the
                  relational structure inherent in these databases, leading to
                  suboptimal performance in data retrieval and analysis tasks.
                  This research aims to investigate the application of Graph
                  Neural Networks (GNNs) to model these relationships,
                  specifically focusing on developing specialized architectures
                  that can effectively represent the relational dynamics. Given
                  the exponential growth of data in various domains,
                  understanding and leveraging these relationships is crucial
                  for enhancing data-driven decision-making processes. How can
                  GNNs be effectively utilized to model relationships in complex
                  multi-table databases?
                </Card.Body>
              </Card>
            </Row>
          </Tab>
          <Tab eventKey="review" title="Review" disabled>
            Tab content for Contact
          </Tab>
          <Tab eventKey="rebuttal" title="Rebuttal" disabled>
            Tab content for Contact
          </Tab>
          <Tab eventKey="metareview" title="Metareview" disabled>
            Tab content for Contact
          </Tab>
        </Tabs>
      </Container>
    </div>
  );
}

export default OutputDisplay;
