import os
import unittest
from unittest.mock import MagicMock, patch

from research_town.dbs.agent_db import AgentProfile, AgentProfileDB
from research_town.dbs.env_db import EnvLogDB, AgentPaperReviewLog, AgentPaperRebuttalLog, AgentPaperMetaReviewLog, AgentAgentDiscussionLog
from research_town.dbs.paper_db import PaperProfileDB, PaperProfile
from research_town.dbs.progress_db import ResearchProgressDB, ResearchIdea, ResearchPaperDraft


@patch("research_town.dbs.agent_db.AgentProfileDB.save_to_file")
@patch("research_town.dbs.agent_db.AgentProfileDB.load_from_file")
def test_agent_profile_db(mock_load_from_file, mock_save_to_file):
    db = AgentProfileDB()
    agent1 = AgentProfile(name="John Doe", bio="Researcher in AI", institute="AI Institute")
    agent2 = AgentProfile(name="Jane Smith", bio="Expert in NLP", institute="NLP Lab")
    db.add(agent1)
    db.add(agent2)
    
    agent3 = AgentProfile(name="Alice Johnson", bio="Data Scientist", institute="Data Lab")
    db.add(agent3)
    assert agent3.pk in db.data
    assert db.data[agent3.pk].name == "Alice Johnson"
    
    updates = {"bio": "Senior Researcher in AI"}
    success = db.update(agent1.pk, updates)
    assert success
    assert db.data[agent1.pk].bio == "Senior Researcher in AI"

    success = db.update("non-existing-pk", {"bio": "New Bio"})
    assert not success
    
    success = db.delete(agent1.pk)
    assert success
    assert agent1.pk not in db.data
    
    success = db.delete("non-existing-pk")
    assert not success
    
    results = db.get(name="Jane Smith")
    assert len(results) == 1
    assert results[0].name == "Jane Smith"
    
    file_name = "test_agents.json"
    db.save_to_file(file_name)
    mock_save_to_file.assert_called_once_with(file_name)
    
    new_db = AgentProfileDB() 
    new_db.load_from_file(file_name)
    mock_load_from_file.assert_called_once_with(file_name)
    
    new_data = {
        "2024-05-29": [
            {
                "pk": agent1.pk, 
                "name": "John Doe", 
                "bio": "Updated bio", 
                "collaborators": [], 
                "institute": "AI Institute"
            },
            {
                "pk": "new-pk", 
                "name": "New Agent", 
                "bio": "New agent bio", 
                "collaborators": [], 
                "institute": "New Institute"
            }
        ]
    }
    db.update_db(new_data)
    assert db.data[agent1.pk].bio == "Updated bio"
    assert "new-pk" in db.data
    assert db.data["new-pk"].name == "New Agent"

@patch("research_town.dbs.env_db.EnvLogDB.save_to_file")
@patch("research_town.dbs.env_db.EnvLogDB.load_from_file")  
def test_env_log_db(mock_load_from_file, mock_save_to_file):
    db = EnvLogDB()
    review_log = AgentPaperReviewLog(paper_pk="paper1", agent_pk="agent1", review_score=5, review_content="Good paper")
    rebuttal_log = AgentPaperRebuttalLog(paper_pk="paper1", agent_pk="agent1", rebuttal_content="I disagree with the review")
    meta_review_log = AgentPaperMetaReviewLog(paper_pk="paper1", agent_pk="agent1", decision=True, meta_review="Accept")
    discussion_log = AgentAgentDiscussionLog(agent_from_pk="agent1", agent_to_pk="agent2", message="Let's discuss this paper")
    
    db.add(review_log)
    db.add(rebuttal_log) 
    db.add(meta_review_log)
    db.add(discussion_log)
    
    new_log = AgentPaperReviewLog(paper_pk="paper2", agent_pk="agent2", review_score=4, review_content="Interesting paper")
    db.add(new_log)
    assert new_log.dict() in db.data["AgentPaperReviewLog"]
    
    results = db.get(AgentPaperReviewLog, paper_pk="paper1")
    assert len(results) == 1
    assert results[0].review_content == "Good paper"
    
    updates = {"review_score": 3, "review_content": "Decent paper"}
    updated_count = db.update(AgentPaperReviewLog, {"paper_pk": "paper1"}, updates)
    assert updated_count == 1
    updated_log = db.get(AgentPaperReviewLog, paper_pk="paper1")[0]
    assert updated_log.review_score == 3
    assert updated_log.review_content == "Decent paper"
    
    deleted_count = db.delete(AgentPaperReviewLog, paper_pk="paper1")
    assert deleted_count == 1
    results = db.get(AgentPaperReviewLog, paper_pk="paper1")
    assert len(results) == 0
    
    file_name = "test_env_logs.json"
    db.save_to_file(file_name)
    mock_save_to_file.assert_called_once_with(file_name)
        
    new_db = EnvLogDB()
    new_db.load_from_file(file_name)
    mock_load_from_file.assert_called_once_with(file_name)
    
    assert len(new_db.data["AgentPaperReviewLog"]) == 1
    assert len(new_db.data["AgentPaperRebuttalLog"]) == 1
    assert len(new_db.data["AgentPaperMetaReviewLog"]) == 1 
    assert len(new_db.data["AgentAgentDiscussionLog"]) == 1
    assert new_db.data["AgentPaperReviewLog"][0]["review_content"] == "Interesting paper"
    
