from typing import List, Tuple, Dict


class BaseMultiAgentEnvironment(object):
    def __init__(self, agent_dict: Dict[str, str]) -> None:
        self.agent_dict = agent_dict

    def step(self):
        raise NotImplementedError