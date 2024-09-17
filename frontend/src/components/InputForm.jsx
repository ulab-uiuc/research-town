import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

function InputForm({ url, setUrl, handleSubmit }) {
  return (
    <Container fluid="md">
      <Row>
        <Col xs={8}>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL"
            required
            style={{ width: "100%" }}
          />
        </Col>
        <Col xs={4}>
          <button
            type="submit"
            onClick={handleSubmit}
            style={{ width: "100%" }}
          >
            Process
          </button>
        </Col>
      </Row>
    </Container>
  );
}

export default InputForm;
