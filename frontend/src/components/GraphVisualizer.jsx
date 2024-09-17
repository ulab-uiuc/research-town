import React from "react";
import { ForceGraph2D } from "react-force-graph";
import { Container, Row, Col } from "react-bootstrap";

// Define colors for different research fields
const fieldColors = {
  AI: "#1f77b4",
  ML: "#ff7f0e",
  NLP: "#2ca02c",
  CV: "#d62728",
};

// Custom function to draw links with different styles
const drawLink = (link, ctx) => {
  ctx.beginPath();
  ctx.moveTo(link.source.x, link.source.y);
  ctx.lineTo(link.target.x, link.target.y);

  // Set different styles for different types of relationships
  if (link.relation === "collaborated") {
    ctx.setLineDash([5, 5]); // Dashed line
  } else if (link.relation === "co-authored") {
    ctx.setLineDash([]); // Solid line
  } else if (link.relation === "cited") {
    ctx.setLineDash([1, 3]); // Dotted line
  }

  ctx.strokeStyle = "#999"; // Set the color of the line
  ctx.stroke();
};

// Custom function to draw nodes with colors based on field
const drawNode = (node, ctx, globalScale) => {
  const label = node.name;
  const fontSize = 12 / globalScale;
  ctx.font = `${fontSize}px Sans-Serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  // Draw the node circle
  ctx.fillStyle = fieldColors[node.field] || "#000"; // Fallback to black if field is undefined
  ctx.beginPath();
  ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI, false);
  ctx.fill();

  // Draw the label
  ctx.fillStyle = "#fff";
  ctx.fillText(label, node.x, node.y + 12); // Offset text slightly below the node
};

const GraphVisualizer = () => {
  const graphData = {
    nodes: [
      { id: "1", name: "Alice", field: "AI", institution: "University X" },
      { id: "2", name: "Bob", field: "ML", institution: "University Y" },
      { id: "3", name: "Charlie", field: "AI", institution: "University Z" },
      { id: "4", name: "Dana", field: "NLP", institution: "University X" },
      { id: "5", name: "Eve", field: "CV", institution: "University Y" },
    ],
    links: [
      { source: "1", target: "2", relation: "collaborated" },
      { source: "1", target: "3", relation: "co-authored" },
      { source: "2", target: "4", relation: "co-authored" },
      { source: "4", target: "5", relation: "cited" },
      { source: "3", target: "5", relation: "cited" },
    ],
  };

  return (
    <Container>
      <Row>
        <Col>
          <div
            style={{
              border: "2px solid #ccc",
              borderRadius: "10px",
              overflowY: "auto",
            }}
          >
            <ForceGraph2D
              graphData={graphData}
              nodeCanvasObject={(node, ctx, globalScale) =>
                drawNode(node, ctx, globalScale)
              }
              height={240}
              linkCanvasObject={(link, ctx) => drawLink(link, ctx)}
              linkDirectionalParticles={2} // Optional: particles to show direction of relationships
              enableNodeDrag={true} // Enable node dragging
            />
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default GraphVisualizer;
