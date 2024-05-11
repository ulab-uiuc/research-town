from research_town.agents.agent_base import BaseResearchAgent


def test_get_profile():
    research_agent = BaseResearchAgent("Jiaxuan You")
    profile = research_agent.profile
    assert profile["name"] == "Jiaxuan You"
    assert "profile" in profile.keys()


def test_communicate():
    research_agent = BaseResearchAgent("Jiaxuan You")
    response = research_agent.communicate({"Alice": "I believe in the potential of using automous agents to simulate the current research pipeline."})
    assert isinstance(response, str)
    assert response != ""

'''
def test_read_paper():
    external_data = {"2021-01-01": {"abstract": ["This is a paper"]}}
    domain = "machine learning"
    research_agent = BaseResearchAgent("Jiaxuan You")
    summary = research_agent.read_paper(external_data, domain)
    assert isinstance(summary, str)
'''
