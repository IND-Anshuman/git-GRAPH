# Temporal Code Knowledge Graph Platform API Documentation

This document provides a comprehensive overview of the REST API routes available in the platform, covering ingestion, entities, logic, capabilities, temporal evolution, reasoning, and decision intelligence.

All endpoints are prefixed with `/api/v1` unless otherwise specified.

---

## 1. System Health & Core Repositories
Endpoints related to core system status and repository management.

### `GET /health`
Returns the core health status of the API service and its connection to the underlying datastores.

### `POST /repositories`
Trigger the initial ingestion, cloning, and metadata extraction of a Git repository. Returns the tracked repository ID.

### `GET /repositories`
List all tracked repositories in the system.

### `GET /repositories/{repository_id}`
Get the current status and metadata of a specific tracked repository.

### `DELETE /repositories/{repository_id}`
Deletes an ingested repository from the database and removes its cloned workspace from disk.

---

## 2. Entities & Relationships
Endpoints for querying structural code elements.

### `GET /repositories/{repository_id}/entities`
Query entities (files, classes, functions, etc.) in a repository. Supports filtering by SEID (Semantic Entity Identifier) and semantic attributes.

### `GET /repositories/{repository_id}/relationships`
Query structural and semantic relationships between entities in a repository.

---

## 3. Temporal Graph & Evolution
Endpoints for traversing code history and architectural changes over time.

### `POST /repositories/{repository_id}/scan-history`
Triggers a background history scan and temporal diff generation across all historical commits.

### `GET /repositories/{repository_id}/timeline`
Retrieves the chronological timeline of commit events and high-level structural changes.

### `GET /repositories/{repository_id}/commits`
Retrieves a paginated list of all analyzed commits for the repository.

### `GET /commits/{commit_hash}`
Retrieves detailed metadata for a single analyzed commit.

### `GET /commits/{commit_hash}/changes`
Retrieves the exact structural addition, modification, and deletion events introduced by a specific commit.

### `GET /commits/{commit_hash}/graph`
Reconstructs the active entities and relationships graph state exactly as it existed at the given commit.

### `GET /entities/{entity_id}/history`
Retrieves the chronological version history of a specific entity by its SEID.

### `GET /repositories/{repository_id}/explorer/entity/{entity_id}/evolution`
Retrieves the chronological lifecycle sequence of a specific entity.

### `GET /repositories/{repository_id}/explorer/relationship/{relationship_id}/evolution`
Retrieves changes and version updates for a specific relationship constraint over time.

### `GET /repositories/{repository_id}/replay`
Streams commit-by-commit delta changes, emitting graph outputs suited for visualizers.

---

## 4. Logic & Semantic Evidence
Endpoints related to semantic evidence extraction and logic behavior patterns.

### `POST /logic/extract`
Trigger AST and Flow logic extraction for all entities in a repository commit snapshot.

### `GET /logic/entity/{seid}`
Retrieve logic versions detected on a specific CodeEntity at a commit.

### `GET /logic/entity/{seid}/history`
Retrieve the chronological evolution history of logic and behaviors for a CodeEntity.

### `GET /logic/signature/{signature_id}/evolution`
Retrieve the evolution graph of a logic signature (tracking behavioral drift across node versions).

### `GET /logic/version/{version_id}/evidence`
Retrieve concrete AST and Data Flow evidence supporting a given logic version detection.

### `GET /logic/version/{version_id}/explanation`
Retrieve human-readable explanations and rule verdicts for a specific logic version.

### `GET /logic/transition/{transition_id}/drift`
Retrieve quantitative drift scores and security crossing flags for a transition between two logic versions.

### `GET /logic/validate`
Run system-wide validation checks across all logic signatures, versions, and transitions.

---

## 5. Ontology, Concepts & Meta-Types
Endpoints for managing the knowledge framework (SEEE) and domain modeling.

### `POST /meta/embeddings/models`
Registers a new embedding model configuration to the platform.

