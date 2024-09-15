from research_town.agents import Agent, Role
from research_town.utils.serializer import Serializer
from tests.constants.data_constants import agent_profile_A


def test_serializer() -> None:
    agent = Agent(
        agent_profile=agent_profile_A,
        model_name='together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1',
        agent_role=Role.leader,
    )
    agent_serialized = Serializer.serialize(agent)
    agent_deserialized = Serializer.deserialize(agent_serialized)
    agent_serialized_2 = Serializer.serialize(agent_deserialized)

    assert agent_serialized == agent_serialized_2
