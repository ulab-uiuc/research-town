import React from "react";
import { useState, useMemo, useEffect } from "react";
import Container from "react-bootstrap/Container";
import Alert from "react-bootstrap/Alert"; // Import Alert for error handling

import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";

import IdeaDisplay from "./ProgressDisplay/IdeaDisplay";
import InsightDisplay from "./ProgressDisplay/InsightDisplay";
import ProposalDisplay from "./ProgressDisplay/ProposalDisplay";
import ReviewDisplay from "./ProgressDisplay/ReviewDisplay";
import RebuttalDisplay from "./ProgressDisplay/RebuttalDisplay";
import MetareviewDisplay from "./ProgressDisplay/MetareviewDisplay";

function OutputDisplay({ output }) {
  const [key, setKey] = useState("insights");

  useEffect(() => {
    if (output && output.length > 0) {
      if (output[output.length - 1].type === "rebuttal") setKey("proposal");
      else setKey(output[output.length - 1].type);
    }
  }, [output]);

  // Filter lists by type
  var insightList = useMemo(
    () => output.filter((item) => item.type === "insight"),
    [output]
  );
  var ideaList = useMemo(
    () => output.filter((item) => item.type === "idea"),
    [output]
  );
  var proposalList = useMemo(
    () => output.filter((item) => item.type === "proposal"),
    [output]
  );
  var reviewList = useMemo(
    () => output.filter((item) => item.type === "review"),
    [output]
  );
  var rebuttalList = useMemo(
    () => output.filter((item) => item.type === "rebuttal"),
    [output]
  );
  var metareviewList = useMemo(
    () => output.filter((item) => item.type === "metareview"),
    [output]
  );

  var errorList = useMemo(
    () => output.filter((item) => item.type === "error"),
    [output]
  );

  return (
    <div>
      <Container>
        {errorList.length > 0 ? (
          <div style={{ marginTop: "2em", marginBottom: "2em" }}>
            {errorList.map((errorItem, index) => (
              <Alert key={index} variant="danger">
                {errorItem.content || "An unknown error occurred."}
              </Alert>
            ))}
          </div>
        ) : (
          output.length !== 0 && (
            <div style={{ minHeight: "24em" }}>
              <Tabs
                id="fill-tab-example"
                variant="pills"
                activeKey={key}
                fill
                onSelect={(k) => setKey(k)}
                className="mb-3"
                style={{ marginTop: "2em", marginBottom: "2em" }}
              >
                <Tab
                  eventKey="insight"
                  title="Insights"
                  disabled={insightList.length === 0}
                >
                  <InsightDisplay list={insightList} />
                </Tab>
                <Tab
                  eventKey="idea"
                  title="Ideas"
                  disabled={ideaList.length === 0}
                >
                  <IdeaDisplay list={ideaList} />
                </Tab>
                <Tab
                  eventKey="proposal"
                  title="Proposal"
                  disabled={proposalList.length === 0}
                >
                  <ProposalDisplay
                    list={proposalList}
                    revision={rebuttalList}
                  />
                </Tab>
                <Tab
                  eventKey="review"
                  title="Review"
                  disabled={reviewList.length === 0}
                >
                  <ReviewDisplay list={reviewList} />
                </Tab>
                {/* <Tab
                  eventKey="rebuttal"
                  title="Rebuttal"
                  disabled={rebuttalList.length === 0}
                >
                  <RebuttalDisplay list={rebuttalList} />
                </Tab> */}
                <Tab
                  eventKey="metareview"
                  title="Metareview"
                  disabled={metareviewList.length === 0}
                >
                  <MetareviewDisplay list={metareviewList} />
                </Tab>
              </Tabs>
            </div>
          )
        )}
      </Container>
    </div>
  );
}

export default OutputDisplay;
