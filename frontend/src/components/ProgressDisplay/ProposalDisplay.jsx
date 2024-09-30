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
            <Card.Title style={{
                textAlign: "center",
                fontStyle: "italic",
                fontWeight: "bold",
                color: "#007bff",
                fontSize: "2.5rem",
                marginBottom: "1.5em",
                padding: "0.5em",
                letterSpacing: "1px",
                textShadow: "1px 1px 2px rgba(0, 0, 0, 0.1)",
                textTransform: "uppercase"
              }}>
                <i>Revised Proposal</i>
              </Card.Title>
              {/* <Card.Body>
                {["q1", "q2", "q3", "q4", "q5"].map((q) => (
                  <div key={q}>
                    <div>
                      <ReactMarkdown>{q.toUpperCase() + item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </Card.Body> */}
              <Card.Body>
                {[
                    { key: "q1", title: "What is the problem?" },
                    { key: "q2", title: "Why is it interesting and important?" },
                    { key: "q3", title: "Why is it hard?" },
                    { key: "q4", title: "Why hasn't it been solved before?" },
                    { key: "q5", title: "What are the key components of my approach and results?" }
                  ].map(({ key, title }) => (
                    <div key={key} style={{ marginBottom: "1.5em" }}>
                    <h5 style={{ fontWeight: "bold", marginBottom: "0.5em" }}>
                      {title} {/* Render the full question title */}
                    </h5>
                    <div style={{ paddingLeft: "1em", borderLeft: "3px solid #007bff" }}>
                      {/* Remove the leading colon, spaces, and repeated question from the content */}
                      <ReactMarkdown>{item[key]?.replace(/:\s*[^:]*?\n/, '')}</ReactMarkdown>
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
            <Card.Title style={{
                textAlign: "center",
                fontStyle: "italic",
                fontWeight: "bold",
                color: "#007bff",
                fontSize: "2.5rem",
                marginBottom: "1.5em",
                padding: "0.5em",
                letterSpacing: "1px",
                textShadow: "1px 1px 2px rgba(0, 0, 0, 0.1)",
                textTransform: "uppercase"
              }}>
                Initial Proposal
              </Card.Title>
              {/* <Card.Body>
                {["q1", "q2", "q3", "q4", "q5"].map((q) => (
                  <div key={q}>
                    <div>
                      <ReactMarkdown>{q.toUpperCase() + item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </Card.Body> */}
              <Card.Body>
                {[
                    { key: "q1", title: "What is the problem?" },
                    { key: "q2", title: "Why is it interesting and important?" },
                    { key: "q3", title: "Why is it hard?" },
                    { key: "q4", title: "Why hasn't it been solved before?" },
                    { key: "q5", title: "What are the key components of my approach and results?" }
                  ].map(({key, title}) => (
                    <div key={key} style={{ marginBottom: "1.5em" }}>
                    <h5 style={{ fontWeight: "bold", marginBottom: "0.5em" }}>
                      {title} {/* Render the full question title */}
                    </h5>
                    <div style={{ paddingLeft: "1em", borderLeft: "3px solid #007bff" }}>
                      {/* Remove the leading colon, spaces, and repeated question from the content */}
                      <ReactMarkdown>{item[key]?.replace(/:\s*[^:]*?\n/, '')}</ReactMarkdown>
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
