from enum import Enum


class Role(Enum):
    LEADER = 'leader'
    MEMBER = 'member'
    REVIEWER = 'reviewer'
    CHAIR = 'chair'
