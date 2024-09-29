from research_town.agents.agent import Agent
from research_town.data import Role
from research_town.utils.serializer import Serializer
from tests.constants.data_constants import profile_A


def test_serializer() -> None:
    agent = Agent(
        profile=profile_A,
        model_name='gpt-4o-mini',
        role=Role.LEADER,
    )
    agent_serialized = Serializer.serialize(agent)
    agent_deserialized = Serializer.deserialize(agent_serialized)
    agent_serialized_2 = Serializer.serialize(agent_deserialized)

    assert agent_serialized == agent_serialized_2
