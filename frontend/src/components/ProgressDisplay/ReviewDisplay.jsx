import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import ReactMarkdown from "react-markdown";

function ReviewDisplay({ list }) {
  console.log("Review");
  console.log(list);
  return (
    <>
      <Row className="mb-3">
        <Col>
          <h2>Review</h2>
        </Col>
      </Row>
      <Row>
        {list.map((item, index) => {
          return (
            <>
              {["summary", "strength", "weakness", "ethical_concerns"].map(
                (field) => (
                  <div key={field} className="sub-item">
                    <div>
                      <b>{field.replace("_", " ").toUpperCase()}</b>
                    </div>
                    <div style={{ textAlign: "left" }}>
                      <ReactMarkdown>{item[field]}</ReactMarkdown>
                    </div>
                  </div>
                )
              )}
              <div className="sub-item">
                <div className="sub-item-label">{"Score"}:</div>
                <div className="sub-item-content">{item["score"]}</div>
              </div>
            </>
          );
        })}
      </Row>
    </>
  );
}

export default ReviewDisplay;
