import React from "react";
import ReactMarkdown from "react-markdown";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";

import ExpandableCard from "./ExpandableCard";
import GraphVisualizer from "./GraphVisualizer";
import ProgressVisualizer from "./ProgressVisualizer";

function OutputDisplay({ output }) {
  const insightsList = [
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
    { type: "Insight", summary: "Summary", content: "Content" },
  ];

  const ideaList = [
    { type: "Idea", idea: ["Idea", "Idea"] },
    { type: "Idea", idea: ["Idea", "Idea"] },
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
        <ProgressVisualizer />
        <Row className="mb-3">
          <Col>
            <h2>Agents</h2>
          </Col>
        </Row>
        <GraphVisualizer />
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
        <Row className="mb-3">
          <Col>
            <h2>Ideas</h2>
          </Col>
        </Row>
        <Row>
          {ideaList.map((idea, index) => (
            <Col xs={4}>
              <Card>
                <Card.Body>
                  <Card.Title>{idea.type}</Card.Title>
                  <Card.Text>{idea.idea}</Card.Text>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
    </div>
  );
}

export default OutputDisplay;