### `POST /meta/embeddings/models/{model_id}/activate`
Sets an embedding model as active, enabling it for capability clustering and capability queries.

### `POST /meta/types`
Registers a new MetaType structure identifier (e.g., Domain Model, Value Object).

### `POST /meta/types/{type_id}/definitions`
Registers a new versioned schema definition configuration for a specific MetaType.

### `GET /meta/types`
Lists all registered MetaTypes, optionally filtered by architectural category.

### `POST /meta/discovery/run`
Triggers the dynamic clustering scan (EntityDiscoveryEngine) across a repository to detect candidate concepts.

### `POST /meta/discovery/concepts`
Triggers the ConceptDiscoveryEngine dynamic clustering scan, staging new domain semantic candidates.

### `GET /concepts/repositories/{id}/concepts`
Retrieve the list of functional concepts detected in a repository, optionally filtered by domain context.

### `GET /concepts/{id}/drift`
Retrieve multi-dimensional conceptual drift scores between two specific code commits.

### `GET /concepts/repositories/{id}/concept-map`
Retrieve the graph nodes and edges representing the high-level dependency map of domain concepts.

---

## 6. Capability Intelligence (CIL)
Endpoints for tracking bounded contexts and operational capabilities.

### `GET /repositories/{repository_id}/capabilities`
List all approved, active capabilities operating within a repository.

### `GET /repositories/{repository_id}/capabilities/candidates`
List all newly discovered, unapproved capability candidates.

### `POST /repositories/{repository_id}/capabilities/discover`
Trigger deep capability discovery heuristics for a repository.

### `POST /capabilities/{candidate_id}/approve`
Approve and promote a capability candidate to a formally recognized capability.

### `POST /capabilities/{candidate_id}/reject`
Reject an incorrectly discovered capability candidate.

### `GET /capabilities/{capability_id}/health-risk`
Retrieve stability, health, risk, drift, cohesion, and boundary breach details for a specific capability.

### `GET /capabilities/{capability_id}/blast-radius`
Calculate and retrieve the transitive dependency impact (blast radius) if a capability is modified or breaks.

### `POST /repositories/{repository_id}/capabilities/query`
Run a natural-language semantic query against the capability taxonomy to find related capabilities.

---

## 7. Diagnostics & Benchmarks
Endpoints for structural integrity and platform performance diagnostics.

### `GET /repositories/{repository_id}/diagnostics/health`
Calculates and returns system-wide structural health score metrics for the repository.

### `GET /repositories/{repository_id}/diagnostics/integrity`
Runs deep structural consistency checks and returns active or unresolved graph violations.

### `POST /repositories/{repository_id}/diagnostics/repair`
Executes transactional repair operations to fix structural or orphan node violations.

### `GET /repositories/{repository_id}/diagnostics/benchmarks`
Retrieves performance benchmark scan logs associated with a repository.

---

## 8. Deterministic Reasoning Layer
Endpoints for querying the reasoning engines.

### `POST /reasoning/query`
Execute a deterministic reasoning query (Phase 7A). Used to answer complex questions about code behavior, ownership, or architecture.

### `GET /reasoning/health`
Returns the status and index health of the semantic reasoning subsystem.

### `DELETE /reasoning/cache/{repository_id}`
Invalidates and drops all cached reasoning results for a specified repository.

---

## 9. Decision Intelligence Layer (DIL)
Endpoints for interacting with architectural intents and historical tech adoptions.

### `GET /decisions/{repository_id}`
List all tracked decisions, technology adoptions, and capability splits for the specified repository.

### `GET /decisions/decision/{decision_id}`
Retrieve exhaustive metadata (versions, confidence scores, evidence) for a specific decision.

### `GET /decisions/decision/{decision_id}/conflicts`
List detected conflicts or contradictory architectural decisions related to the given decision.

### `GET /decisions/decision/{decision_id}/fitness`
Retrieve the current lifecycle fitness score (stability, adoption, longevity) of an existing decision.
