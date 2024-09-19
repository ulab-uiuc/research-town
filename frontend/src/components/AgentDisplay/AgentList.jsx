import React from "react";
import { useState } from "react";
import Card from "react-bootstrap/Card";
import ListGroup from "react-bootstrap/ListGroup";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

function AgentList() {
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <Card>
      <>
        <Modal show={show} onHide={handleClose}>
          <Modal.Header closeButton>
            <Modal.Title>Agent Information</Modal.Title>
          </Modal.Header>
          <Modal.Body>Agent Information</Modal.Body>
          <Modal.Footer>
            <Button variant="primary" onClick={handleClose}>
              Close
            </Button>
          </Modal.Footer>
        </Modal>
      </>
      <ListGroup variant="flush">
        <ListGroup.Item>
          <Button variant="text" onClick={handleShow}>
            Agent 1
          </Button>
        </ListGroup.Item>
        <ListGroup.Item>
          <Button variant="text" onClick={handleShow}>
            Agent 2
          </Button>
        </ListGroup.Item>
        <ListGroup.Item>
          <Button variant="text" onClick={handleShow}>
            Agent 3
          </Button>
        </ListGroup.Item>
      </ListGroup>
    </Card>
  );
}

export default AgentList;
