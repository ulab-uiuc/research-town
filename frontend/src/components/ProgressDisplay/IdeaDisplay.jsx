import React from "react";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";
import Accordion from "react-bootstrap/Accordion";

function IdeaDisplay({ list }) {
  console.log(list);
  return (
    <>
      <br />
      <Row>
        <Accordion>
          {list.map((item, index) => {
            return (
              <Accordion.Item key={index} eventKey={index.toString()}>
                <Accordion.Header>
                  {agentRole === "leader"
                    ? `Discussed idea from ${item.agent_domain} expert agent`
                    : `Idea from ${item.agent_domain} expert agent`}
                </Accordion.Header>
                <Accordion.Body style={{ textAlign: "left" }}>
                  <p>
                    <ReactMarkdown>{item.content}</ReactMarkdown>
                  </p>
                </Accordion.Body>
              </Accordion.Item>
            );
          })}
        </Accordion>
      </Row>
    </>
  );
}

export default IdeaDisplay;
