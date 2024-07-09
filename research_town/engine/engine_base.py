from typing import List

from ..envs.env_base import BaseMultiAgentEnv


class BaseResearchEngine(object):
    def __init__(self) -> None:
        self.envs: List[BaseMultiAgentEnv] = []
