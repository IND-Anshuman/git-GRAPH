# Temporal Code Knowledge Graph Platform: Capabilities & Technical Reference

This document serves as the comprehensive theoretical reference and capabilities catalog for the **Temporal Code Knowledge Graph Platform**. It details the supported languages, semantic entities, relationship edges, behavior logic types, and concept classifications after the Phase 4.5 implementation.

---

## 1. Supported Programming Languages

The platform parses codebase source trees and extracts entities using Tree-sitter. The following programming languages are supported:

| Language | Tree-sitter Parser | File Extensions | Status |
| :--- | :--- | :--- | :--- |
| **Python** | `tree-sitter-python` | `.py` | Active |
| **JavaScript** | `tree-sitter-javascript` | `.js`, `.mjs` | Active |
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

---

## 2. Platform Entities (Supported Nodes)

Entities represent first-class node types within the Temporal Knowledge Graph, partitioned across four conceptual abstraction layers:

### A. Structural Entities (Codebase AST Layer)
* **`Repository`**: Represents a git codebase repository.
* **`Commit`**: Represents a point-in-time revision within the git history.
* **`SourceFile`**: Represents a physical source code file in the repository tree.
* **`CodeEntity`**: Represents an individual syntactic construct extracted from a file's Abstract Syntax Tree (AST). Valid subtypes include:
  * `Class`: Class declaration (C#, Java, Python, TS).
  * `Struct`: Struct definition (Rust, Swift).
  * `Interface`/`Trait`: Interface or trait contract (Java, C#, Kotlin, Rust).
  * `Method`/`Function`: Executable function or class method blocks.
  * `Module`: Declaration module (Python, TS, Go, Elixir).

### B. Behavioral Entities (Phase 3 Logic Layer)
* **`BehaviorPattern`**: A template rule defining matching signatures for tree-sitter AST queries.
* **`LogicSignature`**: Represents the stable behavioral identity of a code entity tracked across commits.
* **`LogicVersion`**: A point-in-time snapshot of the behavioral features implemented by a logic signature at a specific commit.
* **`LogicEvidence`**: Raw audit evidence (matched imports, matched calls, matched rules) supporting a logic version match.
* **`LogicTransition`**: An edge representing a detected change (creation, evolution, deletion) between two logic versions.
* **`BehaviorExplanation`**: A deterministic explanation verdict describing the footprint statistics of a logic version.
* **`BehaviorDrift`**: A node containing multidimensional drift dimensions between two commits.
* **`LogicCluster`**: A grouping of logically similar logic signatures based on AST structure and dependency hashes.

### C. Conceptual Entities (Phase 4 Ontology Layer)
* **`OntologyNode`**: A node representing a capability category in the master hierarchical taxonomy.
* **`ConceptNode`**: A repository-specific capability node instantiated by aggregating logic versions matching a given ontology category.
* **`ConceptVersion`**: A point-in-time snapshot of a concept node at a commit.
* **`ConceptEvidence`**: Associations linking a concept version to underlying logic versions.
* **`ConceptCluster`**: High-level capability groupings of concept nodes.
* **`ConceptExplanation`**: An explanation summarizing a concept version's structural stats.
* **`ConceptMetrics`**: PageRank, centrality, and impact scoring metrics computed for a concept version.
* **`ConceptDrift`**: Multidimensional drift scores computed between concept snapshots.
* **`ConceptEvolution`**: Evolutionary transitions (split, merge, modify) between concept versions.

### D. Intermediate Semantic Representation Entities (Phase 4.5 ISR Layer)
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

---

## 3. Supported Relationship Edges

The platform links nodes using semantic directed edges depending on the graph abstraction layer:

| Source Layer | Edge Type | Description |
| :--- | :--- | :--- |
| **AST/Structural** | `CALLS` | A function or method invokes another function or method. |
| **AST/Structural** | `INHERITS` | A class inherits from a base class. |
| **AST/Structural** | `IMPORTS` | A file or module imports a namespace/package. |
| **AST/Structural** | `DECLARES` | An entity (class, module) declares a child construct (method, inner class). |
| **AST/Structural** | `IMPLEMENTS` | A class implements an interface or trait. |
| **Conceptual** | `DEPENDS_ON` | A concept relies on another concept structurally. |
| **Conceptual** | `IMPLEMENTS` | A concept version implements a specific capability. |
| **Conceptual** | `SUPPORTS` | A capability supports another capability. |
| **Conceptual** | `USES` | A concept utilizes another concept. |
| **Conceptual** | `REQUIRES` | A concept strictly requires another concept to operate. |
| **Conceptual** | `ENHANCES` | A concept augments or patches another concept. |
| **Conceptual** | `REPLACES` | A concept supersedes another concept. |
| **Semantic/ISR** | `CALLS` | Standardized function or method invocation. |
| **Semantic/ISR** | `INJECTS` | Dependency injection of a service or repository. |
| **Semantic/ISR** | `SENDS` | Message publication or dispatch to a message broker queue. |
| **Semantic/ISR** | `USES_TOOL` | An AI Agent calls a tool function. |
| **Semantic/ISR** | `EXPOSES` | A controller method exposes an HTTP route endpoint. |
| **Semantic/ISR** | `CONSUMES` | A subscriber reads from a queue or topic partition. |

---

## 4. Supported Logic Types (Behavior Detection Patterns)

The platform includes **33 active behavioral detection patterns** that match tree-sitter AST tokens:

### 🔒 Security
* **`auth_direct_compare`**: Plaintext credentials comparisons without hashing.
* **`auth_sha256_verification`**: SHA256 password checks via `hashlib.sha256`.
* **`auth_bcrypt_verification`**: Password verification via `bcrypt.checkpw`.
* **`auth_bcrypt_hash`**: Bcrypt hashing and salt generation (`bcrypt.hashpw`).
* **`auth_jwt_generation`**: Signed JWT token creation.
* **`auth_jwt_verification`**: JWT token validation decodes.
* **`auth_passlib_verify`**: Passlib verification.
* **`auth_argon2_verification`**: Argon2 cryptographic password verification.
* **`authz_permission_check`**: Direct checks on user permissions or scopes.
* **`authz_rbac`**: Checks on user roles (e.g. `has_role`, `is_in_role`).

### 💾 Data Management
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

### 🔄 Reliability
* **`circuit_breaker_pybreaker`**: Fault tolerance circuit policies via `pybreaker`.
* **`circuit_breaker_manual`**: Manual state-based circuit breaking.
* **`retry_tenacity`**: Retries via the `tenacity` library.
* **`retry_manual_loop`**: Custom try-except retries inside loops.
* **`retry_backoff`**: Exponential backoff loops.

### 🌐 Integration
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
