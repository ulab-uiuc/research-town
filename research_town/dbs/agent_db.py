from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class AgentProfile(BaseModel):
    agent_id: str
    name: Optional[str] = Field(default=None)
    profile: Optional[str] = Field(default=None)

class AgentProfileDB:
    def __init__(self):
        self.data: Dict[str, AgentProfile] = {}

    def add_agent(self, agent: AgentProfile) -> None:
        self.data[agent.agent_id] = agent

    def update_agent(self, agent_id: str, updates: Dict[str, Optional[str]]) -> bool:
        if agent_id in self.data:
            for key, value in updates.items():
                if value is not None:
                    setattr(self.data[agent_id], key, value)
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        return self.data.get(agent_id)

    def delete_agent(self, agent_id: str) -> bool:
        if agent_id in self.data:
            del self.data[agent_id]
            return True
        return False

    def query_agents(self, **conditions) -> List[AgentProfile]:
        result = []
        for agent in self.data.values():
            if all(getattr(agent, key) == value for key, value in conditions.items()):
                result.append(agent)
        return result

    def save_to_file(self, file_name: str) -> None:
        with open(file_name, "w") as f:
            json.dump({aid: agent.dict() for aid, agent in self.data.items()}, f, indent=2)

    def load_from_file(self, file_name: str) -> None:
        with open(file_name, "r") as f:
            data = json.load(f)
            self.data = {aid: AgentProfile(**agent_data) for aid, agent_data in data.items()}

    def update_kb(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        for date, agents in data.items():
            for agent_data in agents:
                agent = AgentProfile(**agent_data)
                self.add_agent(agent)