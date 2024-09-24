import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Card, Button, Collapse } from "react-bootstrap";

const ExpandableCard = ({ index, type, summary, content, name }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Card>
      <Card.Body>
        <Card.Title>#{index} {type} </Card.Title>
        <Card.Text>
          {summary} from {name}
        </Card.Text>
        <Button onClick={toggleExpand}>
          {isExpanded ? "Collapse" : "Expand"}
        </Button>
        <Collapse in={isExpanded}>
          <div style={{ textAlign: "left" }}>
            <Card.Text className="mt-3">
              <ReactMarkdown>{content}</ReactMarkdown>
            </Card.Text>
          </div>
        </Collapse>
      </Card.Body>
    </Card>
  );
};

export default ExpandableCard;
