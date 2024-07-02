from research_town.agents.agent_base import BaseResearchAgent
from research_town.utils.serializer import Serializer
from tests.db_constants import agent_profile_A


def test_serializer() -> None:
    research_agent = BaseResearchAgent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
    )
    research_agent_serialized = Serializer.serialize(research_agent)
    research_agent_deserialized = Serializer.deserialize(research_agent_serialized)
    research_agent_serialized_2 = Serializer.serialize(research_agent_deserialized)

    assert research_agent_serialized == research_agent_serialized_2
