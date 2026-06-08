# Temporal Code Knowledge Graph Platform
# Architecture V4: Concept Graph & Concept Intelligence Layer

**Version**: 4.0  
**Status**: Authoritative Reference Specification  
**Review Panel**: Distinguished Software Architect, Principal Knowledge Graph Architect, Principal Software Intelligence Researcher, Principal Domain Driven Design Architect, Principal Program Analysis Engineer, Principal RAG Architect, Principal Static Analysis Researcher, Principal Database Architect, Principal Systems Engineer  

---

## Preamble

Architecture V3 extended the platform with a **Behavior Graph** (`LogicSignature`, `LogicVersion`, `LogicEvidence`), defining *what the code does* on a detailed AST and data-flow level. 

**Architecture V4** introduces the **Concept Graph & Concept Intelligence Layer**. This layer shifts the platform's understanding from individual program behaviors to aggregate software capabilities. It defines *what software capabilities exist*, mapping low-level behavior patterns to high-level domain concepts (e.g., mapping bcrypt checkpw calls and OAuth token checks to an overarching "Authentication" capability).

Crucially, Concept Graph operations—including classification, relation mapping, clustering, and drift analysis—are designed to be **deterministic, explainable, testable, and auditable**. To preserve reproducibility and compliance, **no Large Language Models (LLMs) are used in the core concept detection pipeline**. High-level AI features (such as generating human-readable narrative explanations or semantic searches) are isolated to optional enrichment layers, ensuring that the base code capability map remains fully verifiable.

---

# Table of Contents

