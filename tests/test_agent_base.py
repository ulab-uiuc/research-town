
from unittest.mock import MagicMock, patch

from research_town.agents.agent_base import BaseResearchAgent


@patch("research_town.utils.agent_prompting.openai_prompting")
def test_get_profile(mock_openai_prompting: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.return_value = ["I am a research agent who is interested in machine learning."]

    mock_openai_prompting.return_value = mock_response

    research_agent = BaseResearchAgent("Jiaxuan You")
    profile = research_agent.profile
    assert profile["name"] == "Jiaxuan You"
    assert "profile" in profile.keys()

'''
def test_generate_idea() -> None:
    research_agent = BaseResearchAgent("Jiaxuan You")
    ideas = research_agent.generate_idea({"2024-04": {"abstract": ["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]}})
    assert isinstance(ideas, list)
    assert len(ideas) > 0
'''

@patch("research_town.utils.agent_prompting.openai_prompting")
def test_communicate(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = ["I believe in the potential of using automous agents to simulate the current research pipeline."]

    research_agent = BaseResearchAgent("Jiaxuan You")
    response = research_agent.communicate({"Alice": "I believe in the potential of using automous agents to simulate the current research pipeline."})
    assert isinstance(response, str)
    assert response != ""

@patch("research_town.utils.agent_prompting.openai_prompting")
def test_write_paper_abstract(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = ["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]

    research_agent = BaseResearchAgent("Jiaxuan You")
    abstract = research_agent.write_paper(["We can simulate the scientific research pipeline with agents."], {"2024-04":{"abstract":["Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal communication to prototyping tools. In this paper, we introduce generative agents--computational software agents that simulate believable human behavior. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on days past as they plan the next day. To enable generative agents, we describe an architecture that extends a large language model to store a complete record of the agent's experiences using natural language, synthesize those memories over time into higher-level reflections, and retrieve them dynamically to plan behavior. We instantiate generative agents to populate an interactive sandbox environment inspired by The Sims, where end users can interact with a small town of twenty five agents using natural language. In an evaluation, these generative agents produce believable individual and emergent social behaviors: for example, starting with only a single user-specified notion that one agent wants to throw a Valentine's Day party, the agents autonomously spread invitations to the party over the next two days, make new acquaintances, ask each other out on dates to the party, and coordinate to show up for the party together at the right time. We demonstrate through ablation that the components of our agent architecture--observation, planning, and reflection--each contribute critically to the believability of agent behavior. By fusing large language models with computational, interactive agents, this work introduces architectural and interaction patterns for enabling believable simulations of human behavior. "]}})
    assert isinstance(abstract, str)
    assert abstract != ""

@patch("research_town.utils.agent_prompting.openai_prompting")
def test_read_paper(mock_openai_prompting: MagicMock) -> None:
    mock_openai_prompting.return_value = ["This is a paper"]

    external_data = {"2021-01-01": {"abstract": ["This is a paper"]}}
    domain = "machine learning"
    research_agent = BaseResearchAgent("Jiaxuan You")
    summary = research_agent.read_paper(external_data, domain)
    assert isinstance(summary, str)
