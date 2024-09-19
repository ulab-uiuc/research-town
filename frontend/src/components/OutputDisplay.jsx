import React from "react";
import { useState, useMemo, useEffect } from "react";
import Container from "react-bootstrap/Container";

import Tab from "react-bootstrap/Tab";
import Tabs from "react-bootstrap/Tabs";

// import ProgressVisualizer from "./ProgressVisualizer";
import IdeaDisplay from "./ProgressDisplay/IdeaDisplay";
import InsightDisplay from "./ProgressDisplay/InsightDisplay";
import ProposalDisplay from "./ProgressDisplay/ProposalDisplay";
import ReviewDisplay from "./ProgressDisplay/ReviewDisplay";
import RebuttalDisplay from "./ProgressDisplay/RebuttalDisplay";
import MetareviewDisplay from "./ProgressDisplay/MetareviewDisplay";
import AgentDisplay from "./AgentDisplay/AgentDisplay";

function OutputDisplay({ output }) {
  const [key, setKey] = useState("insights");

  useEffect(() => {
    if (output && output.length > 0) {
      setKey(output[output.length - 1].type);
    }
  }, [output]);

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

  return (
    <div>
      <Container>
        {/* <ProgressVisualizer style={{ marginTop: "2em", marginBottom: "2em" }} /> */}
        {output.length !== 0 ? (
          <div style={{ minHeight: "24em" }}>
            {" "}
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
                <ProposalDisplay list={proposalList} />
              </Tab>
              <Tab
                eventKey="review"
                title="Review"
                disabled={reviewList.length === 0}
              >
                <ReviewDisplay list={reviewList} />
              </Tab>
              <Tab
                eventKey="rebuttal"
                title="Rebuttal"
                disabled={rebuttalList.length === 0}
              >
                <RebuttalDisplay list={rebuttalList} />
              </Tab>
              <Tab
                eventKey="metareview"
                title="Metareview"
                disabled={metareviewList.length === 0}
              >
                <MetareviewDisplay list={metareviewList} />
              </Tab>
            </Tabs>
          </div>
        ) : (
          <></>
        )}

        <AgentDisplay />
      </Container>
    </div>
  );
}

export default OutputDisplay;
