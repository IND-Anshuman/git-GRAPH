"""Registry for canonical behaviors, families, and language mappings."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BehaviorFamily:
    """Represents a category grouping multiple related canonical behaviors."""

    id: str
    name: str
    parent_concept_id: str
    description: str


@dataclass
class BehaviorMappingRule:
    """Language-specific indicators mapping to a canonical behavior."""

    language: str
    imports: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)
    heuristics: dict = field(default_factory=dict)


@dataclass
class CanonicalBehaviorDefinition:
    """Normalized action definition with language-specific rules."""

    id: str
    name: str
    family_id: str
    description: str
    mappings: List[BehaviorMappingRule] = field(default_factory=list)


class CanonicalRegistry:
    """In-memory registry for canonical behaviors and families."""

    def __init__(self) -> None:
        self._families: Dict[str, BehaviorFamily] = {}
        self._behaviors: Dict[str, CanonicalBehaviorDefinition] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        # Seed secure hashing family
        self.register_family(BehaviorFamily(
            id="secure_hashing",
            name="Secure Hashing Family",
            parent_concept_id="security.authentication",
            description="Cryptographic hash checks and validation algorithms."
        ))
        
        self.register_family(BehaviorFamily(
            id="web_routing",
            name="Web Routing and Handlers",
            parent_concept_id="web.api",
            description="Web frameworks routing and endpoint handlers."
        ))
        
        self.register_family(BehaviorFamily(
            id="messaging",
            name="Distributed Messaging",
            parent_concept_id="distributed.messaging",
            description="Message queue, mediator, and event dispatch systems."
        ))

        self.register_family(BehaviorFamily(
            id="state_management",
            name="Frontend State Management",
            parent_concept_id="frontend.state",
            description="Client-side state management frameworks."
        ))

        self.register_family(BehaviorFamily(
            id="ai_agentic",
            name="AI Agentic Workflows",
            parent_concept_id="ai.agentic",
            description="AI orchestrators, agents, and LLM providers."
        ))

        self.register_family(BehaviorFamily(
            id="infrastructure",
            name="Infrastructure and Containers",
            parent_concept_id="devops.infra",
            description="Infrastructure-as-code and container configuration."
        ))

        # Seed password verification behavior
        self.register_behavior(CanonicalBehaviorDefinition(
            id="auth_password_verification",
            name="Password Cryptographic Verification",
            family_id="secure_hashing",
            description="Verifies user-supplied credentials against secure cryptographic hashes.",
            mappings=[
                BehaviorMappingRule("python", ["bcrypt"], ["bcrypt.checkpw"], {}),
                BehaviorMappingRule("java", ["org.springframework.security.crypto.password.PasswordEncoder"], ["PasswordEncoder.matches"], {}),
                BehaviorMappingRule("csharp", ["Microsoft.AspNetCore.Identity.PasswordHasher"], ["PasswordHasher.VerifyHashedPassword"], {}),
                BehaviorMappingRule("rust", ["argon2"], ["argon2.verify"], {})
            ]
        ))

        self.register_behavior(CanonicalBehaviorDefinition(
            id="web_request_handler",
            name="Web Request Handler",
            family_id="web_routing",
            description="HTTP routes for routing web endpoint requests.",
            mappings=[
                BehaviorMappingRule("python", ["fastapi", "flask"], ["get", "post", "route"], {}),
                BehaviorMappingRule("java", ["org.springframework.web.bind.annotation"], ["GetMapping", "PostMapping", "RequestMapping"], {}),
                BehaviorMappingRule("csharp", ["Microsoft.AspNetCore.Mvc"], ["HttpGet", "HttpPost", "Route"], {}),
                BehaviorMappingRule("javascript", ["express", "next"], ["get", "post", "router"], {})
            ]
        ))

        self.register_behavior(CanonicalBehaviorDefinition(
            id="event_mediator_dispatch",
            name="Event Mediator Dispatch",
            family_id="messaging",
            description="Publishes or sends messages to distributed handlers or mediator queues.",
            mappings=[
                BehaviorMappingRule("csharp", ["MediatR", "MassTransit"], ["IMediator.Send", "IPublishEndpoint.Publish"], {}),
                BehaviorMappingRule("python", ["celery", "confluent_kafka"], ["delay", "produce"], {}),
                BehaviorMappingRule("java", ["org.springframework.kafka", "org.springframework.amqp"], ["KafkaTemplate.send", "RabbitTemplate.convertAndSend"], {})
            ]
        ))

        self.register_behavior(CanonicalBehaviorDefinition(
            id="client_state_update",
            name="Client State Update",
            family_id="state_management",
            description="Manages frontend browser/client application states.",
            mappings=[
                BehaviorMappingRule("javascript", ["react", "redux", "zustand"], ["useState", "dispatch", "createStore", "useStore"], {}),
                BehaviorMappingRule("typescript", ["react", "redux", "zustand"], ["useState", "dispatch", "createStore", "useStore"], {})
            ]
        ))

        self.register_behavior(CanonicalBehaviorDefinition(
            id="llm_agent_execution",
            name="LLM Agentic Execution",
            family_id="ai_agentic",
            description="Invokes LLMs, triggers prompt completions, or executes agent workflows.",
            mappings=[
                BehaviorMappingRule("python", ["openai", "anthropic", "crewai", "autogen", "langgraph"], ["chat.completions.create", "messages.create", "Crew.kickoff", "ConversableAgent.initiate_chat", "StateGraph.compile"], {})
            ]
        ))

        self.register_behavior(CanonicalBehaviorDefinition(
            id="infrastructure_provisioning",
            name="Infrastructure Provisioning",
            family_id="infrastructure",
            description="Provisions devops environments or configures container runtimes.",
            mappings=[
                BehaviorMappingRule("terraform", ["provider", "resource", "module"], [], {}),
                BehaviorMappingRule("docker", ["FROM", "RUN", "EXPOSE", "ENV"], [], {})
            ]
        ))

    def register_family(self, family: BehaviorFamily) -> None:
        """Register a new behavior family."""
        self._families[family.id] = family

    def register_behavior(self, behavior: CanonicalBehaviorDefinition) -> None:
        """Register a new canonical behavior definition."""
        self._behaviors[behavior.id] = behavior

    def get_behavior(self, behavior_id: str) -> Optional[CanonicalBehaviorDefinition]:
        """Look up a behavior by ID."""
        return self._behaviors.get(behavior_id)

    def get_family(self, family_id: str) -> Optional[BehaviorFamily]:
        """Look up a family by ID."""
        return self._families.get(family_id)

    def list_behaviors(self) -> List[CanonicalBehaviorDefinition]:
        """List all registered behaviors."""
        return list(self._behaviors.values())
