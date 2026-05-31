from enum import Enum, auto

class EntityType(Enum):
    """Type of code entity."""
    MODULE = auto()
    PACKAGE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    VARIABLE = auto()
    CONSTANT = auto()
    INTERFACE = auto()
    ENUM = auto()
    DECORATOR = auto()
    TYPE_ALIAS = auto()
