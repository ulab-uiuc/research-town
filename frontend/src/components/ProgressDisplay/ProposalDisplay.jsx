import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Card from "react-bootstrap/Card";

function ProposalDisplay() {
  return (
    <>
      <Row className="mb-3">
        <Col>
          <h2>Proposal</h2>
        </Col>
      </Row>
      <Row>
        <Card>
          <Card.Body style={{ textAlign: "left" }}>
            <b>What is the problem?</b> The increasing complexity of multi-table
            databases presents significant challenges in effectively modeling
            the intricate relationships among data entities. Traditional methods
            often fail to capture the relational structure inherent in these
            databases, leading to suboptimal performance in data retrieval and
            analysis tasks. This research aims to investigate the application of
            Graph Neural Networks (GNNs) to model these relationships,
            specifically focusing on developing specialized architectures that
            can effectively represent the relational dynamics. Given the
            exponential growth of data in various domains, understanding and
            leveraging these relationships is crucial for enhancing data-driven
            decision-making processes. How can GNNs be effectively utilized to
            model relationships in complex multi-table databases?
          </Card.Body>
        </Card>
      </Row>
    </>
  );
}

export default ProposalDisplay;
