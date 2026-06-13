from enum import Enum, auto

class RelationshipType(Enum):
    """Type of relationship between code entities."""
    CALLS = auto()
    IMPORTS = auto()
    DEPENDS_ON = auto()
    BELONGS_TO = auto()
    EXTENDS = auto()
    IMPLEMENTS = auto()
    READS = auto()
    WRITES = auto()
    USES = auto()
    TESTS = auto()
    DECORATES = auto()
    CONTAINS = auto()
    DECLARES = auto()

    # Phase 5B Distributed & Messaging Relationships
    PASSES_STATE_TO = auto()
    INJECTED_INTO = auto()
    PUBLISHES_EVENT_TO = auto()
    TRIGGERS = auto()
    CALLS_ENDPOINT = auto()
    PUBLISHES_TO_TOPIC = auto()
    CONSUMES_FROM_TOPIC = auto()
    BELONGS_TO_GROUP = auto()

    # Phase 5B Frontend Relationships
    USES_HOOK = auto()
    NAVIGATES_TO = auto()
    DISPATCHES_ACTION = auto()

    # Phase 5B AI-Native Relationships
    USES_TOOL = auto()
    CALLS_MODEL = auto()
    ROUTES_TO_AGENT = auto()
    RETRIEVES_CONTEXT = auto()
    WRITES_MEMORY = auto()
    READS_MEMORY = auto()
    EVALUATES_OUTPUT = auto()
    REFLECTS_ON_RESULT = auto()

    # Phase 5.6 Semantic & Configuration Relationships
    EXPORTS = auto()
    DEPLOYS = auto()
    EXPOSES = auto()
    CONNECTS_TO = auto()
    USES_DATABASE = auto()
