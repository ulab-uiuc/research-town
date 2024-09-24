import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ReactMarkdown from "react-markdown";
import Accordion from "react-bootstrap/Accordion";

function IdeaDisplay({ list }) {

    const agentName = list.length > 0 ? list[0].agent_name : "Agent";
    return (
        <>
        <Row className="mb-3">
            <Col>
            <h2>Ideas</h2>
            </Col>
        </Row>
        <Row>
            <Accordion>
            {list.map((item, index) => (
                <Accordion.Item key={index} eventKey="0">
                <Accordion.Header>
                    {item.type}#{index + 1} from {agentName}
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
