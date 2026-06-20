from enum import Enum

class DecisionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REVERTED = "REVERTED"
    PROPOSED = "PROPOSED"
    DEPRECATED = "DEPRECATED"
