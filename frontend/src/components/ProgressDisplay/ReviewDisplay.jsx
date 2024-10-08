import React from "react";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";

function ReviewDisplay({ list }) {
  return (
    <>
      {/* <Row className="mb-3">
        <Col>
          <h2>Review</h2>
        </Col>
      </Row> */}
      <br />
      <Row>
        {list.map((item, index) => {
          return (
            <>
              {["summary", "strength", "weakness", "ethical_concern"].map(
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
