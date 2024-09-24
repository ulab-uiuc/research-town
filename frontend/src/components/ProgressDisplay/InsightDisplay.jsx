import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import ExpandableCard from "./ExpandableCard";

function InsightDisplay({ list }) {

    const agentName = list.length > 0 ? list[0].agent_name : "Agent";

    return (
        <>
        <Row className="mb-3">
            <Col>
            <h2>Insights</h2>
            </Col>
        </Row>
        <Row>
            {list.map((insight, index) => (
            <Col xs={4}>
                <ExpandableCard
                key={index}
                index={index + 1}
                type={insight.type}
                summary={""}
                content={insight.content}
                name={agentName}
                />
            </Col>
            ))}
        </Row>
        </>
    );
}

export default InsightDisplay;
