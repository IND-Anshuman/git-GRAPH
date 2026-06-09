# Temporal Code Knowledge Graph Platform: Capabilities & Technical Reference

This document serves as the comprehensive technical reference and capabilities catalog for the **Temporal Code Knowledge Graph Platform**. It details the supported languages, semantic entities, relationship edges, behavior logic types, concept classifications, and semantic discovery engines up to the Phase 5C implementation.

---

## Table of Contents
1. [Supported Programming Languages](#1-supported-programming-languages)
2. [Platform Entities (Supported Nodes)](#2-platform-entities-supported-nodes)
   * [A. Structural Entities (Codebase AST Layer)](#a-structural-entities-codebase-ast-layer)
   * [B. Behavioral Entities (Phase 3 Behavior Graph)](#b-behavioral-entities-phase-3-behavior-graph)
   * [C. Conceptual Entities (Phase 4 Concept Graph)](#c-conceptual-entities-phase-4-concept-graph)
   * [D. Intermediate Semantic Representation (ISR Layer)](#d-intermediate-semantic-representation-isr-layer)
   * [E. Meta-Ontology & Embedding Registry Layer (Phase 5A)](#e-meta-ontology--embedding-registry-layer-phase-5a)
   * [F. Governance, Evolution, & Boundaries Layer (Phase 5A/5C)](#f-governance-evolution--boundaries-layer-phase-5a5c)
3. [Supported Relationship Edges](#3-supported-relationship-edges)
   * [A. AST / Structural Edges](#a-ast--structural-edges)
   * [B. Conceptual Edges](#b-conceptual-edges)
   * [C. Distributed & Messaging Edges (Phase 5B)](#c-distributed--messaging-edges-phase-5b)
   * [D. Frontend UI Edges (Phase 5B)](#d-frontend-ui-edges-phase-5b)
   * [E. AI-Native Agent Edges (Phase 5B)](#e-ai-native-agent-edges-phase-5b)
4. [Supported Logic Types (Behavior Detection Patterns)](#4-supported-logic-types-behavior-detection-patterns)
5. [Supported Concept Types (Ontology Registry Taxonomy)](#5-supported-concept-types-ontology-registry-taxonomy)
6. [Advanced Semantics & Discovery Engines (Phase 5A, 5B, 5C)](#6-advanced-semantics--discovery-engines-phase-5a-5b-5c)
   * [A. Dynamic Meta-Ontology & Schema Registry](#a-dynamic-meta-ontology--schema-registry)
   * [B. Embedding Registry & Similarity Search](#b-embedding-registry--similarity-search)
   * [C. Confidence Calibration Engine](#c-confidence-calibration-engine)
   * [D. Relationship & Interaction Discovery Engine](#d-relationship--interaction-discovery-engine)
   * [E. Concept Discovery Engine & Placement Scores](#e-concept-discovery-engine--placement-scores)
   * [F. Flow Discovery Engine & Structural Path Tracing](#f-flow-discovery-engine--structural-path-tracing)
   * [G. Semantic Evolution & Bitemporal Query Engine](#g-semantic-evolution--bitemporal-query-engine)

---

## 1. Supported Programming Languages

The platform parses codebase source trees and extracts entities using Tree-sitter. The following programming languages are supported:

| Language | Tree-sitter Parser | File Extensions | Integration Status |
| :--- | :--- | :--- | :--- |
| **Python** | `tree-sitter-python` | `.py` | Active |
| **JavaScript** | `tree-sitter-javascript` | `.js`, `.jsx`, `.mjs` | Active |
| **TypeScript** | `tree-sitter-typescript` | `.ts`, `.tsx` | Active |
| **Go** | `tree-sitter-go` | `.go` | Active |
| **Java** | `tree-sitter-java` | `.java` | Active |
| **C#** | `tree-sitter-csharp` | `.cs` | Active (Phase 4.5) |
| **Rust** | `tree-sitter-rust` | `.rs` | Active (Phase 4.5) |
| **Kotlin** | `tree-sitter-kotlin` | `.kt` | Active (Phase 4.5) |
| **Swift** | `tree-sitter-swift` | `.swift` | Registered (Phase 4.5) |
| **PHP** | `tree-sitter-php` | `.php` | Registered (Phase 4.5) |
| **Scala** | `tree-sitter-scala` | `.scala` | Registered (Phase 4.5) |
| **Ruby** | `tree-sitter-ruby` | `.rb` | Registered (Phase 4.5) |
| **Elixir** | `tree-sitter-elixir` | `.ex`, `.exs` | Registered (Phase 4.5) |
| **HTML** | `tree-sitter-html` | `.html`, `.htm` | Registered (Phase 5B) |
| **CSS** | `tree-sitter-css` | `.css` | Registered (Phase 5B) |

---

## 2. Platform Entities (Supported Nodes)

Entities represent first-class node types within the Temporal Knowledge Graph, partitioned across six abstraction layers:

### A. Structural Entities (Codebase AST Layer)
* **`Repository`**: Represents a git codebase repository.
* **`Commit`**: Represents a point-in-time revision within the git history.
* **`SourceFile`**: Represents a physical source code file in the repository tree.
* **`CodeEntity`**: Represents an individual syntactic construct extracted from a file's AST. Valid subtypes include:
  * `Module`: Declaration module (Python, TS, Go, Elixir).
  * `Package`: Package grouping namespace.
  * `Class`: Class declaration (Java, C#, Python, TS, Kotlin).
  * `Struct`: Struct definition (Rust, Swift, Go).
  * `Interface`/`Trait`: Interface or trait contract (Java, C#, Kotlin, Rust).
  * `Method`/`Function`: Executable function or class method blocks.
  * `Variable`/`Constant`: Variable or constant declarations.
  * `Enum`: Enum declaration.
  * `Decorator`: Decorator metadata annotation.
  * `TypeAlias`: User-defined type alias.

### B. Behavioral Entities (Phase 3 Behavior Graph)
* **`BehaviorPattern`**: A template rule defining matching signatures for Tree-sitter AST queries.
* **`LogicSignature`**: Represents the stable behavioral identity of a code entity tracked across commits.
* **`LogicVersion`**: A point-in-time snapshot of the behavioral features implemented by a logic signature at a specific commit.
* **`LogicEvidence`**: Raw audit evidence (matched imports, matched calls, matched rules) supporting a logic version match.
* **`LogicTransition`**: An edge representing a detected change (creation, evolution, deletion) between two logic versions.
* **`BehaviorExplanation`**: A deterministic explanation verdict describing the footprint statistics of a logic version.
* **`BehaviorDrift`**: A node containing multidimensional drift dimensions between two commits.
* **`LogicCluster`**: A grouping of logically similar logic signatures based on AST structure and dependency hashes.

### C. Conceptual Entities (Phase 4 Concept Graph)
* **`OntologyNode`**: A node representing a capability category in the master hierarchical taxonomy.
* **`ConceptNode`**: A repository-specific capability node instantiated by aggregating logic versions matching a given ontology category.
* **`ConceptVersion`**: A point-in-time snapshot of a concept node at a commit.
* **`ConceptEvidence`**: Associations linking a concept version to underlying logic versions.
* **`ConceptCluster`**: High-level capability groupings of concept nodes.
* **`ConceptExplanation`**: An explanation summarizing a concept version's structural stats.
* **`ConceptMetrics`**: PageRank, centrality, and impact scoring metrics computed for a concept version.
* **`ConceptDrift`**: Multidimensional drift scores computed between concept snapshots.
* **`ConceptEvolution`**: Evolutionary transitions (split, merge, modify) between concept versions.

### D. Intermediate Semantic Representation (ISR Layer)
* **`CanonicalEntity`**: Language-neutral representation of a code construct. Valid types include:
  * `Class`/`Interface`: Generic struct or interface wrappers.
  * `Coroutine`: Asynchronous tasks, promises, and futures.
  * `Actor`: Message-driven actor state-machines.
  * `Channel`: Thread-safe asynchronous queues.
  * `Agent`: AI conversational agent controllers.
  * `Model`: Language model references.
* **`CanonicalRelationship`**: Standardized semantic edges connecting canonical entities.
* **`CanonicalBehavior`**: Unified action signature containing matched aliases and confidence evidence.
* **`CanonicalContext`**: Execution settings and detected framework versions.
* **`CanonicalFlow`**: First-class traced execution paths capturing sequential dependencies.

### E. Meta-Ontology & Embedding Registry Layer (Phase 5A)
* **`MetaType`**: Dynamically registered semantic type identifiers.
* **`MetaDefinition`**: Versioned schema configuration structures (compiled and validated via JSON Schema).
* **`EmbeddingModel`**: Vector embedding model registrations (name, provider, dimensions, distance metrics).
* **`EmbeddingVersion`**: Specific configuration checkpoints and hyperparameter registers for embedding models.

### F. Governance, Evolution, & Boundaries Layer (Phase 5A/5C)
* **`ConceptCandidate`**: Proposed concepts under governance waiting for promotion or rejection.
* **`CapabilityCandidate`**: Proposed macro capabilities computed using flow and concept similarities.
* **`CandidateEvidence`**: Unified evidence object capturing supporting entities, relationships, behaviors, and flows.
* **`ConceptLineage`**: Structural mutation timeline mapping concept splits, merges, and rename ancestry.
* **`MicroserviceBoundary`**: Network and process boundaries separating distributed sub-systems (RPC/messaging queues).

---

## 3. Supported Relationship Edges

The platform links nodes using semantic directed edges depending on the graph abstraction layer:

### A. AST / Structural Edges
* **`CALLS`**: A function/method invokes another function/method.
* **`IMPORTS`**: A file/module imports a namespace or package.
* **`DEPENDS_ON`**: An entity depends on another entity.
* **`BELONGS_TO`**: A child node belongs to a parent scope.
* **`EXTENDS`**: A class extends another base class.
* **`IMPLEMENTS`**: A class implements an interface/trait contract.
* **`READS`**: A function reads a variable/field.
* **`WRITES`**: A function writes/modifies a variable/field.
* **`USES`**: An entity uses another entity.
* **`TESTS`**: A test function exercises a target method/class.
* **`DECORATES`**: An annotation/decorator wraps a function or class.

### B. Conceptual Edges
* **`DEPENDS_ON`**: Concept A structurally depends on Concept B.
* **`IMPLEMENTS`**: Concept A implements the capability contract of Concept B.
* **`SUPPORTS`**: Concept A supports the execution of Concept B.
* **`USES`**: Concept A utilizes specific functionalities of Concept B.
* **`REQUIRES`**: Concept A strictly requires Concept B to run.
* **`ENHANCES`**: Concept A extends or optimizes Concept B.
* **`REPLACES`**: Concept A supersedes or replaces Concept B.

### C. Distributed & Messaging Edges (Phase 5B)
* **`PASSES_STATE_TO`**: Sequential data passing across service interfaces.
* **`INJECTED_INTO`**: Dependency injection of services, utilities, or databases.
* **`PUBLISHES_EVENT_TO`**: Async publishing of events.
* **`TRIGGERS`**: Triggers execution in a dependent component.
* **`CALLS_ENDPOINT`**: HTTP, gRPC, or RPC invocation of a remote endpoint route.
* **`PUBLISHES_TO_TOPIC`**: Event publication to a Kafka or RabbitMQ broker topic.
* **`CONSUMES_FROM_TOPIC`**: Async consumption from a topic partition or queue.
* **`BELONGS_TO_GROUP`**: Group membership in broker consumer groups.

### D. Frontend UI Edges (Phase 5B)
* **`USES_HOOK`**: React/Vue/Svelte component subscribing to state hooks.
* **`NAVIGATES_TO`**: Routing navigation link between pages/views.
* **`DISPATCHES_ACTION`**: State actions dispatched to a Redux/Pinia store.

### E. AI-Native Agent Edges (Phase 5B)
* **`USES_TOOL`**: AI Agent calls an external tool function.
* **`CALLS_MODEL`**: Model invocation (e.g. Google Gemini Client API).
* **`ROUTES_TO_AGENT`**: Conversational route dispatching from router to a sub-agent.
* **`RETRIEVES_CONTEXT`**: Vector database lookup or prompt context retrieval.
* **`WRITES_MEMORY`**: Storing chat history or agent states.
* **`READS_MEMORY`**: Accessing past context from storage.
* **`EVALUATES_OUTPUT`**: Running evaluator checks on model output.
* **`REFLECTS_ON_RESULT`**: Agent feedback reflection loop execution.

---

## 4. Supported Logic Types (Behavior Detection Patterns)

The platform includes **33 active behavioral detection patterns** matching AST structures:

### 🔒 Security (Authentication & Authorization)
* **`auth_direct_compare`**: Plaintext credentials comparisons without hashing.
* **`auth_sha256_verification`**: SHA256 password checks via `hashlib.sha256`.
* **`auth_bcrypt_verification`**: Password verification via `bcrypt.checkpw`.
* **`auth_bcrypt_hash`**: Bcrypt hashing and salt generation (`bcrypt.hashpw`).
* **`auth_jwt_generation`**: Signed JWT token creation.
* **`auth_jwt_verification`**: JWT token validation decodes.
* **`auth_passlib_verify`**: Passlib password verification.
* **`auth_argon2_verification`**: Argon2 cryptographic password verification.
* **`authz_permission_check`**: Direct checks on user permissions or scopes.
* **`authz_rbac`**: Checks on user roles (e.g. `has_role`, `is_in_role`).

### 💾 Data Management (Caching, Database, Serialization)
* **`cache_memory_dict`**: Local process dictionary caches.
* **`cache_lru_cache`**: Function result caching (`@lru_cache`, `@cache`).
* **`cache_redis_lookup`**: Reading from a Redis store.
* **`cache_redis_set`**: Writing to a Redis store.
* **`cache_redis_cluster`**: Clustered Redis cache queries.
* **`cache_invalidation`**: Evicting keys from caches.
* **`db_raw_sql_execute`**: Direct SQL cursor execution.
* **`db_orm_sqlalchemy_query`**: SQLAlchemy ORM queries.
* **`db_repository_pattern`**: Repository classes wrapping DB actions.
* **`db_transaction`**: Transaction boundaries (`commit`, `rollback`).

### 🔄 Reliability (Retry & Circuit Breaker)
* **`circuit_breaker_pybreaker`**: Fault tolerance circuit policies via `pybreaker`.
* **`circuit_breaker_manual`**: Manual state-based circuit breaking.
* **`retry_tenacity`**: Retries via the `tenacity` library.
* **`retry_manual_loop`**: Custom try-except retries inside loops.
* **`retry_backoff`**: Exponential backoff loops.

### 🌐 Integration (HTTP Client, GenAI, Messaging)
* **`api_requests_call`**: HTTP requests via `requests`.
* **`api_httpx_call`**: HTTP calls via `httpx`.
* **`api_endpoint_handler`**: HTTP routing endpoints (FastAPI `@router.post`, etc.).
* **`api_gemini_client`**: Google GenAI model calls.
* **`tts_parler_generation`**: Text-to-Speech audio generation via Parler.
* **`msg_publish_kafka`**: Kafka message publishing.
* **`msg_publish_rabbitmq`**: RabbitMQ message dispatching.
* **`msg_consume`**: Subscriber routing tasks.

---

## 5. Supported Concept Types (Ontology Registry Taxonomy)

Concept types represent high-level ontology capabilities. The following categories are loaded and matched by the Concept Graph Ontology Registry:

### 🔒 Security Capability Domain
* **`security.authentication`**: User, system, or client identity verification.
  * **`security.authentication.direct_compare`**: Plaintext credentials comparisons.
  * **`security.authentication.hash_comparison`**: Verification using cryptographic hashing (SHA256, bcrypt, Argon2).
  * **`security.authentication.jwt`**: Token authentication.
  * **`security.authentication.oauth`**: OAuth2/SSO provider integrations.
  * **`security.authentication.session`**: Session state management.
* **`security.authorization`**: Access control enforcement.
  * **`security.authorization.rbac`**: Role-based access control checking.
  * **`security.authorization.abac`**: Attribute-based policy checks.
  * **`security.authorization.permission_check`**: Direct checks on permissions.
* **`security.cryptography`**: Cipher operations.
  * **`security.cryptography.symmetric`**: Symmetric ciphers (AES).
  * **`security.cryptography.asymmetric`**: Asymmetric cryptography (RSA).
  * **`security.cryptography.signing`**: Digital signatures.

### 💾 Data Management Capability Domain
* **`data_management.caching`**: Caching configurations.
  * **`data_management.caching.memory`**: In-process caches.
  * **`data_management.caching.redis`**: Redis caching.
  * **`data_management.caching.memcached`**: Memcached caching.
  * **`data_management.caching.invalidation`**: Eviction logic.
* **`data_management.database`**: Database stores.
  * **`data_management.database.raw_sql`**: SQL query executions.
  * **`data_management.database.orm_query`**: ORM operations.
  * **`data_management.database.repository`**: Decoupled repository patterns.
  * **`data_management.database.transaction`**: Transactions.

### 🔄 Reliability Capability Domain
* **`reliability.fault_tolerance`**: Resilience patterns.
  * **`reliability.fault_tolerance.circuit_breaker`**: Pybreaker/manual circuit breakers.
  * **`reliability.fault_tolerance.retry`**: Retries.
  * **`reliability.fault_tolerance.backoff`**: Backoff algorithms.

### 🌐 Integration Capability Domain
* **`integration.api_client`**: API HTTP clients.
  * **`integration.api_client.http`**: REST calls.
  * **`integration.api_client.genai`**: Google Gemini integrations.
* **`integration.audio`**: Audio components.
  * **`integration.audio.tts`**: TTS pipelines.
* **`integration.messaging`**: Pub/sub systems.
  * **`integration.messaging.kafka`**: Kafka publishers/consumers.
  * **`integration.messaging.rabbitmq`**: RabbitMQ brokers.

---

## 6. Advanced Semantics & Discovery Engines (Phase 5A, 5B, 5C)

### A. Dynamic Meta-Ontology & Schema Registry
Provides dynamic open-world meta-ontology discovery capabilities to the platform. It registers new semantic metadata types on the fly, manages SemVer schemas, and validates dynamic dictionary payloads using JSON Schema validation. A governance workflow coordinates the promotion lifecycle:
$$\text{EXPERIMENTAL} \longrightarrow \text{CANDIDATE} \longrightarrow \text{ACTIVE} \longrightarrow \text{DEPRECATED}$$

### B. Embedding Registry & Similarity Search
Handles vector embedding registrations, provider configurations, metric types (cosine, L2, dot product), and calculates distances to locate structurally and semantically similar method behaviors.

### C. Confidence Calibration Engine
Centralizes calibration formulas across all subsystems. Integrates joint probability scaling, Bayesian updates, and decayed taxonomical Noisy-OR aggregations:
$$C_{\text{final}} = \min\left(1 - \prod_{t \in U} (1 - c_t), \, \max_{e \in E}(c(e)) + (1 - \max_{e \in E}(c(e))) \times 0.25 \right)$$

### D. Relationship & Interaction Discovery Engine
Scans AST and Intermediate Semantic Representations to discover network interactions. It maps HTTP route handlers to HTTP clients, Kafka publishers to consumers, and AI agent triggers to core model engines.

### E. Concept Discovery Engine & Placement Scores
Aggregates logic signatures and behaviors into new concepts. It uses co-occurrence clustering and the Concept Placement Score formula:
$$\text{Concept Score} = 0.40 \times \text{Ontology Similarity} + 0.30 \times \text{Behavior Overlap} + 0.20 \times \text{Relationship Similarity} + 0.10 \times \text{Embedding Similarity}$$

It also computes capability scores for structural clusters:
$$\text{Capability Score} = 0.35 \times \text{Concept Similarity} + 0.30 \times \text{Flow Similarity} + 0.20 \times \text{Behavior Similarity} + 0.15 \times \text{Usage Coverage}$$

### F. Flow Discovery Engine & Structural Path Tracing
Traces multi-hop execution chains using Depth-First Search (DFS) algorithms. It extracts structural path types (`node_sequence` and `calls_signature`), builds fingerprints, and compares paths. Categorizes flows into standard `Execution Flow`s, `AI Flow`s, `Frontend Flow`s, or `Messaging Flow`s.

### G. Semantic Evolution & Bitemporal Query Engine
Executes historical reconstruction and diffing of code semantics over time. Supports querying a historic snapshot of concept hierarchies at any historic `commit_hash` / `as_of` timestamp, and calculates structural concept modifications, splits, and merges between any two commits.