@patch("research_town.dbs.paper_db.PaperProfileDB.save_to_file")  
@patch("research_town.dbs.paper_db.PaperProfileDB.load_from_file")
def test_paper_profile_db(mock_load_from_file, mock_save_to_file):
    db = PaperProfileDB()
    paper1 = PaperProfile(
        title="Sample Paper 1",
        abstract="This is the abstract for paper 1", 
        authors=["Author A", "Author B"],
        url="http://example.com/paper1",
        timestamp=1617181723,
        keywords=["AI", "ML"],
        domain="Computer Science",
        citation_count=10
    )
    paper2 = PaperProfile(
        title="Sample Paper 2",
        abstract="This is the abstract for paper 2",
        authors=["Author C"], 
        url="http://example.com/paper2",
        timestamp=1617181756, 
        keywords=["Quantum Computing"],
        domain="Physics",
        citation_count=5
    )
    db.add_paper(paper1)
    db.add_paper(paper2)
    
    new_paper = PaperProfile(
        title="Sample Paper 3",
        abstract="This is the abstract for paper 3",
        authors=["Author D"],
        url="http://example.com/paper3", 
        timestamp=1617181789,
        keywords=["Blockchain"],
        domain="Computer Science", 
        citation_count=2
    )
    db.add_paper(new_paper)
    assert new_paper.pk in db.data
    
    paper = db.get_paper(paper1.pk)
    assert paper is not None
    assert paper.title == "Sample Paper 1"
    
    updates = {"title": "Updated Sample Paper 1", "citation_count": 15}
    result = db.update_paper(paper1.pk, updates)
    assert result
    updated_paper = db.get_paper(paper1.pk)
    assert updated_paper.title == "Updated Sample Paper 1"
    assert updated_paper.citation_count == 15
    
    result = db.delete_paper(paper2.pk)
    assert result
    assert db.get_paper(paper2.pk) is None
    
    results = db.query_papers(domain="Computer Science")
    assert len(results) == 2
    assert results[0].title == "Updated Sample Paper 1"
    assert results[1].title == "Sample Paper 3"
    
    file_name = "test_paper_db.json"
    db.save_to_file(file_name)
    mock_save_to_file.assert_called_once_with(file_name)
    
    new_db = PaperProfileDB()
    new_db.load_from_file(file_name)  
    mock_load_from_file.assert_called_once_with(file_name)
    
    assert len(new_db.data) == 2
    assert paper1.pk in new_db.data
    assert new_db.data[paper1.pk].title == "Updated Sample Paper 1"
    
@patch("research_town.dbs.progress_db.ResearchProgressDB.save_to_file") 
@patch("research_town.dbs.progress_db.ResearchProgressDB.load_from_file")
def test_research_progress_db(mock_load_from_file, mock_save_to_file):  
    db = ResearchProgressDB()
    idea1 = ResearchIdea(content="Idea for a new AI algorithm")
    idea2 = ResearchIdea(content="Quantum computing research plan")
    paper1 = ResearchPaperDraft(
        title="Draft on AI", 
        abstract="This is the abstract for AI research paper."
    )
    db.add(idea1)
    db.add(idea2)
    db.add(paper1)
    
    new_idea = ResearchIdea(content="Blockchain research proposal")
    db.add(new_idea)
    assert new_idea.dict() in db.data["ResearchIdea"]
    
    new_paper = ResearchPaperDraft(
        title="Draft on Blockchain",
        abstract="This is the abstract for Blockchain research paper."
    )
    db.add(new_paper)
    assert new_paper.dict() in db.data["ResearchPaper"]

    results = db.get(ResearchIdea, content="Idea for a new AI algorithm")
    assert len(results) == 1
    assert results[0].content == "Idea for a new AI algorithm"

    results = db.get(ResearchPaperDraft, title="Draft on AI")
    assert len(results) == 1 
    assert results[0].title == "Draft on AI"

    updates = {"content": "Updated idea content"}
    updated_count = db.update(ResearchIdea, {"content": "Idea for a new AI algorithm"}, updates)
    assert updated_count == 1
    updated_results = db.get(ResearchIdea, content="Updated idea content")
    assert len(updated_results) == 1
    assert updated_results[0].content == "Updated idea content"

    updates = {"title": "Updated Draft on AI"} 
    updated_count = db.update(ResearchPaperDraft, {"title": "Draft on AI"}, updates)
    assert updated_count == 1
    updated_results = db.get(ResearchPaperDraft, title="Updated Draft on AI")
    assert len(updated_results) == 1
    assert updated_results[0].title == "Updated Draft on AI"

    deleted_count = db.delete(ResearchIdea, content="Quantum computing research plan")
    assert deleted_count == 1
    remaining_results = db.get(ResearchIdea, content="Quantum computing research plan")
    assert len(remaining_results) == 0

    deleted_count = db.delete(ResearchPaperDraft, title="Updated Draft on AI")
    assert deleted_count == 1 
    remaining_results = db.get(ResearchPaperDraft, title="Updated Draft on AI")
    assert len(remaining_results) == 0

    file_name = "test_research_db.json"
    db.save_to_file(file_name)
    mock_save_to_file.assert_called_once_with(file_name)
    
    new_db = ResearchProgressDB()
    new_db.load_from_file(file_name)
    mock_load_from_file.assert_called_once_with(file_name)
    
    assert len(new_db.data["ResearchIdea"]) == 2
    assert len(new_db.data["ResearchPaper"]) == 1
    assert idea1.dict() in new_db.data["ResearchIdea"]
    assert new_paper.dict() in new_db.data["ResearchPaper"]