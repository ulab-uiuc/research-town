import React from "react";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";

function RebuttalDisplay({ list }) {
  return (
    <>
      {/* <Row className="mb-3">
        <Col>
          <h2>Rebuttal</h2>
        </Col>
      </Row> */}
      <br />
      <Row>
        {list.map((item, index) => {
          return (
            <div style={{ textAlign: "left" }}>
              <ReactMarkdown>{item.content}</ReactMarkdown>
            </div>
          );
        })}
      </Row>
    </>
  );
}

export default RebuttalDisplay;
