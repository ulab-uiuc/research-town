import React from "react";
import Row from "react-bootstrap/Row";
import Card from "react-bootstrap/Card";
import ReactMarkdown from "react-markdown";

function ProposalDisplay({ list, revision }) {
  return (
    <>
      {/* <Row className="mb-3">
        <Col>
          <h2>Proposal</h2>
        </Col>
      </Row> */}
      <br />
      <Row>
        {revision.map((item, index) => {
          return (
            <Card
              key={index}
              style={{ textAlign: "left", margin: "1em", padding: "1em" }}
            >
              <Card.Title style={{ textAlign: "center" }}>
                <i>Revised Proposal</i>
              </Card.Title>
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
        {list.map((item, index) => {
          return (
            <Card
              key={index}
              style={{ textAlign: "left", margin: "1em", padding: "1em" }}
            >
              <Card.Title style={{ textAlign: "center" }}>
                <i>Initial Proposal</i>
              </Card.Title>
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
