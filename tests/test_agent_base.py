from research_town.agent_base import BaseResearchAgent


def test_get_profile():
    research_agent = BaseResearchAgent("Jiaxuan You")
    profile = research_agent.profile
    assert profile["name"] == "Jiaxuan You"
    assert "profile" in profile.keys()


def test_communicate():
    pass

def test_read_paper():
    external_data = {"2021-01-01": {"abstract": ["This is a paper"]}}
    domain = "machine learning"
    research_agent = BaseResearchAgent("Jiaxuan You")
    summary = research_agent.read_paper(external_data, domain)
    assert isinstance(summary, str)
