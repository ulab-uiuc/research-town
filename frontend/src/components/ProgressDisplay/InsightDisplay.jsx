import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

import ExpandableCard from "./ExpandableCard";

function InsightDisplay() {
  const insightsList = [
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
  ];
  return (
    <>
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
    </>
  );
}

export default InsightDisplay;
