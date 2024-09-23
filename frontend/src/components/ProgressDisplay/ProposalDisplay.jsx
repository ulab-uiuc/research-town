import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";
import ReactMarkdown from "react-markdown";

function ProposalDisplay({ list }) {
  return (
    <>
      <Row className="mb-3">
        <Col>
          <h2>Proposal</h2>
        </Col>
      </Row>
      <Row>
        {list.map((item, index) => {
          return (
            <Card
              key={index}
              style={{ textAlign: "left", margin: "1em", padding: "1em" }}
            >
              <Card.Title style={{ textAlign: "center" }}></Card.Title>
              <Card.Body>
                {["q1", "q2", "q3", "q4", "q5"].map((q) => (
                  <div key={q}>
                    <div>
                      <ReactMarkdown>{q.toUpperCase() + item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </Card.Body>
            </Card>
          );
        })}
      </Row>
    </>
  );
}

export default ProposalDisplay;
