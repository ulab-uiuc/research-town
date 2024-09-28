import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";
import Button from "react-bootstrap/Button";

function InputForm({ url, setUrl, handleSubmit }) {
  return (
    <Container fluid="md" style={{ maxWidth: "600px", margin: "40px auto", padding: "20px"}}>
      {/* Instruction message */}
      <Row>
        <Col>
          <div
            style={{
              backgroundColor: "#d1ecf1", // Light blue background
              padding: "15px",
              borderRadius: "10px",
              marginBottom: "20px",
              border: "1px solid #bee5eb", // A slightly darker border for contrast
              textAlign: "left", // Left-align the text
            }}
          >
            <h5 style={{ marginBottom: "10px" }}>Welcome to Research Town!</h5>
            <p style={{ marginBottom: "5px" }}>
              Enter a URL for a research paper to get started. 
              <br />
              <small>(e.g. https://arxiv.org/abs/1906.04817)</small>
            </p>
            <p style={{ marginBottom: "5px" }}>
              Expert LLM agents with different research domains will be matched to share insights, brainstorm ideas after reading the paper, and write a proposal to clarify a valuable idea.
            </p>
            <p>
              These proposals will be reviewed by other expert agents in the community and automatically improved.
            </p>
          </div>
        </Col>
      </Row>
      {/* Input field and submit button */}
      <Row>
        <Col xs={9}>
          <InputGroup className="mb-3">
            <Form.Control
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL for paper link"
              required
              style={{
                padding: "12px",
                fontSize: "16px",
                borderRadius: "5px",
              }}
            />
          </InputGroup>
        </Col>
        <Col xs={3}>
          <Button
            type="submit"
            onClick={handleSubmit}
            style={{ 
              width: "100%", 
              padding: "12px", 
              backgroundColor: "#007bff", 
              color: "#fff", 
              fontSize: "16px",
              borderRadius: "5px", 
            }}
          >
            Process
          </Button>
        </Col>
      </Row>
    </Container>
  );
}

export default InputForm;
