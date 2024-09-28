import React from "react";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";
import Accordion from "react-bootstrap/Accordion";

function IdeaDisplay({ list }) {
  return (
    <>
      {/* <Row className="mb-3">
        <Col>
          <h2>Ideas</h2>
        </Col>
      </Row> */}
      <br />
      <Row>
        <Accordion>
          {list.map((item, index) => (
            <Accordion.Item key={index} eventKey="0">
              <Accordion.Header>
                {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
                {index + 1} from {item.agent_domain} expert
              </Accordion.Header>
              <Accordion.Body style={{ textAlign: "left" }}>
                <p>
                  <ReactMarkdown>{item.content}</ReactMarkdown>
                </p>
              </Accordion.Body>
            </Accordion.Item>
          ))}
        </Accordion>
      </Row>
    </>
  );
}

export default IdeaDisplay;
