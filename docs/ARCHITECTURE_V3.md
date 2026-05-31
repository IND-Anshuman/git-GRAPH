# Temporal Code Knowledge Graph Platform
# Architecture V3: Software Intelligence Extension

**Version**: 3.0  
**Classification**: Architecture Extension — Intelligence Layers  
**Prerequisite**: Architecture V2 (Foundational Specification)  
**Review Panel**: Distinguished Software Architect, Principal Knowledge Graph Architect, Staff Compiler Engineer, Principal RAG Architect, Principal AI Agent Architect, Software Intelligence Researcher, Distributed Systems Architect, Git Internals Specialist, Program Analysis Research Engineer

---

## Preamble

Architecture V2 established the foundational data model: entities, relationships, temporal versioning, structural/semantic/temporal graph layers, identity resolution, and PostgreSQL storage. That architecture produces a **code indexing system** — a system that can answer "what exists?" and "what changed?"

Architecture V3 extends the platform into a **software intelligence system** — a system that can answer "why did it change?", "what does it mean?", "what will break?", and "how has thinking evolved?" This document designs six new intelligence subsystems, an orchestration layer, and a RAG integration strategy, all preserving full backward compatibility with V2.

The fundamental insight driving V3 is: **V2 tracks what the code is. V3 tracks what the code means.** V2 records that a function's body changed between two commits. V3 understands that the function transitioned from direct password comparison to bcrypt verification, that this change belongs to the "Authentication" concept and the "User Security" business capability, that the commit was a security fix, that the change reduced architectural drift in the security layer, and that the change impacts 14 downstream consumers with a risk score of 0.73.

---

# Table of Contents

