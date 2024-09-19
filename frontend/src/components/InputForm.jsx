import React from "react";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";
import Button from "react-bootstrap/Button";

function InputForm({ url, setUrl, handleSubmit }) {
  return (
    <Container fluid="md">
      <Row>
        <Col xs={10}>
          <InputGroup className="mb-3">
            <Form.Control
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL"
              required
            />
          </InputGroup>
        </Col>
        <Col xs={2}>
          <Button
            type="submit"
            onClick={handleSubmit}
            style={{ width: "100%" }}
          >
            Process
          </Button>
        </Col>
      </Row>
    </Container>
  );
}

export default InputForm;
