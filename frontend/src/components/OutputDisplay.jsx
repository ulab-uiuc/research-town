import React from "react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
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
  return (
    <div>
      {output.map((item, index) => {
        switch (item.type) {
          case "insight":
          case "idea":
          case "rebuttal":
            return (
              <div key={index} className="item-container">
                <div className="item-label">
                  {item.type.charAt(0).toUpperCase() + item.type.slice(1)}:
                </div>
                <div className="item-content">
                  <ReactMarkdown>{item.content}</ReactMarkdown>
                </div>
              </div>
            );
          case "proposal":
            return (
              <div key={index} className="item-container">
                <div className="item-label">Proposal:</div>
                {["q1", "q2", "q3", "q4", "q5"].map((q) => (
                  <div key={q} className="sub-item">
                    <div className="sub-item-label">{q.toUpperCase()}:</div>
                    <div className="sub-item-content">
                      <ReactMarkdown>{item[q]}</ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
            );
          case "review":
          case "metareview":
            return (
              <div key={index} className="item-container">
                <div className="item-label">
                  {item.type.charAt(0).toUpperCase() + item.type.slice(1)}:
                </div>
                {["summary", "strength", "weakness", "ethical_concerns"].map(
                  (field) => (
                    <div key={field} className="sub-item">
                      <div className="sub-item-label">
                        {field.replace("_", " ").toUpperCase()}:
                      </div>
                      <div className="sub-item-content">
                        <ReactMarkdown>{item[field]}</ReactMarkdown>
                      </div>
                    </div>
                  )
                )}
                <div className="sub-item">
                  <div className="sub-item-label">
                    {item.type === "review" ? "Score" : "Decision"}:
                  </div>
                  <div className="sub-item-content">
                    {item[item.type === "review" ? "score" : "decision"]}
                  </div>
                </div>
              </div>
            );
          case "error":
            return (
              <div key={index} className="item-container">
                <p style={{ color: "red" }}>{item.content}</p>
              </div>
            );
          default:
            return (
              <div key={index} className="item-container">
                <p>Unknown item type.</p>
              </div>
            );
        }
      })}
      <Container>
        {/* <ProgressVisualizer style={{ marginTop: "2em", marginBottom: "2em" }} /> */}
        <AgentDisplay />
        <Tabs
          id="fill-tab-example"
          activeKey={key}
          fill
          onSelect={(k) => setKey(k)}
          className="mb-3"
          style={{ marginTop: "2em", marginBottom: "2em" }}
        >
          <Tab eventKey="insights" title="Insights">
            <InsightDisplay />
          </Tab>
          <Tab eventKey="ideas" title="Ideas">
            <IdeaDisplay />
          </Tab>
          <Tab eventKey="proposal" title="Proposal">
            <ProposalDisplay />
          </Tab>
          <Tab eventKey="review" title="Review">
            <ReviewDisplay />
          </Tab>
          <Tab eventKey="rebuttal" title="Rebuttal">
            <RebuttalDisplay />
          </Tab>
          <Tab eventKey="metareview" title="Metareview">
            <MetareviewDisplay />
          </Tab>
        </Tabs>
      </Container>
    </div>
  );
}

export default OutputDisplay;