1. [Logic Evolution Graph](#section-1-logic-evolution-graph)
2. [Concept Graph](#section-2-concept-graph)
3. [Business Capability Graph](#section-3-business-capability-graph)
4. [Commit Intent Classification](#section-4-commit-intent-classification)
5. [Architecture Drift Engine](#section-5-architecture-drift-engine)
6. [Runtime Knowledge Graph](#section-6-runtime-knowledge-graph)
7. [Impact Prediction Engine](#section-7-impact-prediction-engine)
8. [Software Intelligence Layer](#section-8-software-intelligence-layer)
9. [RAG Integration Strategy](#section-9-rag-integration-strategy)
10. [Architectural Review](#section-10-architectural-review)

---

# Section 1: Logic Evolution Graph

## 1.1 Motivation

V2's Temporal Graph records that an entity was MODIFIED at commit C. It stores the old source text and the new source text. It computes a structural fingerprint (normalized AST hash). But it does not understand **what changed behaviorally**. A function that transitions from bubble sort to quicksort registers as MODIFIED — identical to a function that merely renames a local variable. The temporal graph is behavior-blind.

The Logic Evolution Graph adds a **behavioral dimension** to temporal tracking. It does not replace the temporal graph; it layers on top of it, enriching entity version transitions with behavioral semantics.

## 1.2 Ontology

### Node Types

#### LogicSignature

**Purpose**: Represents the abstract behavioral fingerprint of an entity version. A LogicSignature captures *what* the code does, not *how* it is written syntactically.

**Attributes**:
- `id`: UUID.
- `entity_version_id`: FK → entity_versions. The specific version this signature describes.
- `seid`: UUID. The stable entity ID (denormalized for query efficiency).
- `signature_type`: Enum. The method used to generate this signature.
  - `CONTROL_FLOW`: Derived from control flow graph analysis.
  - `DATA_FLOW`: Derived from data flow analysis.
  - `API_SURFACE`: Derived from function signature and return type.
  - `ALGORITHMIC`: Derived from computational pattern classification.
  - `BEHAVIORAL_EMBEDDING`: Derived from a semantic embedding of behavior description.
- `fingerprint`: String. A hashable representation of the logic signature.
- `confidence`: Float (0.0–1.0). How confident the system is in the accuracy of this signature.
- `detail`: JSONB. Structured breakdown of the signature components.

**Metadata**:
- Control flow complexity (cyclomatic, cognitive)
- Data flow summary (inputs consumed, outputs produced, side effects)
- API calls made (ordered list of external function invocations)
- Algorithmic pattern label (if classifiable: sorting, searching, hashing, encryption, iteration, recursion, etc.)
- IO operations (file, network, database)

#### LogicTransition

**Purpose**: Represents a detected behavioral change between two consecutive versions of the same entity. This is the primary analytical object in the Logic Evolution Graph.

**Attributes**:
- `id`: UUID.
- `seid`: UUID. The entity whose logic transitioned.
- `from_version_id`: FK → entity_versions.
- `to_version_id`: FK → entity_versions.
- `transition_type`: Enum.
  - `ALGORITHM_CHANGE`: The computational approach changed (e.g., linear search → binary search).
  - `SECURITY_HARDENING`: Security-relevant logic was strengthened (e.g., plaintext → hashed).
  - `SECURITY_WEAKENING`: Security-relevant logic was weakened (rare but critical to detect).
  - `ERROR_HANDLING_CHANGE`: Error/exception handling was added, removed, or modified.
  - `PERFORMANCE_OPTIMIZATION`: Logic was restructured for performance (e.g., N+1 → batch query).
  - `CONTROL_FLOW_CHANGE`: Branching logic was altered (new conditions, removed conditions).
  - `DATA_FLOW_CHANGE`: The data transformation pipeline was modified.
  - `API_SURFACE_CHANGE`: The function's external contract changed (parameters, return type).
  - `BEHAVIOR_PRESERVING`: Logic was rewritten but behavior is equivalent (refactoring).
  - `UNKNOWN`: The system detected a change but cannot classify it.
- `confidence`: Float. How confident the classification is.
- `description`: String. Human-readable explanation of what changed.
- `evidence`: JSONB. Supporting data for the classification.
- `commit_hash`: CHAR(40). The commit that caused the transition.

#### BehaviorChain

**Purpose**: An aggregate view of an entity's complete behavioral evolution. A chain of LogicTransitions for a single SEID, ordered chronologically. Not stored as a separate table — computed by traversing LogicTransitions filtered by SEID.

### Edge Types

#### LOGIC_EVOLVED_TO

**Meaning**: A directed temporal edge from one LogicSignature to another, indicating that the entity's behavior transitioned from state A to state B.

**Direction**: Earlier version → Later version. `LogicSignature_V1 LOGIC_EVOLVED_TO LogicSignature_V2`.

**Cardinality**: One-to-One within a single entity's timeline (each version has at most one predecessor and one successor).

**Metadata carried on the edge**: The `LogicTransition` object — the transition type, confidence, and description. The edge is the transition.

**Traversal Implications**: Following LOGIC_EVOLVED_TO from the earliest LogicSignature of an entity traces its complete behavioral history. This answers "how has this entity's logic evolved?"

#### LOGIC_SIMILAR_TO

**Meaning**: A non-temporal edge between two LogicSignatures (potentially in different entities) that exhibit similar behavioral patterns.

**Direction**: Bidirectional. `LogicSig_A LOGIC_SIMILAR_TO LogicSig_B`.

**Cardinality**: Many-to-Many.

**Use Cases**: "Find other functions that use the same algorithmic pattern as this one." "Find all functions that perform bcrypt verification." Cross-entity behavioral pattern detection.

**Detection**: Computed from behavioral embedding similarity (cosine distance below a threshold) or identical algorithmic pattern labels.

#### LOGIC_REGRESSION

**Meaning**: A specialized edge indicating that a logic transition appears to revert or regress a previous improvement. For example, a function that was upgraded from SHA256 to bcrypt, then later changed back to SHA256.

**Direction**: Points from the regressed version to the earlier version it reverted toward. This is a derived analytical edge, not a primary storage edge.

**Detection**: When a LogicSignature at version N is more similar to the signature at version N-2 than to N-1, a potential regression is flagged.

## 1.3 Behavior Change Detection

### Approach 1: Control Flow Graph Differencing (Deterministic)

**Mechanism**: For each entity version, extract the control flow graph (CFG) from the AST. The CFG represents the branching structure: if/else chains, loops, try/catch blocks, switch statements. Normalize the CFG by replacing concrete values and identifiers with type tokens. Compute a graph hash of the normalized CFG.

**What it detects**: Changes in branching logic, loop structures, exception handling paths. Does NOT detect changes within straight-line code blocks (e.g., replacing one function call with another that has the same control flow).

**Strengths**: Deterministic, cheap to compute (requires only the AST which is already available), no external dependencies.

**Weaknesses**: Blind to data flow changes, API substitutions, and algorithmic changes that preserve control flow structure. A function that swaps `hashlib.sha256` for `bcrypt.hashpw` without changing any branching has an identical CFG.

### Approach 2: Data Flow Fingerprinting (Deterministic)

**Mechanism**: For each entity version, extract the set of external symbols referenced in the function body. This includes: function calls made, types instantiated, constants referenced, and global variables accessed. Normalize by stripping argument values. Sort and hash the resulting symbol list.

**What it detects**: Changes in which external functions/libraries are used. The SHA256 → bcrypt transition is detectable because the referenced symbols change from `hashlib.sha256` to `bcrypt.hashpw`.

**Strengths**: Deterministic, cheap, captures API-level transitions.

**Weaknesses**: Cannot distinguish *how* symbols are used. A function that calls `bcrypt.hashpw` once vs. ten times has the same data flow fingerprint. Cannot detect changes in custom logic that does not reference new external symbols.

### Approach 3: Behavioral Embedding Differencing (AI-Assisted)

**Mechanism**: Generate a natural-language description of the function's behavior (either from its docstring, its LLM-generated summary, or a direct LLM analysis of the code). Embed this description into a vector. Compare vectors between consecutive versions. A significant vector distance (cosine similarity below 0.85) indicates a behavioral change.

**What it detects**: Semantic/intentional changes. The embedding captures *what the code does* at a conceptual level. Algorithm substitutions, security changes, and performance optimizations all produce measurable embedding shifts.

**Strengths**: Captures meaning, not just syntax. Can detect subtle behavioral changes invisible to structural analysis.

**Weaknesses**: Non-deterministic (LLM summaries may vary). Expensive (requires LLM call + embedding computation per entity version). Embedding models may not reliably distinguish small behavioral changes from irrelevant phrasing differences.

### Approach 4: LLM-Based Transition Classification (AI-Assisted)

**Mechanism**: Present the LLM with the source code of two consecutive versions and ask it to classify the nature of the change. Provide a structured prompt with the transition type taxonomy. The LLM returns a transition type label and a natural-language explanation.

**What it detects**: The full spectrum of behavioral changes, including nuanced transitions (security hardening, performance optimization, error handling improvement) that cannot be detected structurally.

**Strengths**: Highest accuracy for complex transitions. Produces human-readable explanations.

**Weaknesses**: Highest cost (full LLM inference per transition). Non-deterministic. Potentially slow for batch processing. Cannot be used for real-time analysis.

### Recommended Hybrid Strategy

The system applies detection approaches in a **cascading pipeline**, from cheapest to most expensive, stopping when sufficient confidence is achieved:

```
Step 1: Control Flow Graph Diff (deterministic)
  → If CFG hash unchanged AND data flow fingerprint unchanged:
      Label: BEHAVIOR_PRESERVING (confidence: 0.95)
      STOP.

Step 2: Data Flow Fingerprint Diff (deterministic)
  → If CFG unchanged but data flow changed:
      Record changed symbols.
      Apply heuristic rules:
        - If security-related symbols changed (crypto libs, auth libs): SECURITY_HARDENING or SECURITY_WEAKENING (confidence: 0.8)
        - If database/ORM symbols changed: DATA_FLOW_CHANGE (confidence: 0.75)
        - Otherwise: flag for next step.
  → If CFG changed:
      Record structural change metrics (added/removed branches).
      Flag for next step.

Step 3: Behavioral Embedding Diff (AI-assisted, batch-friendly)
  → Compute behavioral embeddings for both versions.
  → If cosine similarity > 0.92: BEHAVIOR_PRESERVING (confidence: 0.8). STOP.
  → If cosine similarity < 0.7: Major behavioral change. Flag for LLM classification.
  → Otherwise: moderate change. Flag for LLM classification if entity has high fan-in (many dependents).

Step 4: LLM Transition Classification (AI-assisted, expensive)
  → Present both versions to LLM with structured prompt.
  → LLM returns transition_type and description.
  → Assign confidence based on LLM's own reported certainty, capped at 0.9.
```

This cascade ensures that the majority of transitions (estimated 60–70% of modifications are behavior-preserving refactoring/formatting) are classified cheaply in Steps 1–2. Only genuinely interesting behavioral changes reach the expensive LLM step.

## 1.4 Logic Fingerprint Generation

A LogicSignature is a composite object generated as follows:

```
LogicSignature = {
  control_flow_hash:    hash(normalized_CFG),
  data_flow_hash:       hash(sorted(external_symbol_references)),
  api_surface_hash:     hash(parameter_types + return_type + visibility),
  behavioral_embedding: vector(LLM_summary_of_behavior),
  algorithmic_label:    classify(AST_patterns) → "sorting" | "searching" | "encryption" | "iteration" | "io" | "unknown",
  complexity_metrics: {
    cyclomatic: int,
    cognitive: int,
    nesting_depth: int,
    branch_count: int,
    loop_count: int
  },
  io_profile: {
    reads_file: bool,
    writes_file: bool,
    network_call: bool,
    database_query: bool,
    cache_access: bool
  }
}
```

The composite `fingerprint` field is computed as:
```
fingerprint = hash(control_flow_hash + data_flow_hash + api_surface_hash)
```

This deterministic fingerprint changes if and only if the function's control flow, external dependencies, or API contract changes. The behavioral embedding is stored separately and used for similarity queries, not for fingerprint identity.

## 1.5 Storage Model

### Table: `logic_signatures`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Signature identifier |
| `seid` | UUID | FK → entities, NOT NULL | Entity this signature describes |
| `entity_version_id` | UUID | FK → entity_versions, NOT NULL | Specific version |
| `fingerprint` | CHAR(64) | NOT NULL | Composite logic fingerprint |
| `control_flow_hash` | CHAR(64) | NOT NULL | CFG hash |
| `data_flow_hash` | CHAR(64) | NOT NULL | External symbol reference hash |
| `api_surface_hash` | CHAR(64) | NOT NULL | Signature hash |
| `algorithmic_label` | VARCHAR(50) | NULLABLE | Classified algorithmic pattern |
| `complexity_metrics` | JSONB | NOT NULL | Cyclomatic, cognitive, nesting metrics |
| `io_profile` | JSONB | NOT NULL | IO operation flags |
| `behavioral_embedding` | VECTOR(1536) | NULLABLE | Semantic behavior vector |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_logic_sig_seid` on `(seid, entity_version_id)`
- `idx_logic_sig_fingerprint` on `fingerprint`
- `idx_logic_sig_algorithmic` on `algorithmic_label` WHERE `algorithmic_label IS NOT NULL`
- `idx_logic_sig_embedding` using HNSW on `behavioral_embedding vector_cosine_ops`

### Table: `logic_transitions`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Transition identifier |
| `seid` | UUID | FK → entities, NOT NULL | Entity that transitioned |
| `from_version_id` | UUID | FK → entity_versions, NOT NULL | Source version |
| `to_version_id` | UUID | FK → entity_versions, NOT NULL | Target version |
| `from_signature_id` | UUID | FK → logic_signatures, NOT NULL | Source logic signature |
| `to_signature_id` | UUID | FK → logic_signatures, NOT NULL | Target logic signature |
| `transition_type` | VARCHAR(40) | NOT NULL | Classification label |
| `confidence` | REAL | NOT NULL | Classification confidence |
| `description` | TEXT | NULLABLE | Human-readable explanation |
| `detection_method` | VARCHAR(30) | NOT NULL | (CFG_DIFF, DATA_FLOW, EMBEDDING, LLM) |
| `evidence` | JSONB | DEFAULT '{}' | Supporting data |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Causing commit |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record timestamp |

**Indexes**:
- `idx_logic_trans_seid` on `(seid, commit_hash)`
- `idx_logic_trans_type` on `transition_type`
- `idx_logic_trans_commit` on `commit_hash`

## 1.6 Reconstruction Model

To reconstruct the behavioral evolution of an entity:

```
Query: SELECT lt.*, ls_from.*, ls_to.*
FROM logic_transitions lt
JOIN logic_signatures ls_from ON lt.from_signature_id = ls_from.id
JOIN logic_signatures ls_to ON lt.to_signature_id = ls_to.id
WHERE lt.seid = :target_seid
ORDER BY (SELECT version_ordinal FROM entity_versions WHERE id = lt.to_version_id) ASC
```

This returns the chronological chain of behavioral transitions. Each entry describes: what the behavior was before, what it became, what type of transition occurred, and why. Displaying this chain answers "how has authentication logic evolved?" with entries like:

```
V1 → V2: ALGORITHM_CHANGE (confidence 0.92)
  "Transitioned from direct string comparison of passwords to SHA-256 hash verification."
V2 → V3: SECURITY_HARDENING (confidence 0.95)
  "Upgraded from SHA-256 to bcrypt with salt, adding work factor parameter."
V3 → V4: BEHAVIOR_PRESERVING (confidence 0.97)
  "Refactored variable names and extracted helper function. No behavioral change."
```

---

# Section 2: Concept Graph

## 2.1 Motivation

The Structural Graph knows that `LoginController`, `JWTTokenGenerator`, `PasswordHasher`, and `SessionManager` are four distinct classes. But it does not know that they all belong to the concept of "Authentication." A developer asking "how does authentication work?" must manually identify the relevant entities. The Concept Graph bridges this gap by grouping entities into **architectural concepts** — cross-cutting concerns that span multiple modules, packages, and layers.

## 2.2 Concept Ontology

### What is a Concept?

A concept is a **domain-independent architectural concern** that manifests as a collection of entities working together to provide a specific capability. Concepts are language-agnostic and framework-agnostic. "Authentication" is a concept regardless of whether it is implemented in Python with Flask or in Java with Spring.

Concepts are distinct from business capabilities (Section 3). A concept describes a *technical concern*; a business capability describes a *business function*. "Caching" is a concept. "Order Management" is a business capability. "Caching" may serve "Order Management," but they exist at different abstraction levels.

### Concept Hierarchy

Concepts are organized in a **two-level hierarchy**: domains and concepts. A domain is a broad area; concepts are specific concerns within that domain.

```
SECURITY
├── Authentication
├── Authorization
├── Encryption
├── Input Validation
├── Session Management
└── Secret Management

DATA MANAGEMENT
├── Persistence
├── Caching
├── Data Transformation
├── Data Validation
├── Migration
└── Serialization

COMMUNICATION
├── API Gateway
├── Messaging
├── Notifications
├── WebSocket
├── Email
└── Event Publishing

INFRASTRUCTURE
├── Logging
├── Monitoring
├── Observability
├── Configuration
├── Error Handling
├── Health Checking
└── Feature Flagging

PRESENTATION
├── Routing
├── Templating
├── Localization
├── Pagination
└── Response Formatting

BUSINESS LOGIC
├── Workflow Orchestration
├── Rule Engine
├── Scheduling
├── Rate Limiting
└── Retry Logic

TESTING
├── Unit Testing
├── Integration Testing
├── Mocking
├── Fixture Management
└── Assertion Utilities
```

This taxonomy is a **starting point**, not a fixed schema. The system must support:
- User-defined concepts (custom labels added by teams).
- Concept discovery (LLM-assisted identification of concepts not in the predefined taxonomy).
- Concept refinement (splitting a concept into sub-concepts when the codebase warrants it).

### Node Types

#### Concept

**Attributes**:
- `id`: UUID.
- `name`: String. Human-readable concept name (e.g., "Authentication").
- `domain`: String. Parent domain (e.g., "SECURITY").
- `description`: String. Definition of what this concept encompasses.
- `detection_patterns`: JSONB. Heuristic rules for detecting this concept (keywords, decorators, library names, AST patterns).
- `is_system_defined`: Boolean. Whether this is from the predefined taxonomy or user-defined.

#### ConceptMembership

**Attributes**:
- `id`: UUID.
- `concept_id`: FK → concepts.
- `seid`: UUID. FK → entities.
- `confidence`: Float. How confident the classification is.
- `classification_method`: Enum. (HEURISTIC, EMBEDDING, LLM, MANUAL).
- `evidence`: JSONB. Why this entity was classified under this concept.
- `commit_hash`: CHAR(40). The commit at which this classification was computed.

### Edge Types

#### BELONGS_TO_CONCEPT

**Meaning**: An entity is a member of a concept. `PasswordHasher BELONGS_TO_CONCEPT Authentication`.

**Direction**: Entity → Concept.

**Cardinality**: Many-to-Many. An entity can belong to multiple concepts (e.g., `JWTTokenGenerator` belongs to both "Authentication" and "Encryption").

#### CONCEPT_DEPENDS_ON

**Meaning**: One concept depends on another at the architectural level. "Authentication CONCEPT_DEPENDS_ON Persistence" because auth entities store/retrieve credentials.

**Direction**: Dependent concept → Dependency concept.

**Detection**: Inferred from the structural IMPORTS/CALLS/DEPENDS_ON relationships between entities belonging to different concepts. If >30% of entities in concept A have dependencies on entities in concept B, a CONCEPT_DEPENDS_ON edge is created.

#### CONCEPT_RELATED_TO

**Meaning**: Two concepts are thematically related but without a directional dependency. "Authentication CONCEPT_RELATED_TO Authorization."

**Direction**: Bidirectional.

**Detection**: Concepts with high entity co-occurrence (entities frequently classified into both) or high embedding similarity between concept descriptions.

## 2.3 Concept Classification Strategy

### Tier 1: Heuristic Detection (Deterministic, Fast)

Each predefined concept carries a set of detection patterns:

```
Authentication:
  keywords: ["login", "logout", "authenticate", "credential", "password", "token", "jwt", "oauth", "session", "sso"]
  decorators: ["@login_required", "@authenticated", "@requires_auth"]
  libraries: ["passlib", "bcrypt", "pyjwt", "python-jose", "authlib"]
  file_patterns: ["auth*.py", "*authentication*", "*login*"]

Caching:
  keywords: ["cache", "memoize", "ttl", "invalidate", "evict", "redis", "memcached"]
  decorators: ["@cached", "@cache_page", "@lru_cache"]
  libraries: ["redis", "cachetools", "django.core.cache"]
  file_patterns: ["*cache*", "*caching*"]
```

An entity scores against each concept's patterns. Scoring:
- Entity name contains a keyword: +0.3
- Entity is in a file matching a file_pattern: +0.2
- Entity calls a library function matching the concept: +0.3
- Entity uses a matching decorator: +0.4

If total score ≥ 0.5, the entity is classified into the concept with confidence = min(score, 1.0) and method = HEURISTIC.

**Advantage**: Fast, deterministic, no API costs. Handles the majority of obvious classifications.

**Limitation**: Cannot detect entities that belong to a concept through indirect contribution. A utility function `format_expiry_date` that is only called from authentication code won't match authentication keywords.

### Tier 2: Graph Propagation (Deterministic, Medium Cost)

After Tier 1 classification, propagate concept membership through the structural graph:

If entity A is classified into concept C with confidence ≥ 0.7, and entity B is called exclusively by entities in concept C (and has no other concept classification), then entity B is classified into concept C with confidence = 0.5 × (A's confidence).

This cascading propagation captures "support" entities that don't have concept-specific names but serve a single concept.

**Depth Limit**: Propagation is limited to 2 hops to prevent concept leakage into genuinely shared utility code.

### Tier 3: Embedding Classification (AI-Assisted, Batch)

For entities not classified in Tiers 1–2, compute the entity's semantic embedding (from V2's enrichment pipeline) and compare it to concept reference embeddings. Each concept has a reference embedding computed from its description and a curated set of exemplar entities.

Nearest-concept assignment with confidence proportional to cosine similarity.

### Tier 4: LLM Classification (AI-Assisted, Expensive)

For high-value entities still unclassified (high fan-in entities, API endpoints, database models), present the entity's source code and context to an LLM with the concept taxonomy and ask for classification.

## 2.4 Concept Evolution Tracking

Concepts evolve along two axes:

### Axis 1: Membership Evolution
The set of entities belonging to a concept changes over time. Entities are added (a new auth handler), removed (a deprecated login method is deleted), or migrated (an entity moves from one concept to another).

**Storage**: The `concept_memberships` table includes `commit_hash`. By querying memberships at different commits, the system reconstructs concept membership at any historical point. A concept's "size" (entity count) can be charted over time.

### Axis 2: Concept Drift
A concept may drift if its member entities begin to take on responsibilities outside the concept's definition. If "Authentication" entities start directly querying product catalogs, that is concept drift — the auth system is accumulating non-auth responsibilities.

**Detection**: Periodically re-evaluate concept classification for all member entities. If an entity's membership confidence drops below 0.4 on re-evaluation, flag it as a potential drift indicator. If >20% of a concept's entities have declining confidence, flag the concept itself as experiencing drift.

---

# Section 3: Business Capability Graph

## 3.1 Motivation

The Concept Graph captures technical concerns. The Business Capability Graph captures **what the business does** as expressed through software. This is the layer that connects code to business stakeholders. A CTO asks "what changed in our billing system?" — not "what changed in entities classified under the Persistence concept."

Business capabilities are stable abstractions. Technology changes; business capabilities persist. A company may rewrite its billing system from Python to Go, but the "Billing" capability endures. Tracking capabilities separately from technical architecture provides a stable reference frame for long-term evolution analysis.

## 3.2 Capability Ontology

### What is a Business Capability?

A business capability is a **business-meaningful function** that the software enables. It corresponds to a domain in Domain-Driven Design or a feature area in product management. Capabilities are defined by business outcomes, not by technical implementation.

### Capability Hierarchy

```
USER MANAGEMENT
├── User Registration
├── User Profile
├── User Preferences
└── User Deactivation

IDENTITY & ACCESS
├── Authentication
├── Authorization
├── Role Management
└── Permission Management

BILLING & PAYMENTS
├── Invoice Generation
├── Payment Processing
├── Subscription Management
├── Refund Processing
└── Tax Calculation

ORDER MANAGEMENT
├── Order Creation
├── Order Fulfillment
├── Order Tracking
└── Order Cancellation

PRODUCT & INVENTORY
├── Product Catalog
├── Inventory Tracking
├── Pricing
└── Product Search

COMMUNICATION
├── Email Notifications
├── Push Notifications
├── In-App Messaging
└── SMS Notifications

REPORTING & ANALYTICS
├── Dashboard
├── Report Generation
├── Data Export
└── Audit Logging
```

Unlike the Concept taxonomy (which is predefined and relatively stable), the Capability hierarchy is **repository-specific**. Each repository (or repository group) has its own capability map, reflecting the business domains of the software it implements. The system should discover capabilities semi-automatically and allow user curation.

### Node Types

#### Capability

**Attributes**:
- `id`: UUID.
- `name`: String. Capability name.
- `parent_capability_id`: FK → capabilities (nullable, for hierarchy).
- `repository_id`: UUID (or repository_group_id for multi-repo).
- `description`: String.
- `owner`: String (nullable). Team or individual responsible.
- `status`: Enum. (ACTIVE, DEPRECATED, PLANNED).
- `is_auto_discovered`: Boolean.

#### CapabilityMapping

**Attributes**:
- `id`: UUID.
- `capability_id`: FK → capabilities.
- `seid`: UUID. FK → entities.
- `confidence`: Float.
- `mapping_method`: Enum. (DIRECTORY_CONVENTION, HEURISTIC, LLM, MANUAL).
- `commit_hash`: CHAR(40).

### Edge Types

#### PROVIDES_CAPABILITY

**Meaning**: An entity contributes to a business capability. `InvoiceProcessor PROVIDES_CAPABILITY Invoice Generation`.

**Direction**: Entity → Capability.

**Cardinality**: Many-to-Many.

#### CAPABILITY_DEPENDS_ON

**Meaning**: One capability depends on another. `Payment Processing CAPABILITY_DEPENDS_ON Invoice Generation`.

**Direction**: Dependent → Dependency.

**Detection**: Derived from structural dependencies between entities mapped to different capabilities.

#### CAPABILITY_SUPPORTS

**Meaning**: A technical concept supports a business capability. `Persistence CAPABILITY_SUPPORTS Billing & Payments`.

**Direction**: Concept → Capability.

**Detection**: Derived from entity overlap between concept memberships and capability mappings.

## 3.3 Capability Detection Strategy

### Strategy 1: Directory Convention Mapping

Many well-structured projects organize code by business domain:
```
src/
  billing/
  orders/
  users/
  payments/
  inventory/
```

Top-level directories under `src/` (or equivalent) are candidate capabilities. All entities within `src/billing/` are mapped to the "Billing" capability. This is the cheapest and most reliable detection method for conventionally structured projects.

**Confidence**: 0.85 for entities in clearly domain-named directories. 0.4 for entities in ambiguously named directories (e.g., `utils/`, `common/`, `shared/`).

### Strategy 2: Package/Module Semantic Clustering

For projects without clean directory structure, cluster modules by their semantic embeddings. Modules that are semantically similar and structurally connected (high IMPORTS density within the cluster) likely belong to the same business capability. Present clusters to LLM for capability naming.

### Strategy 3: LLM-Assisted Capability Discovery

Present the LLM with:
- The list of all packages and their contained entities.
- A sample of entity summaries (from V2's semantic enrichment).
- The structural dependency graph at the package level.

Ask: "What business capabilities does this codebase implement? For each capability, list the packages and key entities that contribute to it."

**Confidence**: 0.6–0.8 depending on LLM certainty and human review status.

### Strategy 4: Manual Curation

Provide an API for users to define capabilities, assign entities to capabilities, and correct auto-discovered mappings. Manual assignments have confidence 1.0 and override automated classifications.

## 3.4 Capability Evolution Tracking

### Capability Size Over Time

Track the number of entities mapped to each capability per commit (or per time period). A growing capability may indicate feature expansion; a shrinking capability may indicate deprecation.

### Capability Boundary Stability

Track how frequently entities migrate between capabilities. Stable boundaries indicate well-defined domain separation. Frequent migrations indicate unclear domain boundaries — a signal of architectural concern.

### Capability Dependency Evolution

Track how capability-level dependencies change over time. If "Billing" develops a new dependency on "Inventory" that did not exist 6 months ago, this represents a significant architectural evolution at the business level.

### Storage

Capability evolution is tracked through the same temporal mechanism as entities: `capability_mappings` include `commit_hash`, allowing reconstruction of capability membership at any point.

### Table: `capabilities`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Capability identifier |
| `name` | VARCHAR(255) | NOT NULL | Capability name |
| `parent_capability_id` | UUID | FK → capabilities, NULLABLE | Parent in hierarchy |
| `repository_id` | UUID | FK → repositories, NOT NULL | Owning repository |
| `description` | TEXT | NULLABLE | Capability description |
| `owner` | VARCHAR(255) | NULLABLE | Team or individual |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | (active, deprecated, planned) |
| `is_auto_discovered` | BOOLEAN | NOT NULL, DEFAULT TRUE | Auto vs. manual |
| `metadata` | JSONB | DEFAULT '{}' | Extensible |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

### Table: `capability_mappings`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Mapping identifier |
| `capability_id` | UUID | FK → capabilities, NOT NULL | Target capability |
| `seid` | UUID | FK → entities, NOT NULL | Mapped entity |
| `confidence` | REAL | NOT NULL | Mapping confidence |
| `mapping_method` | VARCHAR(30) | NOT NULL | Detection method |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | As-of commit |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record timestamp |

**Indexes**:
- `idx_cap_mappings_capability` on `(capability_id, commit_hash)`
- `idx_cap_mappings_seid` on `seid`

---

# Section 4: Commit Intent Classification

## 4.1 Motivation

V2 stores commit metadata verbatim: hash, message, author, date, parent references. But commits carry **intent** beyond their metadata. A commit that changes a password hashing function is a "Security" commit. A commit that adds a `try/catch` block around a network call is a "Bug Fix" or "Error Handling" commit. Understanding commit intent enables queries like "show me all security-related changes in the last quarter" — queries that are impossible with raw metadata.

## 4.2 Intent Taxonomy

```
FEATURE          – Adds new user-facing functionality
BUG_FIX          – Corrects defective behavior
REFACTOR         – Restructures code without changing external behavior
PERFORMANCE      – Improves execution speed, memory usage, or scalability
SECURITY         – Addresses security vulnerabilities or hardens defenses
CLEANUP          – Removes dead code, fixes formatting, improves naming
MIGRATION        – Database migration, API version upgrade, dependency upgrade
TEST             – Adds, modifies, or removes tests
DOCUMENTATION    – Updates comments, docstrings, README, or docs
CONFIGURATION    – Changes configuration files, environment variables, CI/CD
DEPENDENCY       – Adds, removes, or updates external dependencies
INFRASTRUCTURE   – Changes to deployment, Docker, CI/CD pipeline
HOTFIX           – Emergency production fix (may overlap with BUG_FIX; distinguished by urgency signals)
```

A single commit may carry **multiple intents**. A commit that adds a feature and its tests has intents `[FEATURE, TEST]`. The classification produces an array of (intent, confidence) pairs.

## 4.3 Classification Pipeline

### Signal 1: Commit Message Analysis (Fast, Deterministic + NLP)

Parse the commit message for intent signals:

**Conventional Commits detection**: Messages like `feat:`, `fix:`, `refactor:`, `perf:`, `chore:`, `docs:`, `test:`, `ci:` directly map to intent categories. When detected, assign with confidence 0.9.

**Keyword matching**: In the absence of conventional commit format, scan for keywords:
- `fix`, `bug`, `issue`, `crash`, `error`, `patch` → BUG_FIX
- `add`, `implement`, `introduce`, `new`, `feature` → FEATURE
- `refactor`, `rename`, `restructure`, `reorganize`, `clean up` → REFACTOR
- `perf`, `optimize`, `speed`, `cache`, `faster` → PERFORMANCE
- `security`, `vulnerability`, `CVE`, `auth`, `encrypt` → SECURITY
- `test`, `spec`, `coverage` → TEST
- `doc`, `readme`, `comment`, `docstring` → DOCUMENTATION
- `migrate`, `upgrade`, `version`, `bump` → MIGRATION or DEPENDENCY

**Confidence**: 0.6–0.75 for keyword matches (lower than conventional commits due to ambiguity).

### Signal 2: File Change Analysis (Fast, Deterministic)

Analyze which files were changed:

- Only test files changed → TEST (confidence boost +0.2)
- Only documentation files changed → DOCUMENTATION (confidence boost +0.3)
- Only config files changed → CONFIGURATION (confidence 0.85)
- Only `requirements.txt` / `package.json` / lockfiles → DEPENDENCY (confidence 0.9)
- Only Dockerfile / CI YAML → INFRASTRUCTURE (confidence 0.9)
- Only migration files → MIGRATION (confidence 0.9)

### Signal 3: Entity Mutation Analysis (Medium Cost, Deterministic)

Leverage V2's entity mutation data:

- If commit contains only RENAMED/MOVED mutations with no content changes → REFACTOR (confidence 0.8)
- If commit creates new entities with no modifications to existing ones → FEATURE (confidence 0.7)
- If commit modifies entities that previously appeared in bug-related logic transitions → BUG_FIX (confidence 0.6)
- If commit's logic transitions include SECURITY_HARDENING → SECURITY (confidence 0.8)

### Signal 4: LLM Classification (Expensive, High Accuracy)

For commits that remain unclassified or have low confidence after Signals 1–3, present to LLM:
- Commit message
- List of changed files
- Summary of entity mutations (types, count, nature)
- If available: logic transition classifications

Ask for structured intent classification.

**Confidence**: Model-reported, capped at 0.9.

### Aggregation

Signals are combined using weighted voting:

```
For each intent category:
  final_confidence = weighted_average(
    message_signal × 0.3,
    file_signal × 0.2,
    mutation_signal × 0.25,
    llm_signal × 0.25
  )

Emit all intents with final_confidence ≥ 0.4.
Primary intent = highest confidence intent.
```

## 4.4 Storage Schema

### Table: `commit_intents`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Record identifier |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Classified commit |
| `intent_type` | VARCHAR(30) | NOT NULL | Intent category |
| `confidence` | REAL | NOT NULL | Aggregated confidence |
| `is_primary` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is the dominant intent |
| `signals` | JSONB | NOT NULL | Per-signal breakdown |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Classification timestamp |

**Indexes**:
- `idx_commit_intents_hash` on `commit_hash`
- `idx_commit_intents_type` on `(intent_type, confidence DESC)`
- `idx_commit_intents_primary` on `commit_hash` WHERE `is_primary = TRUE`

---

# Section 5: Architecture Drift Engine

## 5.1 Motivation

Software architecture erodes over time. Teams introduce shortcuts, cross layer boundaries, create circular dependencies, and accumulate technical debt. This erosion is gradual and often invisible until the system becomes unmaintainable. The Architecture Drift Engine provides continuous monitoring and quantitative measurement of architectural health.

## 5.2 Drift Metrics

### Metric 1: Coupling Index

**Definition**: For a given package or module, the ratio of external dependencies to total dependencies (internal + external).

```
Coupling(P) = external_deps(P) / (internal_deps(P) + external_deps(P))
```

A coupling index approaching 1.0 indicates a module that depends almost entirely on external code — it has no internal cohesion. A coupling index near 0.0 indicates a highly self-contained module.

**Drift Signal**: Coupling index increasing over time. If `Coupling(billing)` was 0.3 six months ago and is 0.5 now, the billing module is becoming more coupled to external systems.

### Metric 2: Instability Index (Robert C. Martin)

**Definition**:

```
Instability(P) = Fan_out(P) / (Fan_in(P) + Fan_out(P))
```

Where Fan_out = number of outgoing dependencies (this package depends on others) and Fan_in = number of incoming dependencies (others depend on this package).

Instability near 1.0: the package is unstable (depends on many, few depend on it). Changes to its dependencies cascade to it.
Instability near 0.0: the package is stable (many depend on it, it depends on few). It should be abstract (contain interfaces).

**Drift Signal**: Packages with low instability that are concrete (not abstract) are in the "Zone of Pain" — they are hard to change but will be forced to change when dependencies change. Tracking this metric over time reveals packages drifting into the Zone of Pain.

### Metric 3: Abstractness Index

**Definition**: For a package, the ratio of abstract types (interfaces, abstract classes) to total types.

```
Abstractness(P) = abstract_types(P) / total_types(P)
```

### Metric 4: Distance from Main Sequence

**Definition**: Measures how far a package deviates from the ideal balance of abstractness and instability.

```
D(P) = |Abstractness(P) + Instability(P) - 1|
```

D = 0 is ideal (on the "Main Sequence"). D approaching 1.0 indicates a package in a problematic zone (Zone of Pain or Zone of Uselessness).

### Metric 5: Circular Dependency Count

**Definition**: Number of strongly connected components in the package-level or module-level dependency graph that contain more than one node.

**Drift Signal**: Increasing circular dependency count over time indicates architectural erosion.

### Metric 6: Layer Violation Count

**Definition**: Number of dependency edges that violate a declared layered architecture. For example, if the architecture declares that `infrastructure` may depend on `domain` but not vice versa, any IMPORTS edge from `domain` to `infrastructure` is a violation.

**Prerequisite**: The user (or the system, via heuristic or LLM) must define the intended layer ordering.

**Drift Signal**: Increasing violation count. New violations introduced in recent commits.

### Metric 7: God Module Score

**Definition**: Identifies modules with excessive entity count, excessive fan-in, or excessive fan-out.

```
GodScore(M) = normalize(entity_count(M)) × 0.4 + normalize(fan_in(M)) × 0.3 + normalize(fan_out(M)) × 0.3
```

Where normalize maps to [0, 1] relative to the repository's distribution.

**Drift Signal**: GodScore increasing over time for any module.

### Metric 8: Concept Leakage Score

**Definition**: Measures how much a concept's entities are scattered across the codebase rather than concentrated in a few packages.

```
ConceptLeakage(C) = 1 - (entities_in_primary_package(C) / total_entities(C))
```

Where `primary_package` is the package containing the most entities of concept C.

**Drift Signal**: Increasing leakage indicates the concept is spreading across the codebase rather than being encapsulated.

## 5.3 Drift Detection Rules

Rules combine metrics with temporal thresholds to generate alerts:

```
Rule: COUPLING_GROWTH
  Trigger: Coupling(P) increased by > 0.1 over the last 100 commits.
  Severity: WARNING if Coupling(P) > 0.5, CRITICAL if > 0.7.
  Message: "Package {P} coupling index grew from {old} to {new} over the last {N} commits."

Rule: LAYER_VIOLATION_INTRODUCED
  Trigger: A commit introduces a new IMPORTS edge that violates declared layer ordering.
  Severity: WARNING.
  Message: "Commit {hash} introduced a layer violation: {source_module} → {target_module}."

Rule: CIRCULAR_DEPENDENCY_INTRODUCED
  Trigger: A commit creates a new cycle in the package dependency graph.
  Severity: CRITICAL.
  Message: "Commit {hash} introduced circular dependency: {cycle_path}."

Rule: GOD_MODULE_GROWTH
  Trigger: GodScore(M) > 0.8.
  Severity: WARNING.
  Message: "Module {M} has grown to {entity_count} entities with {fan_in} inbound dependencies."

Rule: CONCEPT_LEAKAGE
  Trigger: ConceptLeakage(C) > 0.6.
  Severity: WARNING.
  Message: "Concept {C} is scattered across {N} packages. Consider consolidation."
```

## 5.4 Drift Storage

### Table: `drift_metrics`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Record identifier |
| `repository_id` | UUID | FK → repositories, NOT NULL | Repository |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Measured at commit |
| `subject_type` | VARCHAR(20) | NOT NULL | (PACKAGE, MODULE, CONCEPT, REPOSITORY) |
| `subject_id` | UUID | NOT NULL | SEID of the measured entity |
| `metric_name` | VARCHAR(50) | NOT NULL | Metric identifier |
| `metric_value` | REAL | NOT NULL | Computed value |
| `metadata` | JSONB | DEFAULT '{}' | Breakdown details |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Measurement timestamp |

**Indexes**:
- `idx_drift_subject` on `(subject_id, metric_name, commit_hash)`
- `idx_drift_repo_metric` on `(repository_id, metric_name)`

### Table: `drift_alerts`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Alert identifier |
| `repository_id` | UUID | FK → repositories, NOT NULL | Repository |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Triggering commit |
| `rule_name` | VARCHAR(50) | NOT NULL | Rule that fired |
| `severity` | VARCHAR(20) | NOT NULL | (INFO, WARNING, CRITICAL) |
| `subject_type` | VARCHAR(20) | NOT NULL | Subject of the alert |
| `subject_id` | UUID | NOT NULL | Subject entity SEID |
| `message` | TEXT | NOT NULL | Human-readable alert |
| `metric_snapshot` | JSONB | NOT NULL | Metric values at time of alert |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'open' | (open, acknowledged, resolved, suppressed) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Alert timestamp |

**Indexes**:
- `idx_drift_alerts_repo_status` on `(repository_id, status)`
- `idx_drift_alerts_severity` on `(severity, status)`

## 5.5 Historical Drift Tracking

Drift metrics are computed per commit (or per configurable interval — e.g., every 50 commits for large repositories). The `drift_metrics` table accumulates a time series for every (subject, metric) pair. This enables:

- **Drift Charts**: Plot coupling index of the billing package over the last 6 months.
- **Trend Analysis**: Is the architectural health of the repository improving or deteriorating?
- **Regression Detection**: Did a specific commit cause a significant metric regression?
- **Release Comparison**: Compare architectural metrics between releases v1.0 and v2.0.

---

# Section 6: Runtime Knowledge Graph

## 6.1 Motivation

The existing architecture analyzes source code **statically** — at rest, as written. But code behavior at runtime can differ dramatically from what static analysis reveals. Dynamic dispatch, runtime configuration, feature flags, and framework magic (dependency injection, middleware chains, ORM lazy loading) create runtime relationships invisible to static analysis.

The Runtime Knowledge Graph is designed as a **future extension** that captures actual runtime behavior and connects it to the static graph. This section specifies the architecture; integration is phased.

## 6.2 Runtime Ontology

### Runtime Entity Types

#### ServiceInstance

**Purpose**: Represents a running instance of a microservice or application.

**Attributes**:
- `id`: UUID.
- `service_name`: String. Logical service identifier.
- `repository_id`: UUID (nullable). Maps to the source code repository.
- `deployed_commit`: CHAR(40) (nullable). The commit hash deployed.
- `environment`: Enum. (production, staging, development).
- `first_observed`: Timestamp.
- `last_observed`: Timestamp.

#### RuntimeEndpoint

**Purpose**: Represents an API endpoint as actually invoked at runtime (vs. the APIEndpoint entity defined in static code).

**Attributes**:
- `id`: UUID.
- `service_instance_id`: FK → service_instances.
- `static_endpoint_seid`: UUID (nullable). Links to the statically-extracted APIEndpoint entity.
- `http_method`: Enum.
- `route_pattern`: String.
- `avg_latency_ms`: Float.
- `request_count`: Integer.
- `error_rate`: Float.

#### DatabaseInteraction

**Purpose**: Represents observed database queries and table accesses.

**Attributes**:
- `id`: UUID.
- `service_instance_id`: FK → service_instances.
- `table_name`: String.
- `operation`: Enum. (SELECT, INSERT, UPDATE, DELETE).
- `static_model_seid`: UUID (nullable). Links to DatabaseModel entity.
- `avg_latency_ms`: Float.
- `query_count`: Integer.

#### MessageQueueInteraction

**Purpose**: Represents observed message publish/consume patterns.

**Attributes**:
- `id`: UUID.
- `service_instance_id`: FK → service_instances.
- `queue_name`: String.
- `direction`: Enum. (PUBLISH, CONSUME).
- `message_count`: Integer.

### Runtime Relationship Types

#### RUNTIME_CALLS

**Meaning**: Service A made HTTP/RPC calls to Service B at runtime.

**Differs from static CALLS**: Static CALLS operates at the function level within a single process. RUNTIME_CALLS operates at the service level across network boundaries. They are complementary but distinct relationships.

**Direction**: Caller → Callee.

**Metadata**: Call count, average latency, error rate, protocol.

#### RUNTIME_READS / RUNTIME_WRITES

**Meaning**: A service reads from or writes to a specific database table.

**Differs from static READS/WRITES**: Static READS/WRITES tracks variable and field access within code. RUNTIME variants track actual database operations observed in production.

#### RUNTIME_PUBLISHES / RUNTIME_CONSUMES

**Meaning**: A service publishes to or consumes from a message queue.

## 6.3 Integration Strategy

### Static ↔ Runtime Linking

Runtime entities link to static entities through SEID references:
- `RuntimeEndpoint.static_endpoint_seid → entities.seid` (APIEndpoint)
- `DatabaseInteraction.static_model_seid → entities.seid` (DatabaseModel)
- `ServiceInstance.repository_id → repositories.id`
- `ServiceInstance.deployed_commit → commits.hash`

These links enable cross-graph queries: "This endpoint has 500 requests/second in production. Show me its static dependencies and what tests cover it."

### Data Ingestion Sources

The Runtime Graph is populated from:

1. **OpenTelemetry traces**: Extract service-to-service call graphs, latencies, and error rates.
2. **Database query logs**: Extract table access patterns.
3. **Message broker metrics**: Extract publish/consume patterns.
4. **APM tools**: Integrate with Datadog, New Relic, or Jaeger for trace data.

### Phasing

- **Phase 1 (current)**: No runtime graph. Static analysis only.
- **Phase 2**: Ingest OpenTelemetry traces to populate service-level call graph.
- **Phase 3**: Link runtime endpoints to static APIEndpoint entities.
- **Phase 4**: Full runtime graph with database and message queue interactions.

## 6.4 Runtime + Static Synergy

When both graphs are available, the system can answer queries impossible for either alone:

- **"Which code paths handle the highest traffic?"**: Runtime request counts mapped to static call graphs.
- **"What is the blast radius of this database migration?"**: Static DatabaseModel dependencies + Runtime service-level callers.
- **"This endpoint is slow. What code should I optimize?"**: Runtime latency → static handler → static call graph → identify hot paths.
- **"Are there dead endpoints?"**: Static APIEndpoints with no corresponding Runtime traffic.

---

# Section 7: Impact Prediction Engine

## 7.1 Motivation

The most actionable question in software engineering is: "What happens if I change this?" The Impact Prediction Engine answers this question by synthesizing evidence from multiple graph layers: structural dependencies, temporal co-change patterns, concept/capability memberships, and (when available) runtime call patterns.

## 7.2 Impact Assessment Dimensions

Impact is not a single score. It is a multi-dimensional assessment:

### Dimension 1: Structural Impact (Deterministic)

**Definition**: The set of entities that are statically reachable from the changed entity through dependency relationships.

**Computation**: Graph traversal from the changed entity following reverse CALLS, reverse IMPORTS, reverse DEPENDS_ON edges. With depth limiting.

**Scoring**: Each impacted entity receives a score inversely proportional to its hop distance from the change source.

```
structural_score(entity, source) = 1.0 / (1 + hop_distance(entity, source))
```

Entities at distance 1 (direct dependents) score 0.5. Distance 2 scores 0.33. Distance 3 scores 0.25. Entities beyond distance 5 are excluded.

### Dimension 2: Historical Co-Change Impact (Empirical)

**Definition**: Entities that have historically been modified alongside the changed entity.

**Computation**: Query `entity_versions` to find entities whose version records share the same `commit_hash` as any version of the changed entity. Compute co-change frequency:

```
cochange_score(A, B) = commits_where_both_changed / total_commits_where_A_changed
```

**Significance**: Co-change patterns reveal **hidden dependencies** not captured by static analysis. If entities A and B are always modified together but have no structural dependency, there is likely a semantic or business logic coupling between them.

**Scoring**: Co-change score directly (range 0.0 to 1.0). Entities with co-change score > 0.3 are flagged.

### Dimension 3: Concept/Capability Impact (Business-Level)

**Definition**: The concepts and business capabilities affected by the change.

**Computation**: Identify the concepts and capabilities the changed entity belongs to. Identify all other entities in the same concepts/capabilities. These entities are at elevated risk because they share business semantics.

**Scoring**: Entities in the same concept receive a base concept_impact_score of 0.3 (proximity within the concept affects this; entities that CALLS or IMPORTS the changed entity within the concept score higher).

### Dimension 4: Test Impact (Verification)

**Definition**: The tests that must be executed to verify the change.

**Computation**: Find all entities with TESTS relationships targeting the changed entity (direct tests). Find all entities in the structural impact set and collect their TESTS relationships (indirect tests).

**Scoring**: Tests are ranked by coverage relevance:
- Direct tests of the changed entity: priority 1.
- Tests of direct dependents: priority 2.
- Tests of transitive dependents: priority 3.

### Dimension 5: Runtime Impact (Operational, Future)

**Definition**: The runtime services and endpoints affected by the change.

**Computation**: Map the changed entity to runtime endpoints and services through the static-runtime linkage. Identify services that call the affected service. Weight by request volume.

**Scoring**: `runtime_score = normalized_request_volume × structural_score`.

## 7.3 Composite Impact Score

The final impact prediction for each potentially affected entity is a weighted composite:

```
impact_score(entity) =
    w_structural × structural_score +
    w_cochange   × cochange_score +
    w_concept    × concept_impact_score +
    w_runtime    × runtime_score

Default weights: w_structural=0.35, w_cochange=0.30, w_concept=0.15, w_runtime=0.20
```

If the Runtime Graph is not available, redistribute its weight to structural and co-change:
```
w_structural=0.40, w_cochange=0.40, w_concept=0.20
```

## 7.4 Risk Estimation

Beyond identifying *what* is impacted, the engine estimates *how risky* the impact is:

```
risk(entity) = impact_score(entity)
             × change_volatility(entity)
             × (1 - test_coverage(entity))
             × business_criticality(entity)
```

Where:
- `change_volatility`: How frequently this entity has changed recently. Frequently-changed entities are more fragile.
- `test_coverage`: Ratio of TESTS relationships to callable surface. Well-tested entities are less risky.
- `business_criticality`: Derived from the entity's capability mapping. Payment processing entities are more critical than logging utilities.

## 7.5 Impact Report Structure

An impact prediction produces a structured report:

```
ImpactReport:
  change_entity: SEID
  change_description: String
  timestamp: DateTime
  
  structural_impact:
    - entity: SEID, name, type
      distance: int
      path: [SEID chain showing dependency path]
      score: float
  
  historical_cochange:
    - entity: SEID, name, type
      cochange_frequency: float
      shared_commits: int
      score: float
  
  concept_impact:
    - concept: name
      affected_entities: int
      score: float
  
  capability_impact:
    - capability: name
      affected_entities: int
      business_risk: HIGH | MEDIUM | LOW
  
  test_impact:
    - test: SEID, name
      priority: int
      coverage_type: DIRECT | INDIRECT
  
  risk_summary:
    overall_risk: CRITICAL | HIGH | MEDIUM | LOW
    highest_risk_entities: [top 5 by risk score]
    untested_impacted_entities: [entities in impact set with no TESTS relationships]
    affected_api_endpoints: [list]
    affected_capabilities: [list]
```

## 7.6 Storage

Impact reports are stored for historical analysis (to later validate predictions against actual outcomes).

### Table: `impact_predictions`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Report identifier |
| `repository_id` | UUID | FK → repositories, NOT NULL | Repository |
| `trigger_seid` | UUID | FK → entities, NOT NULL | Entity being changed |
| `trigger_commit` | CHAR(40) | FK → commits, NULLABLE | Commit triggering analysis |
| `overall_risk` | VARCHAR(20) | NOT NULL | (CRITICAL, HIGH, MEDIUM, LOW) |
| `report_data` | JSONB | NOT NULL | Full structured report |
| `prediction_version` | VARCHAR(20) | NOT NULL | Algorithm version |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Prediction timestamp |

**Indexes**:
- `idx_impact_repo` on `(repository_id, created_at DESC)`
- `idx_impact_trigger` on `trigger_seid`

---

# Section 8: Software Intelligence Layer

## 8.1 Architecture Position

The Software Intelligence Layer is a new **top-level bounded context** that sits above all existing graph layers and intelligence subsystems. It does not own data — it orchestrates queries across subsystems and synthesizes results.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     CONSUMER LAYER                                       │
│          (APIs, Agents, Dashboards, IDE Extensions)                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                 SOFTWARE INTELLIGENCE LAYER                               │
│                                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Impact    │  │ Architecture │  │   Commit     │  │   Query     │  │
│  │ Prediction  │  │    Drift     │  │   Intent     │  │  Synthesis  │  │
│  │   Engine    │  │   Engine     │  │ Classifier   │  │   Engine    │  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                │                  │                 │          │
├─────────┼────────────────┼──────────────────┼─────────────────┼──────────┤
│         │                │                  │                 │          │
│  ┌──────▼──────────────────────────────────────────────────────▼──────┐  │
│  │                    INTELLIGENCE GRAPH LAYER                        │  │
│  │                                                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌─────────┐ │  │
│  │  │    Logic     │  │   Concept    │  │ Capability │  │ Runtime │ │  │
│  │  │  Evolution   │  │    Graph     │  │   Graph    │  │  Graph  │ │  │
│  │  │    Graph     │  │              │  │            │  │ (future)│ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  └─────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    FOUNDATION GRAPH LAYER (V2)                      │  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │  │
│  │  │  Structural  │  │   Semantic   │  │   Temporal   │              │  │
│  │  │    Graph     │  │    Graph     │  │    Graph     │              │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## 8.2 Responsibilities

The Software Intelligence Layer:

1. **Receives complex analytical questions** from the Consumer Layer (API, agents, dashboards).
2. **Decomposes questions** into sub-queries targeting specific graph layers.
3. **Executes sub-queries** against the appropriate subsystems.
4. **Synthesizes results** into coherent, multi-dimensional answers.
5. **Manages cross-cutting concerns**: caching, access control, result ranking, confidence aggregation.

Example decomposition for the question "How has authentication evolved and what is its current health?":

```
Sub-query 1 → Concept Graph:
  Find all entities in the "Authentication" concept.

Sub-query 2 → Logic Evolution Graph:
  For each Authentication entity, retrieve the LogicTransition chain.

Sub-query 3 → Architecture Drift Engine:
  Compute ConceptLeakage and CouplingIndex for Authentication entities.

Sub-query 4 → Temporal Graph:
  Retrieve entity version timeline for Authentication entities.

Sub-query 5 → Impact Prediction Engine:
  Compute the current blast radius of the Authentication concept.

Synthesis:
  Combine results into a structured AuthenticationEvolutionReport.
```

## 8.3 Interfaces

### Intelligence Query Interface

The primary interface exposed by the Software Intelligence Layer:

```
IntelligenceQuery:
  query_type: Enum
    - IMPACT_ANALYSIS
    - ARCHITECTURE_HEALTH
    - CONCEPT_EVOLUTION
    - CAPABILITY_OVERVIEW
    - COMMIT_ANALYSIS
    - TEMPORAL_COMPARISON
    - ENTITY_DEEP_DIVE
    - CROSS_CUTTING_ANALYSIS
  
  parameters: dict (query-type-specific parameters)
  
  filters:
    repository_id: UUID (optional)
    time_range: (start_commit, end_commit) or (start_date, end_date) (optional)
    concept_filter: String (optional)
    capability_filter: String (optional)
    entity_filter: SEID (optional)

IntelligenceResult:
  query_id: UUID
  confidence: float (overall result confidence)
  data: dict (query-type-specific structured result)
  evidence: list (links to supporting graph data)
  caveats: list (limitations or confidence warnings)
```

### Subsystem Query Interfaces

Each intelligence subsystem exposes a typed query interface consumed by the Software Intelligence Layer:

- `LogicEvolutionService.get_behavior_chain(seid) → BehaviorChain`
- `LogicEvolutionService.find_transitions_by_type(transition_type, repository_id) → list[LogicTransition]`
- `ConceptService.get_concept_members(concept_id, at_commit) → list[ConceptMembership]`
- `ConceptService.classify_entity(seid) → list[(Concept, confidence)]`
- `CapabilityService.get_capability_map(repository_id) → CapabilityHierarchy`
- `CapabilityService.get_capability_evolution(capability_id, time_range) → CapabilityTimeline`
- `CommitIntentService.classify_commit(commit_hash) → list[CommitIntent]`
- `CommitIntentService.find_commits_by_intent(intent_type, time_range) → list[Commit]`
- `DriftEngine.compute_metrics(repository_id, at_commit) → DriftMetricSet`
- `DriftEngine.get_alerts(repository_id, severity_filter) → list[DriftAlert]`
- `ImpactEngine.predict_impact(seid) → ImpactReport`

## 8.4 Bounded Context: Intelligence Orchestration

**Responsibility**: Decomposes high-level analytical questions into subsystem queries and synthesizes results.

**Ownership**: Owns `IntelligenceQuery`, `IntelligenceResult`, and `QueryDecomposition` aggregates.

**Boundaries**:
- Accepts: High-level analytical queries from the Consumer Layer.
- Produces: Synthesized, multi-dimensional results.
- Does NOT: Access database tables directly. All data access is through subsystem service interfaces.

**Dependencies**: All intelligence subsystems (Logic Evolution, Concept, Capability, Drift, Impact) + V2 foundational services (Retrieval Engine, Graph Engine).

## 8.5 Storage Architecture

The Intelligence Layer does not own persistent primary data. Each subsystem stores its own data (see storage schemas in Sections 1–5 and 7).

The Intelligence Layer maintains a **query result cache** for expensive analytical queries:

### Table: `intelligence_cache`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Cache entry identifier |
| `cache_key` | CHAR(64) | NOT NULL, UNIQUE | Hash of query parameters |
| `query_type` | VARCHAR(50) | NOT NULL | Query category |
| `repository_id` | UUID | NOT NULL | Repository scope |
| `valid_at_commit` | CHAR(40) | NOT NULL | Commit hash when result was computed |
| `result_data` | JSONB | NOT NULL | Cached result |
| `ttl_seconds` | INTEGER | NOT NULL | Time-to-live |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Cache entry creation |

**Invalidation**: Cache entries are invalidated when `valid_at_commit` no longer equals the repository's `last_analyzed_commit`. This ensures that after new commits are processed, stale intelligence results are not served.

---

# Section 9: RAG Integration Strategy

## 9.1 Motivation

The intelligence layers produce structured analytical results. RAG integration enables **natural language interaction** with this intelligence, allowing users to ask questions in plain English and receive answers grounded in graph evidence.

The key challenge in code-intelligence RAG is **context assembly**: selecting the right pieces of information from multiple graph layers to construct a context window that enables an LLM to produce an accurate, well-sourced answer.

## 9.2 RAG Pipeline Architecture

```
User Question
     │
     ▼
┌─────────────┐
│   Query     │ Classify question type, extract entities/concepts/time ranges
│ Understand  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieval  │ Execute parallel retrieval across applicable graph layers
│   Fan-Out   │
└──────┬──────┘
       │
       ├──▶ Graph-RAG (structural traversal)
       ├──▶ Temporal-RAG (version history)
       ├──▶ Concept-RAG (concept membership + evolution)
       ├──▶ Capability-RAG (business capability context)
       ├──▶ Impact-RAG (dependency impact chains)
       ├──▶ Vector-RAG (embedding similarity)
       │
       ▼
┌─────────────┐
│  Context    │ Merge, deduplicate, rank, and compress retrieved context
│  Assembly   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Response   │ LLM generates answer grounded in assembled context
│ Generation  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Evidence   │ Attach graph references as citations
│  Linking    │
└─────────────┘
```

## 9.3 Retrieval Pipeline Details

### Graph-RAG

**Trigger**: Questions about dependencies, relationships, architecture structure.

**Pipeline**:
1. Resolve mentioned entity names to SEIDs using fuzzy name matching.
2. Extract the local subgraph (N-hop neighborhood, default N=2) around the resolved entities.
3. Serialize the subgraph into a textual representation:

```
Entity: InvoiceProcessor (Class, billing/invoice.py)
  CALLS → TaxCalculator.compute_tax
  CALLS → DiscountEngine.apply_discounts
  IMPORTS → billing.models.Invoice
  EXTENDS → BaseProcessor
  BELONGS_TO → billing (Package)
```

4. Include entity summaries (from V2 semantic metadata) for each entity in the subgraph.

**Context Contribution**: Structural relationships, dependency chains, containment hierarchy.

### Temporal-RAG

**Trigger**: Questions about evolution, history, changes.

**Pipeline**:
1. Resolve time references ("last month", "since v2.0", "in the last 50 commits") to commit ranges.
2. Query `entity_versions` for entities modified within the range.
3. For each modified entity, retrieve:
   - Mutation type (CREATED, MODIFIED, RENAMED, MOVED, DELETED)
   - Logic transitions (from Logic Evolution Graph)
   - Diff summaries
4. Serialize into chronological narrative:

```
Timeline for InvoiceProcessor (last 3 months):
  2026-03-15 (commit abc123): MODIFIED - Added tax exemption handling
    Logic: CONTROL_FLOW_CHANGE - New conditional branch for tax-exempt orders
  2026-04-02 (commit def456): MODIFIED - Performance optimization
    Logic: PERFORMANCE_OPTIMIZATION - Batch database queries instead of N+1
  2026-04-18 (commit ghi789): RENAMED from InvoiceHandler to InvoiceProcessor
    Logic: BEHAVIOR_PRESERVING - No behavioral change
```

**Context Contribution**: Historical evolution, change reasons, temporal patterns.

### Concept-RAG

**Trigger**: Questions mentioning architectural concepts ("authentication", "caching", "error handling").

**Pipeline**:
1. Map the mentioned concept to the concept taxonomy.
2. Retrieve all entities belonging to that concept (with confidence ≥ 0.5).
3. For each entity, include: name, type, summary, key relationships.
4. Include concept-level metadata: concept drift score, entity count, primary packages.
5. If concept evolution is requested, include concept membership changes over time.

**Context Contribution**: Concept boundaries, member entities, concept health.

### Capability-RAG

**Trigger**: Questions mentioning business functions ("billing", "order management", "user registration").

**Pipeline**:
1. Map to capabilities.
2. Retrieve capability hierarchy and member entities.
3. Include capability-level dependencies.
4. Include capability evolution data if temporal dimension requested.

**Context Contribution**: Business-level context, capability boundaries, ownership.

### Impact-RAG

**Trigger**: Questions about consequences of changes, risk assessment, blast radius.

**Pipeline**:
1. Execute the Impact Prediction Engine for the referenced entity.
2. Serialize the impact report into structured text.
3. Highlight highest-risk entities, untested paths, and affected API endpoints.

**Context Contribution**: Impact chains, risk scores, test coverage gaps.

### Vector-RAG

**Trigger**: All questions (as a baseline retrieval mechanism).

**Pipeline**:
1. Embed the user's question.
2. Perform vector similarity search against entity embeddings.
3. Return top-K semantically similar entities.
4. Include their summaries and key relationships.

**Context Contribution**: Semantically relevant entities that may not be found through structural or concept-based retrieval.

## 9.4 Context Assembly

Multiple retrieval pipelines produce overlapping context fragments. The Context Assembly stage merges them:

### Deduplication
If the same entity appears in results from Graph-RAG and Concept-RAG, retain the richer representation (the one with more contextual information).

### Ranking

Each context fragment receives a relevance score:

```
relevance(fragment) =
    retrieval_score (from the pipeline that produced it)
  × source_weight (Graph-RAG: 0.35, Temporal: 0.25, Concept: 0.15, Impact: 0.15, Vector: 0.10)
  × freshness (entities modified recently score higher for "what changed" questions)
```

### Compression

LLM context windows are finite. If the assembled context exceeds the token budget:

1. **Tier the context**: Essential (top 20% by relevance), Supporting (next 40%), Background (bottom 40%).
2. **Summarize Background tier**: Replace full entity details with one-line summaries.
3. **Truncate Supporting tier**: Include relationships but omit source code.
4. **Preserve Essential tier**: Include full details.

### Context Window Structure

```
=== QUESTION CONTEXT ===

[Resolved Entities]
  The question references: InvoiceProcessor (Class), TaxCalculator (Class)

[Structural Context]
  InvoiceProcessor dependencies: ...
  TaxCalculator dependencies: ...

[Temporal Context]
  Recent changes to InvoiceProcessor: ...

[Concept Context]
  These entities belong to the Billing concept.
  Billing concept health: Coupling Index 0.45, no drift alerts.

[Impact Context]
  Changing InvoiceProcessor affects 12 entities, 3 API endpoints, 8 tests.

[Supporting Entities]
  DiscountEngine: Applies discount rules to invoice line items.
  Invoice (Model): Database model for invoice records.

=== END CONTEXT ===
```

## 9.5 Response Generation

The LLM receives the assembled context and the user's question. The system prompt instructs the LLM to:

1. Answer based exclusively on the provided context.
2. Cite specific entities, commits, or metrics when making claims.
3. Indicate uncertainty when the context is insufficient.
4. Distinguish between deterministic facts (from structural/temporal data) and probabilistic assessments (from AI-generated metadata).

## 9.6 Evidence Linking

The response includes citations linking back to specific graph data:

```
"The InvoiceProcessor class [1] was modified in commit abc123 [2] to add
tax exemption handling. This change affected the TaxCalculator [3], which
was also modified in the same commit to support the new exemption codes."

References:
[1] Entity: InvoiceProcessor (SEID: 550e8400...)
[2] Commit: abc123 (2026-03-15, author: Jane Developer)
[3] Entity: TaxCalculator (SEID: 6ba7b810...)
```

---

# Section 10: Architectural Review

## 10.1 Complexity Risks

### Risk: Intelligence Layer Combinatorial Complexity

**Description**: V3 adds 6 new subsystems, each with its own storage, computation pipeline, and query interface. The Software Intelligence Layer must orchestrate queries across all of them. The number of possible query decompositions grows combinatorially with the number of subsystems.

**Severity**: High.

**Mitigation**:
- Define a **fixed set of query types** (Section 8.3) with predetermined decomposition patterns. Do not allow arbitrary cross-subsystem queries initially.
- Each query type maps to a specific, tested decomposition template. New query types are added deliberately, not emergently.
- Implement circuit breakers: if a subsystem query exceeds its timeout (e.g., 5 seconds), the Intelligence Layer proceeds without that subsystem's results and annotates the response with a caveat.

### Risk: Classification Pipeline Maintenance

**Description**: Concept classification, capability mapping, commit intent classification, and logic transition classification all rely on heuristic rules and LLM prompts. These require ongoing tuning as new patterns emerge, languages are added, and LLM models change.

**Severity**: Medium.

**Mitigation**:
- Version all heuristic rules and prompt templates. Store version identifiers alongside classification results.
- Implement classification quality metrics: track the percentage of MANUAL overrides (indicating automated classification failures).
- Build a feedback loop: when users correct a classification, log the correction and use it to improve heuristic rules.
- Treat prompt templates as configuration, not code. Store them in a versioned configuration store, not hardcoded in application logic.

## 10.2 Storage Risks

### Risk: Table Proliferation

**Description**: V3 adds at minimum 10 new tables (`logic_signatures`, `logic_transitions`, `concepts`, `concept_memberships`, `capabilities`, `capability_mappings`, `commit_intents`, `drift_metrics`, `drift_alerts`, `impact_predictions`, `intelligence_cache`). Combined with V2's 9 tables, the system now has ~20 tables. Each table requires indexes, maintenance, backup, and migration management.

**Severity**: Medium.

**Mitigation**:
- Intelligence tables are **additive**. They do not modify V2 tables. A V2-only deployment remains fully functional.
- Intelligence tables can be deployed to a **separate database or schema** if operational isolation is desired.
- Implement a lifecycle policy: `drift_metrics` older than 1 year can be archived. `intelligence_cache` entries are ephemeral. `impact_predictions` older than 6 months can be compressed.

### Risk: JSONB Column Sprawl

**Description**: Multiple tables use JSONB columns for flexible metadata (`evidence`, `signals`, `report_data`, `metric_snapshot`). These are convenient but opaque to the database's query optimizer and difficult to enforce schemas on.

**Severity**: Medium.

**Mitigation**:
- Define Pydantic models for every JSONB structure. Validate at the application layer before writing.
- For frequently-queried JSONB fields, create **GIN indexes** or **generated columns** that extract specific values for indexing.
- Establish a convention: JSONB columns are for extensible metadata only. Fields that are queried in WHERE clauses must be promoted to dedicated columns.

## 10.3 Graph Explosion Risks

### Risk: Concept/Capability Classification Explosion

**Description**: If classification confidence thresholds are too low, every entity gets classified into multiple concepts and capabilities, creating a dense, noisy graph where concept boundaries lose meaning.

**Severity**: Medium.

**Mitigation**:
- Enforce a **maximum concepts per entity** limit (default: 3). If classification yields more than 3 concepts, keep only the top 3 by confidence.
- Require minimum confidence thresholds: 0.5 for concept membership, 0.6 for capability mapping.
- Periodically audit concept membership distribution. If the average entity belongs to more than 2 concepts, thresholds need tightening.

### Risk: Logic Signature Storage Volume

**Description**: If logic signatures are computed for every entity version, and a repository has 600,000 entity versions (per V2's storage estimates), the `logic_signatures` table grows to 600,000 rows. With a 1536-dimension behavioral embedding per row, embedding storage alone is 600,000 × 1536 × 4 bytes = 3.6 GB per repository.

**Severity**: High for large repositories.

**Mitigation**:
- Compute behavioral embeddings **only for entities where the logic fingerprint changed**. If an entity was modified but its control_flow_hash and data_flow_hash are unchanged (behavior-preserving refactoring), skip the expensive embedding computation. Copy the previous embedding. Estimated reduction: 60–70% of versions.
- Apply tiered retention: full logic signatures for the last N versions (e.g., 20). For older versions, retain only the fingerprint hashes and transition classifications, discarding the behavioral embedding.
- Partition `logic_signatures` by repository and apply per-repository retention policies.

## 10.4 Classification Accuracy Risks

### Risk: LLM Classification Drift

**Description**: LLM-based classifications (logic transitions, concept classification, commit intent) may shift when the LLM model is updated. A function classified as "SECURITY_HARDENING" by GPT-4o may be classified as "ALGORITHM_CHANGE" by a future model.

**Severity**: Medium.

**Mitigation**:
- Store `model_identifier` and `prompt_version` with every LLM-generated classification.
- When the model changes, do NOT retroactively reclassify all historical data. The historical record reflects the classification at the time it was generated.
- Provide a "reclassify" API that can be triggered to reprocess specific entities or commits with the current model, creating new classification records alongside (not replacing) the old ones.
- Use deterministic methods (CFG diff, data flow fingerprint, keyword matching) as the primary classification signal. LLM is the fallback, not the primary. This limits the blast radius of LLM drift.

### Risk: Concept Taxonomy Mismatch

**Description**: The predefined concept taxonomy may not match a specific codebase's architecture. An embedded systems codebase has concepts (interrupt handling, memory management, hardware abstraction) that don't appear in the default taxonomy. A web application codebase may have concepts not in the taxonomy (WebSocket management, SSR).

**Severity**: Medium.

**Mitigation**:
- Allow user-defined concepts. The taxonomy is a starting point, not a constraint.
- Implement concept discovery: periodically scan for clusters of entities that are structurally connected and semantically similar but don't match any existing concept. Present these clusters to the user as candidate concepts.
- The LLM classification step should be allowed to propose new concepts outside the taxonomy, with a `is_system_defined = FALSE` flag.

## 10.5 Maintenance Risks

### Risk: Pipeline Ordering Dependencies

**Description**: The intelligence subsystems have implicit ordering dependencies. Logic Evolution depends on entity versions (V2 temporal graph). Concept classification depends on entity extraction (V2). Drift metrics depend on concept classification (V3). Capability mapping may depend on concept classification. Impact prediction depends on drift metrics and co-change analysis.

If any upstream pipeline fails or is delayed, downstream intelligence may be stale or missing.

**Severity**: Medium.

**Mitigation**:
- Define an explicit **pipeline dependency graph** and a pipeline orchestrator that respects ordering.
- Each intelligence subsystem must be **idempotent and restartable**. If concept classification fails midway, it can be rerun from the beginning without corrupting existing data.
- Each subsystem exposes a **health check** indicating whether its data is current relative to the latest analyzed commit. The Intelligence Layer checks health before serving results and annotates responses with staleness warnings.

```
Pipeline Order:
  1. V2: Ingestion → Parsing → Extraction → Graph Building → Temporal Versioning
  2. V3-a (can run in parallel):
     - Logic Evolution (depends on: entity_versions)
     - Commit Intent Classification (depends on: commits, entity_versions)
  3. V3-b (depends on V3-a):
     - Concept Classification (depends on: entities, logic_signatures)
     - Capability Mapping (depends on: entities, concept_memberships)
  4. V3-c (depends on V3-b):
     - Drift Metrics (depends on: entities, relationships, concept_memberships)
     - Impact Prediction (depends on: all above)
  5. V3-d (independent, on-demand):
     - Intelligence Query Cache Warming
```

## 10.6 Cost Risks

### Risk: LLM API Cost Explosion

**Description**: V3 introduces four LLM-dependent pipelines: logic transition classification (Step 4 of the cascade), concept classification (Tier 4), capability discovery (Strategy 3), and commit intent classification (Signal 4). For a repository with 30,000 entities, 50,000 commits, and 20 versions per entity, the potential LLM calls number in the hundreds of thousands.

**Severity**: High if unmanaged.

**Mitigation**:
- The cascading pipeline design ensures LLM is the **last resort**, not the default. Estimated LLM invocation rate:
  - Logic transitions: ~15% of modifications reach LLM (after CFG + data flow + embedding filtering).
  - Concept classification: ~10% of entities reach LLM (after heuristic + propagation + embedding).
  - Commit intent: ~20% of commits reach LLM (after message + file + mutation signals).
- Implement **budget controls**: configurable per-repository LLM API call budget per pipeline run. When budget is exhausted, remaining entities are classified as "UNCLASSIFIED" with a flag indicating budget exhaustion.
- Batch LLM calls where possible. Classify 10 entities in a single prompt rather than one entity per prompt.
- Use cheaper models (e.g., GPT-4o-mini, Claude Haiku) for classification tasks and reserve expensive models for nuanced analysis.
- Cache LLM responses keyed by input hash. If an entity's content hash has not changed, its cached classification remains valid.

---

This concludes the Architecture V3 specification. The document extends the V2 foundation with six intelligence subsystems (Logic Evolution Graph, Concept Graph, Business Capability Graph, Commit Intent Classification, Architecture Drift Engine, Runtime Knowledge Graph), a predictive Impact Prediction Engine, a Software Intelligence orchestration layer, and a multi-pipeline RAG integration strategy. All designs preserve full backward compatibility with V2 and introduce no breaking changes to the existing schema.
