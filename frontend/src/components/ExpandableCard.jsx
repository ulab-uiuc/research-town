import React, { useState } from "react";
import { Card, Button, Collapse } from "react-bootstrap";

const ExpandableCard = ({ type, summary, content }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Card>
      <Card.Body>
        <Card.Title>{type}</Card.Title>
        <Card.Text>{summary}</Card.Text>
        <Button onClick={toggleExpand}>
          {isExpanded ? "Collapse" : "Expand"}
        </Button>
        <Collapse in={isExpanded}>
          <div>
            <Card.Text className="mt-3">{content}</Card.Text>
          </div>
        </Collapse>
      </Card.Body>
    </Card>
  );
};

export default ExpandableCard;
