from research_town.agent_base import BaseResearchAgent

def test_get_profile():
    research_agent = BaseResearchAgent("Jiaxuan You")
    profile = research_agent.get_profile()
    assert isinstance(profile, dict)