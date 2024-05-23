import uuid

from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import BaseResearchAgent
from research_town.kbs.envlog import AgentAgentDiscussionLog, AgentPaperMetaReviewLog, AgentPaperRebuttalLog, AgentPaperReviewLog
from research_town.kbs.profile import PaperProfile, AgentProfile

from tests.utils import mock_papers, mock_prompting


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_get_profile(mock_openai_prompting: MagicMock) -> None:
    mock_prompting = MagicMock()
    mock_prompting.return_value = [
        "I am a research agent who is interested in machine learning."]

    mock_openai_prompting.return_value = mock_prompting

    research_agent = BaseResearchAgent("Jiaxuan You")
    profile = research_agent.profile
    assert profile["name"] == "Jiaxuan You"
    assert "profile" in profile.keys()


# =========================================================
# !IMPORTANT!
# patch should not add path that it comes from
# patch should add path that the function is used
# =========================================================
@patch("research_town.utils.agent_prompter.openai_prompting")
@patch("research_town.utils.agent_prompter.get_related_papers")
def test_generate_idea(
    mock_get_related_papers: MagicMock,
    mock_openai_prompting: MagicMock,
) -> None:

    # Configure the mocks
    mock_get_related_papers.side_effect = mock_papers
    mock_openai_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent("Jiaxuan You")
    ideas = research_agent.generate_idea({"2024-04": {"abstract": ["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]}}, domain="machine learning")

    assert isinstance(ideas, list)
    assert len(ideas) > 0


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_communicate(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "I believe in the potential of using automous agents to simulate the current research pipeline."]

    research_agent = BaseResearchAgent("Jiaxuan You")
    response = research_agent.communicate(
        {"Alice": "I believe in the potential of using automous agents to simulate the current research pipeline."})
    assert isinstance(response, str)
    assert response != ""


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_write_paper_abstract(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = ["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]

    research_agent = BaseResearchAgent("Jiaxuan You")
    abstract = research_agent.write_paper(["We can simulate the scientific research pipeline with agents."], {"2024-04": {"abstract": ["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]}})
    assert isinstance(abstract, str)
    assert abstract != ""

# =========================================================
# !IMPORTANT!
# patch should not add path that it comes from
# patch should add path that the function is used
# =========================================================


@patch("research_town.utils.agent_prompter.openai_prompting")
@patch("research_town.utils.agent_prompter.get_related_papers")
def test_read_paper(
    mock_get_related_papers: MagicMock,
    mock_openai_prompting: MagicMock,
) -> None:
    mock_get_related_papers.side_effect = mock_papers
    mock_openai_prompting.side_effect = mock_prompting

    papers = {"2021-01-01": {"abstract": ["This is a paper"]}}
    domain = "machine learning"
    research_agent = BaseResearchAgent("Jiaxuan You")
    summary = research_agent.read_paper(papers, domain)
    assert isinstance(summary, str)


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_find_collaborators(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "These are collaborators including Jure Leskovec, Rex Ying, Saining Xie, Kaiming He."]

    research_agent = BaseResearchAgent("Jiaxuan You")
    paper = PaperProfile()
    paper.paper_id = str(uuid.uuid4())
    paper.title = "Design Space for Graph Neural Networks"
    paper.abstract = "The rapid evolution of Graph Neural Networks (GNNs) has led to a growing number of new architectures as well as novel applications. However, current research focuses on proposing and evaluating specific architectural designs of GNNs, such as GCN, GIN, or GAT, as opposed to studying the more general design space of GNNs that consists of a Cartesian product of different design dimensions, such as the number of layers or the type of the aggregation function. Additionally, GNN designs are often specialized to a single task, yet few efforts have been made to understand how to quickly find the best GNN design for a novel task or a novel dataset. Here we define and systematically study the architectural design space for GNNs which consists of 315,000 different designs over 32 different predictive tasks."
    collaborators = research_agent.find_collaborators(
        paper=paper, parameter=0.5, max_number=3)
    assert isinstance(collaborators, list)
    assert len(collaborators) <= 3


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_make_review_decision(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "Accept. This is a good paper."]

    research_agent = BaseResearchAgent("Jiaxuan You")
    paper = PaperProfile()
    paper.paper_id = str(uuid.uuid4())
    paper.title = "MambaOut: Do We Really Need Mamba for Vision?"
    paper.abstract = "Mamba, an architecture with RNN-like token mixer of state space model (SSM), was recently introduced to address the quadratic complexity of the attention mechanism and subsequently applied to vision tasks. Nevertheless, the performance of Mamba for vision is often underwhelming when compared with convolutional and attention-based models. In this paper, we delve into the essence of Mamba, and conceptually conclude that Mamba is ideally suited for tasks with long-sequence and autoregressive characteristics. For vision tasks, as image classification does not align with either characteristic, we hypothesize that Mamba is not necessary for this task; Detection and segmentation tasks are also not autoregressive, yet they adhere to the long-sequence characteristic, so we believe it is still worthwhile to explore Mamba's potential for these tasks. To empirically verify our hypotheses, we construct a series of models named \\emph{MambaOut} through stacking Mamba blocks while removing their core token mixer, SSM. Experimental results strongly support our hypotheses. Specifically, our MambaOut model surpasses all visual Mamba models on ImageNet image classification, indicating that Mamba is indeed unnecessary for this task. As for detection and segmentation, MambaOut cannot match the performance of state-of-the-art visual Mamba models, demonstrating the potential of Mamba for long-sequence visual tasks."
    review = research_agent.review_paper(paper=paper)
    decision = research_agent.make_review_decision(
        paper=paper, review=[review])
    assert len(decision.decision) > 0
    assert decision.meta_review == "Accept. This is a good paper."


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_review_paper(mock_openai_prompting: MagicMock) -> None:

    mock_openai_prompting.side_effect = mock_prompting

    research_agent = BaseResearchAgent("Jiaxuan You")
    paper = PaperProfile()
    paper.paper_id = str(uuid.uuid4())
    paper.title = "MambaOut: Do We Really Need Mamba for Vision?"
    paper.abstract = "Mamba, an architecture with RNN-like token mixer of state space model (SSM), was recently introduced to address the quadratic complexity of the attention mechanism and subsequently applied to vision tasks. Nevertheless, the performance of Mamba for vision is often underwhelming when compared with convolutional and attention-based models. In this paper, we delve into the essence of Mamba, and conceptually conclude that Mamba is ideally suited for tasks with long-sequence and autoregressive characteristics. For vision tasks, as image classification does not align with either characteristic, we hypothesize that Mamba is not necessary for this task; Detection and segmentation tasks are also not autoregressive, yet they adhere to the long-sequence characteristic, so we believe it is still worthwhile to explore Mamba's potential for these tasks. To empirically verify our hypotheses, we construct a series of models named \\emph{MambaOut} through stacking Mamba blocks while removing their core token mixer, SSM. Experimental results strongly support our hypotheses. Specifically, our MambaOut model surpasses all visual Mamba models on ImageNet image classification, indicating that Mamba is indeed unnecessary for this task. As for detection and segmentation, MambaOut cannot match the performance of state-of-the-art visual Mamba models, demonstrating the potential of Mamba for long-sequence visual tasks."
    review = research_agent.review_paper(paper=paper)
    assert review.review_score == 2
    assert review.review_content == "This is a paper review for MambaOut."


@patch("research_town.utils.agent_prompter.openai_prompting")
def test_rebut_review(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = [
        "This is a paper rebuttal."]

    research_agent = BaseResearchAgent("Jiaxuan You")
    paper = PaperProfile()
    paper.paper_id = str(uuid.uuid4())
    paper.title = "Design Space for Graph Neural Networks"
    paper.abstract = "The rapid evolution of Graph Neural Networks (GNNs) has led to a growing number of new architectures as well as novel applications. However, current research focuses on proposing and evaluating specific architectural designs of GNNs, such as GCN, GIN, or GAT, as opposed to studying the more general design space of GNNs that consists of a Cartesian product of different design dimensions, such as the number of layers or the type of the aggregation function. Additionally, GNN designs are often specialized to a single task, yet few efforts have been made to understand how to quickly find the best GNN design for a novel task or a novel dataset. Here we define and systematically study the architectural design space for GNNs which consists of 315,000 different designs over 32 different predictive tasks."
    review = research_agent.review_paper(paper=paper)
    decision = research_agent.make_review_decision(
        paper=paper, review=[review])
    rebuttal = research_agent.rebut_review(
        paper=paper, review=[review], decision=[decision])
    assert isinstance(rebuttal, AgentPaperRebuttalLog)
    assert len(rebuttal.rebuttal_content) > 0
    assert rebuttal.rebuttal_content == "This is a paper rebuttal."
