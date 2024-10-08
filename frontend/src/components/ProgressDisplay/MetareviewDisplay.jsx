import React from "react";
import Row from "react-bootstrap/Row";
import ReactMarkdown from "react-markdown";

function MetareviewDisplay({ list }) {
  return (
    <>
      {/* <Row className="mb-3">
        <Col>
          <h2>Metareview</h2>
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
                <div className="sub-item-label">{"Decision"}:</div>
                <div className="sub-item-content">{item["decision"]}</div>
              </div>
            </>
          );
        })}
      </Row>
    </>
  );
}

export default MetareviewDisplay;