1. [Architectural Review & Integration Points](#section-1-architectural-review)
2. [Concept Domain Model](#section-2-concept-domain-model)
3. [Concept Ontology Schema & Registry](#section-3-concept-ontology)
4. [Concept Detection Engine](#section-4-concept-detection-engine)
5. [Concept Evidence Model & Aggregation](#section-5-concept-evidence-model)
6. [Concept Clustering Engine](#section-6-concept-clustering-engine)
7. [Concept Relationship Engine](#section-7-concept-relationship-engine)
8. [Concept Evolution & Metrics Engines](#section-8-concept-evolution-engine)
9. [Concept Drift Engine](#section-9-concept-drift-engine)
10. [Concept Explanation Engine](#section-10-concept-explanation-engine)
11. [Graph Schema & Traversal Extensions](#section-11-graph-extensions)
12. [Relational Database Schema Design](#section-12-database-design)
13. [Application Service Architecture](#section-13-application-services)
14. [API Gateway & Route Contracts](#section-14-api-design)
15. [Observability & Performance Telemetry](#section-15-observability)
16. [Benchmark Suite & Ground Truth Scenarios](#section-16-benchmark-suite)
17. [Validation Framework & Calibration Metrics](#section-17-validation-framework)
18. [Scalability & High-Volume Systems Review](#section-18-scalability-review)
19. [Phase 4 Directory & System Architecture Map](#section-19-phase-4-final-architecture)
20. [Phase 5+ Readiness & Downstream Path](#section-20-phase-5-readiness-review)

---

# Section 1: Architectural Review

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Phase 4: Concept Graph                          │
│                                                                        │
│  ┌───────────────┐      ┌─────────────────┐      ┌──────────────────┐  │
│  │  ConceptNode  │◄────►│ ConceptVersion  │◄────►│  ConceptCluster  │  │
│  └───────┬───────┘      └────────┬────────┘      └──────────────────┘  │
│          │                       │                                     │
│          ▼                       ▼                                     │
│  ┌───────────────┐      ┌─────────────────┐      ┌──────────────────┐  │
│  │ConceptRelation│      │ ConceptEvidence │◄────►│  ConceptMetrics  │  │
│  └───────────────┘      └────────┬────────┘      └──────────────────┘  │
└──────────────────────────────────┼─────────────────────────────────────┘
                                   │ (Integrates with Phase 3)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Phase 3: Behavior Graph                         │
│                                                                        │
│  ┌──────────────────────┐       ┌──────────────────────┐               │
│  │    LogicSignature    │◄─────►│     LogicVersion     │               │
│  └──────────────────────┘       └──────────┬───────────┘               │
│                                            │                           │
│                                            ▼                           │
│                                 ┌──────────────────────┐               │
│                                 │    LogicEvidence     │               │
│                                 └──────────────────────┘               │
└────────────────────────────────────────────────────────────────────────┘
```

## 1.1 Existing Phases Integration

* **Phase 1 (Structural Graph)**: Provides the base structural layout of the codebase. A `ConceptVersion` resolves to a collection of physical source entities (`Module`, `Class`, `Function`) by traversing their stable Entity IDs (`SEID`).
* **Phase 2 (Temporal Graph)**: Dictates how temporal diffing and historical reconstruction work. The Concept Graph hooks into `ChangeEvent` triggers. When a commit modifies source code, the system triggers concept re-detection on affected entities.
* **Phase 2.5 (Validation Layer)**: Integrates the confidence verification. Concept detection confidence scores are mathematically bound to the source code entity confidence scores.
* **Phase 3 (Behavior Graph)**: The primary input feed for Phase 4. `LogicVersion` and `LogicEvidence` nodes represent the compiled behaviors. `BehaviorPattern` structures are matched to AST features. The Phase 4 engine maps these behavior patterns directly to ontology-defined concepts.

## 1.2 Extension & Integration Points

* **Post-Ingestion Concept Pipeline Hook**: Run as a transaction-enclosed task immediately following the completion of Phase 3 behavior scanning.
* **Ontology Matching Extensibility**: The `OntologyNode` entity established in Phase 3 is mapped 1:1 or N:1 into high-level `ConceptNode` entities.
* **Auditable Mapping Register**: Concept detection does not alter Phase 3 database records. Instead, it creates `ConceptEvidence` links which serve as clean, auditable join-tables.

---

# Section 2: Concept Domain Model

Every domain object in the Concept Graph is designed using Clean Architecture principles, ensuring persistence-ignorance and strict invariants.

## 2.1 ConceptNode
* **Responsibilities**: Represents a stable, unique, and long-lived software capability identified in a repository (e.g., "Authentication Service").
* **Invariants**: 
  * Must be uniquely identified by a deterministic UUID derived from the repository ID and the primary concept ontology node identifier.
  * Canonical name cannot be empty.
* **Lifecycle**: Created when a concept is first detected in a commit. Persists indefinitely, even if a commit temporarily removes all implementing code (transitioning its version status to `INACTIVE`).
* **Storage Requirements**: Maps to the `concept_nodes` table.

## 2.2 ConceptVersion
* **Responsibilities**: Represents a point-in-time snapshot of a Concept's state and size at a specific Git commit.
* **Invariants**:
  * Must be associated with a valid `ConceptNode`.
  * `version_number` must be a monotonically increasing integer starting at 1.
  * `confidence` must be a float clamped strictly between $0.05$ and $1.00$.
* **Lifecycle**: Generated when a commit introduces behavioral modifications or structural adjustments to any code entity that serves the parent concept.
* **Storage Requirements**: Maps to the `concept_versions` table.

## 2.3 ConceptEvidence
* **Responsibilities**: Serves as the granular, audit-trail binding that connects a `ConceptVersion` to the underlying behavioral evidence.
* **Invariants**:
  * Must point to a valid `ConceptVersion`.
  * Must reference a concrete target (e.g., a specific `LogicVersion` or `LogicEvidence` UUID).
  * `confidence_contribution` must be a float between $0.0$ and $1.0$.
* **Lifecycle**: Immutable once written. Created in batches alongside a new `ConceptVersion`.
* **Storage Requirements**: Maps to the `concept_evidence` table.

## 2.4 ConceptRelationship
* **Responsibilities**: Tracks dependency, implementation, and semantic relationships between concepts at a specific commit.
* **Invariants**:
  * Cannot link a concept to itself.
  * Must have an explicit `relationship_type` (e.g., `DEPENDS_ON`).
* **Lifecycle**: Generated during concept extraction at a commit. Deleted or updated if the dependency graph changes in subsequent commits.
* **Storage Requirements**: Maps to the `concept_relationships` table.

## 2.5 ConceptCluster
* **Responsibilities**: Represents a high-level grouping of related concepts (e.g., grouping "Authentication", "Authorization", and "Session Management" under "Identity & Access Management").
* **Invariants**:
  * Cluster key must be unique and human-readable.
  * Cohesion score must be in $[0.0, 1.0]$.
* **Lifecycle**: Updated dynamically by the clustering engine as concepts evolve.
* **Storage Requirements**: Maps to the `concept_clusters` table.

## 2.6 ConceptExplanation
* **Responsibilities**: Houses the deterministic, structured breakdown of why a concept exists and how it is composed.
* **Invariants**:
  * Associated 1:1 with a `ConceptVersion`.
* **Lifecycle**: Generated concurrently with the `ConceptVersion`.
* **Storage Requirements**: Maps to the `concept_explanations` table.

## 2.7 ConceptEvolution
* **Responsibilities**: Documents transition edges between successive versions of a concept, recording how a concept was created, modified, split, or merged.
* **Invariants**:
  * Similarity score must be in $[0.0, 1.0]$.
* **Lifecycle**: Generated by comparing a new `ConceptVersion` with its historic predecessor(s).
* **Storage Requirements**: Maps to the `concept_evolution` table.

## 2.8 ConceptMetrics
* **Responsibilities**: Holds structural importance, size, and topological graph centrality scores for a `ConceptVersion`.
* **Invariants**:
  * PageRank and centrality scores must be non-negative.
  * Must be associated 1:1 with a `ConceptVersion`.
* **Lifecycle**: Generated after concept relationship extraction at each commit by analyzing the concept dependency graph.
* **Storage Requirements**: Maps to the `concept_metrics` table.

---

# Section 3: Concept Ontology

The concept ontology is structured as a hierarchical taxonomy stored externally in a versioned YAML schema. This isolates the taxonomy configuration from Python code updates, facilitating audits and hot-swaps.

## 3.1 Taxonomy Hierarchy

```
SYSTEM
├── Security
│   ├── Authentication
│   ├── Authorization
│   ├── Encryption
│   └── SecretManagement
├── DataManagement
│   ├── Persistence
│   ├── Caching
│   ├── Serialization
│   └── Migration
├── Communication
│   ├── APIIntegration
│   ├── Messaging
│   └── EventPublishing
└── Reliability
    ├── RetryLogic
    ├── CircuitBreaker
    └── RateLimiting
```

## 3.2 YAML Schema Specification (`ontology/concepts.yaml`)

```yaml
schema_version: "4.0"
ontology_version: "4.1.0"
last_updated: "2026-06-07T12:00:00Z"

domains:
  - id: security
    name: Security
    description: "Mechanisms enforcing data protection, identity validation, and access control."
    concepts:
      - id: security.authentication
        name: Authentication
        description: "Verification of user, service, or system identities."
        required_patterns:
          - auth_bcrypt_verification
          - auth_sha256_verification
          - auth_jwt_verification
          - auth_argon2_verification
          - auth_passlib_verify
        optional_patterns:
          - auth_bcrypt_hash
          - auth_jwt_generation
          - auth_direct_compare
        min_base_confidence: 0.80

      - id: security.authorization
        name: Authorization
        description: "Enforcement of permission-based and role-based access rights."
        required_patterns:
          - authz_permission_check
          - authz_rbac
        min_base_confidence: 0.75

  - id: data_management
    name: Data Management
    description: "Data lifecycle, transactions, and retrieval mechanisms."
    concepts:
      - id: data_management.caching
        name: Caching
        description: "High-performance memory buffers and distributed lookups."
        required_patterns:
          - cache_memory_dict
          - cache_lru_cache
          - cache_redis_lookup
          - cache_redis_set
        optional_patterns:
          - cache_redis_cluster
          - cache_invalidation
        min_base_confidence: 0.70
```

## 3.3 Verification & Validation Logic
1. **Schema Check**: Validated against a strict JSON Schema using a pre-commit compiler hook.
2. **Cycle Detection**: The parent-child tree is parsed as a directed graph. Any cycle (e.g., $A \to B \to A$) triggers an immediate validation failure (`OntologyLoadException`).
3. **Pattern Verification**: Every pattern listed in `required_patterns` or `optional_patterns` must correspond to a registered pattern in `BehaviorPattern` database records.

---

# Section 4: Concept Detection Engine

The `ConceptDetectionEngine` performs deterministic, rule-based extraction. It does not use stochastic machine learning or LLMs.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ConceptDetectionEngine                          │
│                                                                        │
│                      ┌──────────────────────────┐                      │
│                      │  1. Logic Scan Reader    │                      │
│                      └────────────┬─────────────┘                      │
│                                   │ (Active LogicVersions)             │
│                                   ▼                                    │
│                      ┌──────────────────────────┐                      │
│                      │  2. Ontology Node Mapper │                      │
│                      └────────────┬─────────────┘                      │
│                                   │ (Filter by ontology_node_id)       │
│                                   ▼                                    │
│                      ┌──────────────────────────┐                      │
│                      │  3. Confidence Evaluator │                      │
│                      └────────────┬─────────────┘                      │
│                                   │ (Weighted Aggregation)             │
│                                   ▼                                    │
│                      ┌──────────────────────────┐                      │
│                      │  4. Concept Graph Writer │                      │
│                      └──────────────────────────┘                      │
└────────────────────────────────────────────────────────────────────────┘
```

## 4.1 Concept Classification Algorithm

For a given repository $R$ and commit $C$, the classification algorithm runs as follows:

1. **Fact Retrieval**: Query all active `LogicVersion` records at commit $C$. Identify all associated `LogicEvidence` nodes.
2. **Taxonomy Alignment**: Map the `ontology_node_id` of each `LogicVersion` to the target concept defined in the YAML ontology.
3. **Grouping**: Group the active `LogicVersion` nodes by their target concept ID:
   $$V_{concept} = \{ v \in \text{LogicVersions} \mid \text{OntologyMap}(v.\text{ontology\_node\_id}) = \text{concept\_id} \}$$
4. **Invariant Thresholding**: A concept is declared **detected** if and only if:
   * At least one `LogicVersion` matches a pattern in the ontology's `required_patterns` list.
   * The aggregated confidence score exceeds the ontology's `min_base_confidence` threshold.

## 4.2 Confidence Calibration & Evidence Diversity

To prevent artificial inflation from repeated identical evidence types, we implement a discounted diversity calibration.

Let $E = \{e_1, e_2, \dots, e_n\}$ be the set of active evidence nodes supporting a concept version. Let $T(e)$ be the evidence type (e.g. pattern ID). Let $U = \{T(e) \mid e \in E\}$ be the set of unique evidence types.

We partition the evidence into subsets by type: $E_t = \{e \in E \mid T(e) = t\}$ for each $t \in U$.

For each unique evidence type $t$, we compute a consolidated type-level confidence $c_t$ by sorting elements in $E_t$ by their individual confidence descending, and applying a step-down decay factor $\alpha = 0.5$ for repeated items:

$$c_t = 1 - \prod_{j=0}^{|E_t|-1} (1 - c(e_{t, j}) \cdot \alpha^j)$$

where:
* $e_{t, j}$ is the $j$-th evidence node of type $t$ (sorted descending by confidence).
* $c(e_{t, j})$ is the raw confidence score.

The overall joint confidence is then computed via a standard Noisy-OR over the unique type-level scores:

$$C_{\text{final}} = \min\left(1 - \prod_{t \in U} (1 - c_t), \, \max_{e \in E}(c(e)) + (1 - \max_{e \in E}(c(e))) \times 0.25 \right)$$

This ensures that finding 4 instances of `auth_bcrypt_verification` does not inflate confidence as much as finding 1 `auth_bcrypt_verification` + 1 `auth_jwt_verification` + 1 `authz_rbac` match.

---

# Section 5: Concept Evidence Model

Every detected concept must write an explicit audit trail. The `concept_evidence` record provides the deterministic chain.

## 5.1 Evidence Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ConceptEvidencePayload",
  "type": "object",
  "properties": {
    "evidence_type": {
      "type": "string",
      "enum": ["LOGIC_VERSION", "LOGIC_EVIDENCE", "ONTOLOGY_NODE_MATCH"]
    },
    "trigger_facts": {
      "type": "object",
      "properties": {
        "file_path": { "type": "string" },
        "line_range": {
          "type": "array",
          "prefixItems": [
            { "type": "integer" },
            { "type": "integer" }
          ]
        },
        "matched_ast_node": { "type": "string" },
        "pattern_id": { "type": "string" }
      },
      "required": ["file_path", "pattern_id"]
    },
    "confidence_calculation": {
      "type": "object",
      "properties": {
        "base_weight": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "contributing_factor": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      },
      "required": ["base_weight", "contributing_factor"]
    }
  },
  "required": ["evidence_type", "trigger_facts", "confidence_calculation"]
}
```

## 5.2 Storage Strategy
* `ConceptEvidence` is stored as structured records in the relational database.
* To support audits, the `trigger_facts` field stores the exact, immutable AST information at the time of commit compilation. This allows users to inspect the exact lines of code that generated the concept classification.

---

# Section 6: Concept Clustering Engine

Concepts represent granular technical concerns. The `ConceptClusterEngine` groups these concerns into unified, high-level structural domains.

## 6.1 Clustering Strategy

The clustering engine operates on two cooperative mechanisms:

1. **Ontology Domain Groups (Static)**: Concepts belonging to the same ontology domain (e.g. `security.authentication` and `security.authorization`) are mapped to the same domain cluster (`Identity & Access Management`).
2. **Structural Co-membership Coupling (Dynamic)**: If two concepts $C_A$ and $C_B$ consistently share code files or invoke each other's functions, they are candidates for dynamic clustering. We compute the **Jaccard coupling coefficient** of their active file paths:

$$J(C_A, C_B) = \frac{|F(C_A) \cap F(C_B)|}{|F(C_A) \cup F(C_B)|}$$

where $F(C)$ is the set of source files containing code entities mapped to concept $C$. 

If $J(C_A, C_B) \ge 0.40$, the engine registers a dynamic cluster linking the two concepts, assigning a cluster label derived from their shared ontology domain.

## 6.2 Cluster Lifecycle & Evolution
* **Creation**: Instantiated when a cluster membership is identified.
* **Cohesion Drift**: If $J(C_A, C_B)$ falls below $0.20$ over multiple commits, the cluster **splits** back into separate concepts.
* **Centroid Tracking**: The concept with the highest internal node-degree centrality (most dependencies) is declared the **Cluster Centroid**.

> [!NOTE]
> *Phase 5 Roadmap*: In Phase 5, the clustering framework will be extended to support dynamic topological algorithms such as **Louvain Modularity** and **Community Detection** directly over the dependency relationship graph. The Phase 4 model provides the necessary foundation.

---

# Section 7: Concept Relationship Engine

The relationship engine infers directed semantic links between concept nodes at each commit.

## 7.1 Relationship Inference Rules

* **`IMPLEMENTS`**: Deduced when an entity version belonging to Concept $C_A$ is an abstract class or interface, and the entity version belonging to $C_B$ inherits from it.
* **`DEPENDS_ON`**: Deduced from imports and calls. If code entities in $C_A$ import modules or call functions inside $C_B$, a dependency exists:
  $$\text{Dependency Score}(C_A \to C_B) = \frac{\sum_{u \in C_A} \text{Calls}(u \to C_B)}{\text{Total Calls}(C_A)}$$
  If the Dependency Score $\ge 0.15$, a `DEPENDS_ON` relationship is created.
* **`REPLACES`**: Deduced when a new concept $C_B$ is introduced, and the existing concept $C_A$ loses all code members at the exact same commit, provided both share the same parent domain.

## 7.2 Confidence Calculation for Relationships

The confidence of an inferred relationship $R_{AB}$ is a product of the source concepts' confidence scores and the coupling strength:

$$\text{Conf}(R_{AB}) = \text{Conf}(C_A) \times \text{Conf}(C_B) \times \text{Coupling}(A, B)$$

Where $\text{Coupling}(A, B)$ is the normalized dependency or inheritance score in $[0.0, 1.0]$.

---

# Section 8: Concept Evolution & Metrics Engines

The engine tracks both chronological changes and graph topology scores over successive commits.

```
Commit C-1                   Commit C (Current)
┌──────────────┐             ┌──────────────┐
│Authentication│             │Authentication│
│Version 1     │             │Version 2     │
└──────┬───────┘             └──────▲───────┘
       │                            │
       └───── CONCEPT_EVOLVED_TO ───┘ (Transition: Splitting / Modification)
```

## 8.1 Transition Classifications
* **`CONCEPT_CREATION`**: First appearance of a concept in the commit timeline.
* **`CONCEPT_MODIFICATION`**: A change in code implementation size or confidence, but the underlying core entities remain highly stable (Jaccard similarity of entity IDs $\ge 0.70$).
* **`CONCEPT_SPLIT`**: Occurs when a single concept version at $C_{t-1}$ partitions its entities into two distinct concept versions at $C_t$. Detected when:
  * $E(C_{t-1})$ is split such that $\ge 30\%$ of its elements go to $C_{A, t}$ and $\ge 30\%$ go to $C_{B, t}$.
* **`CONCEPT_MERGE`**: The inverse of a split. Multiple concepts coalesce into one.
* **`CONCEPT_REMOVAL`**: The code implementing the concept is completely deleted. The status transitions to `INACTIVE`.

## 8.2 State Transition Matrix

| From State | Event | To State | Transition Type |
| :--- | :--- | :--- | :--- |
| `NULL` | Ingestion of concept code | `ACTIVE` | `CONCEPT_CREATION` |
| `ACTIVE` | Modification of entities (Jaccard $\ge 0.7$) | `ACTIVE` | `CONCEPT_MODIFICATION` |
| `ACTIVE` | Structural division (Jaccard $\le 0.4$) | `ACTIVE` (Multi) | `CONCEPT_SPLIT` |
| `ACTIVE` | Complete deletion of entities | `INACTIVE` | `CONCEPT_REMOVAL` |

## 8.3 Concept Metrics Engine

The `ConceptMetricsEngine` runs immediately following concept detection and relationship mapping at each commit. It analyzes the concept dependency graph $G_c = (V_c, E_c)$ to compute centrality, structural footprint, and systemic impact.

### 1. Concept Size Metrics
* **Entity Count**: $|SEID(V_c)|$, the count of unique code entities (functions, classes) mapping to the concept.
* **File Count**: $|F(V_c)|$, the count of unique files containing these entities.

### 2. Centrality Metrics
* **Degree Centrality**: Computes normalize in-degree ($k_{in}$) and out-degree ($k_{out}$) values over the graph:
  $$C_{Deg}(v) = \frac{k_{in}(v) + k_{out}(v)}{|V_c| - 1}$$
* **PageRank Score**: Derived via power iteration over the concept dependency matrix:
  $$PR(v) = \frac{1 - d}{|V_c|} + d \sum_{u \in In(v)} \frac{PR(u)}{OutDegree(u)}$$
  where damping factor $d = 0.85$.
* **Betweenness Centrality**: Measures how frequently node $v$ lies on shortest paths between other concepts:
  $$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

### 3. Impact Score
Quantifies the downstream cascade risk if this concept's behavior drifts:
$$\text{Impact}(v) = \sum_{u \in \text{TransitiveDependents}(v)} \text{LinkConfidence}(u \to v) \times \text{Size}(u)$$

All calculated values are stored in the `concept_metrics` table per `ConceptVersion`.

---

# Section 9: Concept Drift Engine

Concept Drift measures how a concept's behavioral boundaries shift over time. 

## 9.1 Multi-Dimensional Drift Formulation

Drift is calculated by comparing `ConceptVersion` $V_1$ at commit $C_1$ to $V_2$ at commit $C_2$. The overall drift score $D_{\text{concept}} \in [0.0, 1.0]$ is computed as a weighted sum of three distinct dimensions:

$$D_{\text{concept}} = w_s \cdot \text{Drift}_{\text{structural}} + w_p \cdot \text{Drift}_{\text{pattern}} + w_d \cdot \text{Drift}_{\text{dependency}}$$

where:
* $w_s = 0.4$, $w_p = 0.4$, $w_d = 0.2$ (weights summing to $1.0$).

### 1. Structural Drift
Measures the change in the set of source entities (SEIDs) implementing the concept:

$$\text{Drift}_{\text{structural}} = 1 - \frac{|SEID(V_1) \cap SEID(V_2)|}{|SEID(V_1) \cup SEID(V_2)|}$$

### 2. Pattern Drift
Measures the change in matching behavioral pattern signatures:

$$\text{Drift}_{\text{pattern}} = 1 - \frac{|Patterns(V_1) \cap Patterns(V_2)|}{|Patterns(V_1) \cup Patterns(V_2)|}$$

### 3. Dependency Drift
Measures the change in external calls and imports:

$$\text{Drift}_{\text{dependency}} = 1 - \frac{|Deps(V_1) \cap Deps(V_2)|}{|Deps(V_1) \cup Deps(V_2)|}$$

## 9.2 Drift Categorization Thresholds

| Drift Score Range | Category | Architectural Assessment |
| :--- | :--- | :--- |
| $0.00 \le D < 0.10$ | `TRIVIAL` | Routine maintenance or cosmetic changes. |
| $0.10 \le D < 0.30$ | `MINOR` | Refactoring or small behavior updates. |
| $0.30 \le D < 0.60$ | `SIGNIFICANT` | Notable feature additions or pattern swaps. |
| $0.60 \le D < 0.85$ | `MAJOR` | Architectural restructure (e.g. changing DB engines). |
| $0.85 \le D \le 1.00$ | `COMPLETE` | Total conceptual replacement. |

---

# Section 10: Concept Explanation Engine

The `ConceptExplanationEngine` generates deterministic, auditable, and structured explanations details without calling external LLM services.

## 10.1 Structured Breakdown Schema

```json
{
  "concept_id": "c76b066c-b143-4c84-9210-20ff08488763",
  "name": "Authentication",
  "commit_hash": "304cbdd0ec926f523580c7278c632ba787359397",
  "confidence_score": 0.94,
  "explanation_summary": "Authentication capability is verified with high confidence (94%) based on 3 active cryptographic and token behaviors across 2 modules.",
  "evidence_breakdown": {
    "primary_triggers": [
      {
        "pattern_id": "auth_bcrypt_verification",
        "entity_seid": "func:auth.verify_password",
        "file_path": "src/services/auth.py",
        "confidence": 0.95
      },
      {
        "pattern_id": "auth_jwt_verification",
        "entity_seid": "func:jwt_helper.decode_token",
        "file_path": "src/utils/jwt_helper.py",
        "confidence": 0.92
      }
    ],
    "structural_footprint": {
      "file_count": 2,
      "class_count": 0,
      "function_count": 2,
      "loc_estimate": 45
    }
  }
}
```

## 10.2 Generation Rules
* **Deterministic Assembly**: The explanation summary is constructed using pre-defined string templates populated directly from database statistics (e.g., number of active patterns, active files, and calculated confidence).
* **Audit Compliance**: Because the summary is generated deterministically, running the engine over the same database state always yields identical explanation strings.

---

# Section 11: Graph Schema & Traversal Extensions

We extend the database schema with four new nodes and seven new relationships.

## 11.1 Schema Extensions

### New Nodes
1. `ConceptNode`: Unique identification of a concept.
2. `ConceptVersion`: Point-in-time configuration of a concept.
3. `ConceptCluster`: Domain groups.
4. `ConceptEvidence`: Granular mapping logs.
5. `ConceptMetrics`: Topological score metrics.

### New Relationships
1. `IMPLEMENTS_CONCEPT`: Links a code entity to a concept.
2. `BELONGS_TO_CONCEPT`: Links a `LogicVersion` to a `ConceptVersion`.
3. `CONCEPT_DEPENDS_ON`: Dependency link between two concepts.
4. `CONCEPT_EVOLVED_TO`: Chronological progression between concept versions.
5. `SUPPORTED_BY`: Links `ConceptVersion` to `ConceptEvidence`.
6. `HAS_EVIDENCE`: Links `ConceptEvidence` to a `LogicVersion`.
7. `HAS_EXPLANATION`: Connects `ConceptVersion` to `ConceptExplanation`.
8. `HAS_METRICS`: Connects `ConceptVersion` to `ConceptMetrics`.

## 11.2 Cypher Traversal Query Examples

### Query: Find all concepts affected by a change in a dependency
```cypher
MATCH (c:ConceptNode)-[:CONCEPT_DEPENDS_ON]->(dep:ConceptNode {name: 'Persistence'})
RETURN c.name, dep.name
```

### Query: Find most central concepts using PageRank score
```cypher
MATCH (cv:ConceptVersion)-[:HAS_METRICS]->(m:ConceptMetrics)
WHERE cv.is_active = true
RETURN cv.concept_id, m.pagerank_score, m.entity_count
ORDER BY m.pagerank_score DESC
```

---

# Section 12: Database Design

To handle codebases containing millions of historical concept versions, the database is fully normalized and indexed.

## 12.1 DDL Schema (PostgreSQL Dialect)

```sql
-- Create Enum Types
CREATE TYPE concept_relationship_type AS ENUM (
    'DEPENDS_ON', 'IMPLEMENTS', 'SUPPORTS', 'USES', 'REQUIRES', 'ENHANCES', 'REPLACES'
);

CREATE TYPE concept_transition_type AS ENUM (
    'CONCEPT_CREATION', 'CONCEPT_MODIFICATION', 'CONCEPT_SPLIT', 'CONCEPT_MERGE', 'CONCEPT_REMOVAL'
);

-- Table: concept_nodes
CREATE TABLE concept_nodes (
    id UUID PRIMARY KEY,
    repository_id UUID NOT NULL,
    ontology_node_id VARCHAR(128) NOT NULL,
    name VARCHAR(256) NOT NULL,
    description TEXT,
    is_system_defined BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_concept_repository FOREIGN KEY (repository_id) 
        REFERENCES repositories(id) ON DELETE CASCADE,
    CONSTRAINT uq_repo_ontology UNIQUE (repository_id, ontology_node_id)
);

-- Table: concept_versions
CREATE TABLE concept_versions (
    id UUID PRIMARY KEY,
    concept_id UUID NOT NULL,
    commit_hash VARCHAR(40) NOT NULL,
    version_number INTEGER NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_concept_version_node FOREIGN KEY (concept_id) 
        REFERENCES concept_nodes(id) ON DELETE CASCADE,
    CONSTRAINT uq_concept_commit UNIQUE (concept_id, commit_hash)
);

-- Table: concept_evidence
CREATE TABLE concept_evidence (
    id UUID PRIMARY KEY,
    concept_version_id UUID NOT NULL,
    evidence_type VARCHAR(64) NOT NULL,
    target_id UUID NOT NULL, -- points to logic_versions or logic_evidence
    confidence_contribution NUMERIC(4,3) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_evidence_version FOREIGN KEY (concept_version_id) 
        REFERENCES concept_versions(id) ON DELETE CASCADE
);

-- Table: concept_relationships
CREATE TABLE concept_relationships (
    id UUID PRIMARY KEY,
    repository_id UUID NOT NULL,
    commit_hash VARCHAR(40) NOT NULL,
    from_concept_id UUID NOT NULL,
    to_concept_id UUID NOT NULL,
    relationship_type concept_relationship_type NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_rel_repo FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_from FOREIGN KEY (from_concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_to FOREIGN KEY (to_concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE
);

-- Table: concept_clusters
CREATE TABLE concept_clusters (
    id UUID PRIMARY KEY,
    cluster_key VARCHAR(128) UNIQUE NOT NULL,
    cluster_label VARCHAR(256) NOT NULL,
    cohesion_score NUMERIC(4,3) NOT NULL,
    member_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Table: concept_cluster_members
CREATE TABLE concept_cluster_members (
    id UUID PRIMARY KEY,
    cluster_id UUID NOT NULL,
    concept_id UUID NOT NULL,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_member_cluster FOREIGN KEY (cluster_id) REFERENCES concept_clusters(id) ON DELETE CASCADE,
    CONSTRAINT fk_member_concept FOREIGN KEY (concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE,
    CONSTRAINT uq_cluster_concept UNIQUE (cluster_id, concept_id)
);

-- Table: concept_explanations
CREATE TABLE concept_explanations (
    id UUID PRIMARY KEY,
    concept_version_id UUID NOT NULL UNIQUE,
    summary TEXT NOT NULL,
    detail JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_explanation_version FOREIGN KEY (concept_version_id) REFERENCES concept_versions(id) ON DELETE CASCADE
);

-- Table: concept_metrics
CREATE TABLE concept_metrics (
    id UUID PRIMARY KEY,
    concept_version_id UUID NOT NULL UNIQUE,
    entity_count INTEGER NOT NULL,
    file_count INTEGER NOT NULL,
    in_degree INTEGER NOT NULL,
    out_degree INTEGER NOT NULL,
    degree_centrality NUMERIC(6,4) NOT NULL,
    betweenness_centrality NUMERIC(6,4) NOT NULL,
    pagerank_score NUMERIC(8,6) NOT NULL,
    impact_score NUMERIC(8,3) NOT NULL,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_metrics_version FOREIGN KEY (concept_version_id) REFERENCES concept_versions(id) ON DELETE CASCADE
);

-- Table: concept_drift
CREATE TABLE concept_drift (
    id UUID PRIMARY KEY,
    concept_id UUID NOT NULL,
    baseline_commit VARCHAR(40) NOT NULL,
    current_commit VARCHAR(40) NOT NULL,
    drift_score NUMERIC(6,4) NOT NULL,
    drift_category VARCHAR(64) NOT NULL,
    dimension_scores JSONB NOT NULL, -- structural, pattern, dependency drift
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_drift_concept FOREIGN KEY (concept_id) REFERENCES concept_nodes(id) ON DELETE CASCADE
);

-- Table: concept_evolution
CREATE TABLE concept_evolution (
    id UUID PRIMARY KEY,
    from_concept_version_id UUID,
    to_concept_version_id UUID NOT NULL,
    transition_type concept_transition_type NOT NULL,
    similarity_score NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT fk_evo_from FOREIGN KEY (from_concept_version_id) REFERENCES concept_versions(id) ON DELETE SET NULL,
    CONSTRAINT fk_evo_to FOREIGN KEY (to_concept_version_id) REFERENCES concept_versions(id) ON DELETE CASCADE
);
```

## 12.2 Optimization Index Strategy

To support lightning-fast temporal traversals across huge codebases:

```sql
-- Indexing concept_nodes for quick repository-level queries
CREATE INDEX ix_concept_nodes_repository ON concept_nodes(repository_id);

-- Compound index for fast point-in-time lookup of a specific concept version
CREATE INDEX ix_concept_versions_node_commit ON concept_versions(concept_id, commit_hash);
CREATE INDEX ix_concept_versions_commit ON concept_versions(commit_hash);

-- Indexing concept_evidence for joins
CREATE INDEX ix_concept_evidence_version ON concept_evidence(concept_version_id);
CREATE INDEX ix_concept_evidence_target ON concept_evidence(target_id);

-- Indexing relationships
CREATE INDEX ix_concept_relationships_commit ON concept_relationships(repository_id, commit_hash);

-- Indexing evolution transitions
CREATE INDEX ix_concept_evolution_to ON concept_evolution(to_concept_version_id);
```

## 12.3 Migration Strategy

Alembic will register a single revision creating all Phase 4 tables. The migration will be non-blocking:
1. **Schema Update**: Execute `alembic upgrade` to create concept tables.
2. **Backfill Task**: A deferred celery task iterates through all ingested repositories, reconstructing concept versions historically from existing `LogicVersion` data.
3. **Write Lock Avoidance**: Queries use read-committed isolation; database indexes are built concurrently.

---

# Section 13: Application Services

Application services run within the Modular Monolith structure.

## 13.1 Use Case Declarations

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Application Services                            │
│                                                                        │
│                      ┌──────────────────────────┐                      │
│                      │  DetectConceptsUseCase   │                      │
│                      └──────────────────────────┘                      │
│                      ┌──────────────────────────┐                      │
│                      │   GetConceptsUseCase     │                      │
│                      └──────────────────────────┘                      │
│                      ┌──────────────────────────┐                      │
│                      │GetConceptEvolutionUseCase│                      │
│                      └──────────────────────────┘                      │
│                      ┌──────────────────────────┐                      │
│                      │GetConceptRelationsUseCase│                      │
│                      └──────────────────────────┘                      │
│                      ┌──────────────────────────┐                      │
│                      │  GetConceptDriftUseCase  │                      │
│                      └──────────────────────────┘                      │
│                      ┌──────────────────────────┐                      │
│                      │GetConceptExplainUseCase  │                      │
│                      └──────────────────────────┘                      │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. `DetectConceptsUseCase`
* **Command**: `DetectConceptsCommand(repository_id: UUID, commit_hash: str)`
* **Flow**: Parses active `LogicVersion` nodes at the given commit, evaluates the YAML ontology rules, creates `ConceptNode` and `ConceptVersion` records, establishes relationships, and computes evolution transitions.
* **Output**: `DetectionSummaryDTO`

### 2. `GetConceptsUseCase`
* **Query**: `GetConceptsQuery(repository_id: UUID, commit_hash: str, domain: Optional[str])`
* **Output**: `List[ConceptResponseDTO]`

### 3. `GetConceptEvolutionUseCase`
* **Query**: `GetConceptEvolutionQuery(concept_id: UUID)`
* **Output**: `List[ConceptEvolutionDTO]` (Chronological timeline of versions and their transition types)

### 4. `GetConceptRelationshipsUseCase`
* **Query**: `GetConceptRelationshipsQuery(repository_id: UUID, commit_hash: str)`
* **Output**: `ConceptDependencyMapDTO`

### 5. `GetConceptDriftUseCase`
* **Query**: `GetConceptDriftQuery(concept_id: UUID, baseline_commit: str, current_commit: str)`
* **Output**: `ConceptDriftDTO`

### 6. `GetConceptExplanationUseCase`
* **Query**: `GetConceptExplanationQuery(concept_version_id: UUID)`
* **Output**: `ConceptExplanationResponseDTO`

## 13.2 Domain Exceptions

```python
class ConceptDomainException(Exception):
    """Base exception for all Concept Graph domain issues."""
    pass

class ConceptNotFoundException(ConceptDomainException):
    """Raised when the requested Concept UUID is not registered in the database."""
    pass

class ConceptOntologyViolationException(ConceptDomainException):
    """Raised when concept detection rules violate ontology validation invariants."""
    pass
```

---

# Section 14: API Design

Exposes REST endpoints through FastAPI.

## 14.1 Routing Contracts

### 1. `GET /api/v1/repositories/{id}/concepts`
* **Query Params**:
  * `commit`: string (defaults to HEAD)
  * `domain`: string (optional, filter by security/data_management)
* **Response (200 OK)**:
```json
[
  {
    "id": "a7b3c291-5f2e-4d8a-b6c4-e1f0a9d2b5c8",
    "ontology_node_id": "security.authentication",
    "name": "Authentication",
    "confidence": 0.94,
    "is_active": true,
    "created_at": "2026-06-07T12:00:00Z"
  }
]
```

### 2. `GET /api/v1/concepts/{id}/timeline`
* **Response (200 OK)**:
```json
[
  {
    "concept_version_id": "f1a08555-de7b-49fa-98e6-d9b2cafac234",
    "commit_hash": "304cbdd0ec926f523580c7278c632ba787359397",
    "version_number": 2,
    "confidence": 0.94,
    "transition": {
      "type": "CONCEPT_MODIFICATION",
      "similarity_score": 0.85
    }
  }
]
```

### 3. `GET /api/v1/concepts/{id}/drift`
* **Query Params**:
  * `baseline_commit`: string (required)
  * `current_commit`: string (required)
* **Response (200 OK)**:
```json
{
  "concept_id": "a7b3c291-5f2e-4d8a-b6c4-e1f0a9d2b5c8",
  "drift_score": 0.3550,
  "drift_category": "SIGNIFICANT",
  "dimension_scores": {
    "structural": 0.4500,
    "pattern": 0.2000,
    "dependency": 0.3000
  }
}
```

### 4. `GET /api/v1/repositories/{id}/concept-map`
* **Query Params**:
  * `commit`: string (defaults to HEAD)
* **Response (200 OK)**:
```json
{
  "nodes": [
    { "id": "auth-id", "label": "Authentication", "type": "Concept" },
    { "id": "db-id", "label": "Persistence", "type": "Concept" }
  ],
  "edges": [
    { "from": "auth-id", "to": "db-id", "type": "DEPENDS_ON", "confidence": 0.85 }
  ]
}
```

---

# Section 15: Observability

System tracing and diagnostic metrics are integrated directly into the concept pipeline.

## 15.1 Metrics Registry (Prometheus Format)

* `concept_detection_latency_seconds`: Histogram measuring execution duration of `DetectConceptsUseCase` per repository.
* `concept_confidence_score`: Gauge tracking calculated confidence across detected concept versions.
* `concept_drift_value`: Gauge tracking the calculated drift score of changed concepts.
* `concept_clustering_duration_seconds`: Histogram measuring the dynamic Jaccard clustering calculation.

## 15.2 Tracing & Structured Logging Logs

```json
{
  "timestamp": "2026-06-07T12:05:00.123Z",
  "level": "INFO",
  "logger": "src.application.services.concept_detection",
  "message": "Concept detection completed successfully.",
  "context": {
    "repository_id": "c76b066c-b143-4c84-9210-20ff08488763",
    "commit_hash": "304cbdd0ec926f523580c7278c632ba787359397",
    "concepts_detected_count": 4,
    "duration_ms": 320.5,
    "details": [
      { "name": "Authentication", "confidence": 0.94 },
      { "name": "Persistence", "confidence": 0.88 }
    ]
  }
}
```

---

# Section 16: Benchmark Suite

To test concept detection correctness, we design a set of standard, reproducible test codebases with predetermined histories.

## 16.1 Scenario 1: Authentication Evolution (Split & Drift Test)
* **Commit 1**: Plaintext credential validation inside `login.py`.
  * *Expected Ground Truth*: Concept detected = `Authentication`. Confidence = $0.80$. Evidence matches = `auth_direct_compare`.
* **Commit 2**: Password checks are updated to utilize `bcrypt.checkpw`.
  * *Expected Ground Truth*: Concept `Authentication` updated to Version 2. Confidence increases to $0.95$. Evolution transition = `CONCEPT_MODIFICATION`.
* **Commit 3**: JWT token authorization helper is separated out into `token_auth.py`.
  * *Expected Ground Truth*: Splitting behavior is detected. The concept splits, creating a second concept = `Authorization`. Evolution transition = `CONCEPT_SPLIT`.

## 16.2 Scenario 2: Dynamic Persistence Merging
* **Commit 1**: Repository contains separate manual dictionary caches (`cache_memory_dict`) and custom file writers.
  * *Expected Ground Truth*: Two distinct concepts detected (`Caching` and `Persistence`).
* **Commit 2**: Code is consolidated into a unified Repository Pattern backed by a shared memory structure.
  * *Expected Ground Truth*: The Jaccard Coupling of implementing files exceeds $0.45$. The two concepts are dynamically clustered under `Data Access Layer`.

---

# Section 17: Validation Framework

The accuracy and reliability of the Concept Detection Engine is evaluated using standard verification metrics.

## 17.1 Mathematical Calibration

### 1. Precision ($P$)
$$\text{Precision} = \frac{TP}{TP + FP}$$
* **Threshold**: Must exceed $0.95$. Any false positive concept classification is flagged as an audit failure.

### 2. Recall ($R$)
$$\text{Recall} = \frac{TP}{TP + FN}$$
* **Threshold**: Must exceed $0.90$.

### 3. Calibration Error (ECE)
Ensures that confidence scores align with actual detection rates:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|I_b|}{N} \left| \text{acc}(I_b) - \text{conf}(I_b) \right|$$

* **Threshold**: Must be less than $0.15$ across ten confidence bins.

---

# Section 18: Scalability Review

Evaluating execution footprints over large organizations.

## 18.1 Performance Profiling

| Workload Metric | 100 Repositories | 1,000 Repositories | 10,000 Repositories |
| :--- | :--- | :--- | :--- |
| **Concept Versions** | $1 \times 10^5$ | $1 \times 10^6$ | $1 \times 10^7$ |
| **Storage (Index + Data)** | 1.2 GB | 12.0 GB | 120.0 GB |
| **Query Latency (HEAD)** | 12 ms | 15 ms | 28 ms |
| **Ingest Compute Time** | 0.8s / commit | 0.8s / commit | 0.8s / commit |

## 18.2 Risk Mitigations
* **Write Bottlenecks**: Avoid writing concept versions for commits that do not alter the code AST or dependencies. If a commit only edits `README.md` or configuration files, the post-ingestion concept task exits immediately.
* **Traversal Depth Capping**: Graph traversals are capped at a max depth of 3 hops, avoiding the "supernode" traversal slowdown.
* **Evidence De-duplication**: If the evidence matched is identical to the previous commit, `concept_evidence` registers a reference to the existing version rather than generating redundant rows.

---

# Section 19: Phase 4 Directory & System Architecture Map

The repository layout is extended cleanly to integrate the new concept layer.

```
git-GRAPH/
├── docs/
│   ├── ARCHITECTURE_V3.md
│   └── ARCHITECTURE_V4.md (This Reference File)
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── concept_node.py
│   │   │   ├── concept_version.py
│   │   │   ├── concept_relationship.py
│   │   │   ├── concept_evidence.py
│   │   │   ├── concept_cluster.py
│   │   │   ├── concept_explanation.py
│   │   │   └── concept_metrics.py
│   │   └── repositories/
│   │       ├── concept_node_repo.py
│   │       ├── concept_version_repo.py
│   │       └── concept_relationship_repo.py
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── detect_concepts.py
│   │   │   ├── get_concepts.py
│   │   │   ├── get_concept_evolution.py
│   │   │   └── get_concept_drift.py
│   │   └── services/
│   │       ├── concept_detection_engine.py
│   │       ├── concept_cluster_engine.py
│   │       └── concept_relationship_engine.py
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   └── models/
│   │   │       └── concept_models.py (SQLAlchemy DB Models)
│   │   └── ontology/
│   │       └── concepts.yaml (Taxonomy Configuration)
│   └── presentation/
│       └── api/
│           └── concepts.py (Endpoints Mapping)
```

---

# Section 20: Phase 5+ Readiness Review

We verify if the Phase 4 specification provides the necessary foundation for subsequent intelligence phases:

* **Phase 5 (Business Capability Graph)**: Enabled. Business capabilities require a structural baseline of technical concepts. A business mapping service can easily bind `ConceptNode` clusters (e.g. `Data Access Layer`) to organizational units (e.g. `Billing & Finance Systems`).
* **Phase 6 (Impact Prediction)**: Enabled. Changes in concepts (measured via `concept_drift`) allow the system to trace upstream/downstream impacts through the `concept_relationships` dependency tree.
* **Phase 7 (Graph-RAG)**: Enabled. Concepts provide high-level, human-comprehensible summaries of codebase regions. Instead of feeding raw AST text to an LLM, the system feeds the deterministic `ConceptExplanation` data, dramatically increasing retrieval accuracy.
* **Blocker Assessment**: No architectural blockers identified.

---

# Architectural Decision Records (ADR)

### ADR 4.1: Bounded Context Boundaries (Domain Boundary Graph)
* **Status**: Proposed (Deferred to Phase 5).
* **Context**: Real-world applications are divided into semantic boundaries (e.g., User Domain vs. Order Domain). Rather than forcing this complexity into the core concept extractor now, Phase 4 remains boundary-agnostic.
* **Decision**: We defer architectural boundary mapping. Phase 5 will introduce a dedicated `Domain Boundary Graph` mapping capabilities to structural boundaries.

### ADR 4.2: Concept Ownership
* **Status**: Proposed (Deferred to Phase 5).
* **Context**: Once business capability mapping occurs, concepts must resolve ownership properties (e.g. `Platform Team` owns `Authentication`).
* **Decision**: We introduce a placeholder interface `ConceptOwner` in Phase 5 to map organizational metadata to concept nodes without modifying Phase 4 core schema models.
