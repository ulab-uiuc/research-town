from research_town.agents.agent_base import ResearchAgent
from research_town.agents.agent_role import Role
from research_town.utils.serializer import Serializer
from tests.constants.data_constants import agent_profile_A


def test_serializer() -> None:
    research_agent = ResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.LEADER,
    )
    research_agent_serialized = Serializer.serialize(research_agent)
    research_agent_deserialized = Serializer.deserialize(research_agent_serialized)
    research_agent_serialized_2 = Serializer.serialize(research_agent_deserialized)

    assert research_agent_serialized == research_agent_serialized_2
