# Temporal Code Knowledge Graph Platform: API Reference Manual

This manual provides the detailed endpoint specifications, input payloads, query parameters, and response schemas for all functional modules of the **Temporal Code Knowledge Graph Platform** up to Phase 7C.

## General Information

### Base URL
All routes are prefixed with `/api/v1` unless noted otherwise.

### Standard Query Parameters
Across list endpoints, the following paging parameters are standard:
*   `page`: (int, default=1) 1-based page index.
*   `limit`: (int, default=50) maximum entries to return per page.

### Identifier Formats
*   `UUID`: Standard RFC 4122 string representing unique IDs (e.g., `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`).
*   `SEID` (Semantic Entity Identifier): Deterministic identifier syntax representing code structures, typically formatted as:
    ```
    {language}:{relative_path}:{fully_qualified_name}
    ```
    Example: `python:src/application/ports/unit_of_work.py:SQLAlchemyUnitOfWork.commit`

---

## 1. System Health & Ingestion

### `GET /health`
Returns the operational health metrics of the API, databases, and filesystem access.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-06-20T12:00:00Z",
      "version": "7.3.0",
      "connections": {
        "sqlite": "connected"
      }
    }
    ```

### `POST /repositories`
Register and queue a remote or local Git repository for cloning, branch tracking, AST parsing, and semantic analysis.
*   **Request Body**:
    ```json
    {
      "repository_url": "https://github.com/user/project.git",
      "branch": "main",
      "local_path": "c:/Users/HP/Desktop/git-GRAPH"
    }
    ```
*   **Response Status**: `201 Created`
*   **Response Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "status": "INGESTING",
      "created_at": "2026-06-20T12:00:05Z"
    }
    ```

### `GET /repositories`
List all tracked repositories registered in the platform.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "url": "https://github.com/user/project.git",
        "branch": "main",
        "local_path": "c:/Users/HP/Desktop/git-GRAPH",
        "status": "ANALYZED",
        "last_scanned_commit": "abcdef1234567890",
        "created_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

### `GET /repositories/{repository_id}`
Retrieve operational metadata, scan status, and repository profile.
*   **Path Parameters**:
    *   `repository_id` (str, required): The UUID of the repository.
*   **Response Status**: `200 OK` / `404 Not Found`
*   **Response Body**:
    ```json
    {
      "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "url": "https://github.com/user/project.git",
      "branch": "main",
      "status": "ANALYZED",
      "total_commits": 142,
      "total_entities": 4120,
      "total_relationships": 18230,
      "last_scanned_commit": "abcdef1234567890",
      "last_scanned_at": "2026-06-20T12:05:00Z"
    }
    ```

### `DELETE /repositories/{repository_id}`
Delete all associated SQLite records, temporal logs, and local workspace directory cache.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "deleted": true,
      "message": "Repository database records and workspace storage removed successfully."
    }
    ```

---

## 2. Entities & Relationships

### `GET /repositories/{repository_id}/entities`
Filter and query structural code entities extracted from the AST.
*   **Path Parameters**:
    *   `repository_id` (str): Repository UUID.
*   **Query Parameters**:
    *   `type`: (string) Filter by entity subtype (`Class`, `Method`, `Function`, `Struct`, `Interface`).
    *   `seid`: (string) exact SEID search.
    *   `name`: (string) partial match on entity name.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "seid": "python:src/application/ports/unit_of_work.py:IUnitOfWork",
        "name": "IUnitOfWork",
        "type": "Interface",
        "file_path": "src/application/ports/unit_of_work.py",
        "start_line": 10,
        "end_line": 45,
        "commit_hash": "abcdef1234567890"
      }
    ]
    ```

### `GET /repositories/{repository_id}/relationships`
Filter structural and import relationships between entities.
*   **Query Parameters**:
    *   `relationship_type`: (`CALLS`, `IMPORTS`, `IMPLEMENTS`, `EXTENDS`).
    *   `source_seid`: (string) Source entity filter.
    *   `target_seid`: (string) Target entity filter.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "source_seid": "python:src/infrastructure/persistence/unit_of_work.py:SQLAlchemyUnitOfWork",
        "target_seid": "python:src/application/ports/unit_of_work.py:IUnitOfWork",
        "relationship_type": "IMPLEMENTS",
        "commit_hash": "abcdef1234567890"
      }
    ]
    ```

---

## 3. Temporal Graph & Evolution

### `POST /repositories/{repository_id}/scan-history`
Asynchronously scans all commits in the repository history, compiling chronological delta maps.
*   **Response Status**: `202 Accepted`
*   **Response Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "task_id": "t1-2345",
      "status": "PROCESSING",
      "message": "Background scanning and delta computation started."
    }
    ```

### `GET /repositories/{repository_id}/timeline`
Retrieves chronological change timelines.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "timeline": [
        {
          "commit_hash": "abcdef1234567890",
          "author": "Anshuman",
          "timestamp": "2026-06-20T06:00:00Z",
          "additions": 42,
          "modifications": 12,
          "deletions": 3
        }
      ]
    }
    ```

### `GET /commits/{commit_hash}/changes`
Get specific structural change events introduced by the target commit.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "event_id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a",
        "seid": "python:src/application/decision_intelligence/decision.py:Decision",
        "mutation_type": "CREATED",
        "entity_type": "Class",
        "lines_added": 120,
        "lines_removed": 0
      }
    ]
    ```

### `GET /commits/{commit_hash}/graph`
Reconstructs the active entities and relationships as-of a specific commit.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "commit_hash": "abcdef1234567890",
      "nodes": [
        { "id": "python:src/main.py:app", "type": "Variable", "label": "app" }
      ],
      "edges": [
        { "from": "python:src/main.py:app", "to": "python:src/presentation/api/router.py:api_router", "type": "CALLS" }
      ]
    }
    ```

---

## 4. Behavioral Intelligence & Logic

### `POST /logic/extract`
Runs deep Tree-sitter behavioral rule validation across the snapshot.
*   **Request Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "commit_hash": "abcdef1234567890"
    }
    ```
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "commit_hash": "abcdef1234567890",
      "logic_signatures_detected": 14,
      "logic_versions_created": 14,
      "status": "SUCCESS"
    }
    ```

### `GET /logic/entity/{seid}`
Get behavioral logic matches for a specific code entity at a commit.
*   **Query Parameters**:
    *   `commit_hash` (str, required): Target commit revision.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b",
        "logic_signature_id": "f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f9a0b1c",
        "code_entity_seid": "python:src/domain/services/identity_service.py:bcrypt_verify",
        "commit_hash": "abcdef1234567890",
        "version_ordinal": 3,
        "overall_confidence": 0.95,
        "confidence_breakdown": {
          "overall_confidence": 0.95,
          "ast_confidence": 0.9,
          "dependency_confidence": 1.0,
          "data_flow_confidence": 0.9,
          "pattern_confidence": 0.8,
          "structural_confidence": 1.0,
          "evidence_count": 4
        },
        "is_primary": true,
        "created_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

### `GET /logic/version/{version_id}/evidence`
Gets concrete structural evidence for why a logic version was matched.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "logic_version_id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b",
        "evidence_type": "AST_CALL",
        "file_path": "src/domain/services/identity_service.py",
        "start_line": 23,
        "end_line": 23,
        "ast_node_type": "call",
        "matched_symbol": "bcrypt.checkpw",
        "matched_rule_id": "auth_bcrypt_verification",
        "call_chain": ["bcrypt_verify", "bcrypt.checkpw"],
        "confidence_contribution": 0.45,
        "detected_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

### `GET /logic/transition/{transition_id}/drift`
Compute multidimensional structural differences between two versions of code logic.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "id": "d1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "logic_transition_id": "t1e2f3a4-b5c6-7d8e-9f0a-1b2c3d4e5f6a",
      "from_logic_version_id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b",
      "to_logic_version_id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0c",
      "drift_score": 0.45,
      "drift_category": "SIGNIFICANT",
      "dimension_scores": {
        "structural_drift": 0.5,
        "dependency_drift": 0.2,
        "api_surface_drift": 0.0,
        "control_flow_drift": 0.6,
        "ontology_drift": 0.0,
        "security_drift": 0.8
      },
      "ontology_changed": false,
      "security_boundary_crossed": true,
      "computed_at": "2026-06-20T12:05:00Z"
    }
    ```

---

## 5. Concept & Ontology Layer

### `GET /repositories/{id}/concepts`
Retrieve high-level functional concepts mapped from code behavior.
*   **Query Parameters**:
    *   `commit_hash` (str, required): Commit revision filter.
    *   `domain`: (string) filter by ontology domain (e.g. `Security`, `DataManagement`).
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
        "ontology_node_id": "security.authentication.hash_comparison",
        "name": "Cryptographic Hash Verification",
        "confidence": 0.95,
        "is_active": true,
        "created_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

### `GET /repositories/{id}/concept-map`
Get nodes and edges representing the dependency graph of concepts.
*   **Query Parameters**:
    *   `commit_hash` (str, required): Snapshot commit hash.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "nodes": [
        { "id": "security.authentication", "label": "Authentication", "type": "Concept" }
      ],
      "edges": [
        { "from": "security.authentication", "to": "security.cryptography", "type": "DEPENDS_ON", "confidence": 0.85 }
      ]
    }
    ```

---

## 6. Capability Intelligence (CIL)

### `GET /repositories/{repository_id}/capabilities`
List all active, verified capabilities.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "e81d4fae-7dec-11d0-a765-00a0c91e6bf6",
        "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "name": "Identity Verification",
        "description": "User login and cryptographic hash comparison subsystem",
        "confidence": 0.94,
        "capability_type": "BUSINESS",
        "maturity_score": 0.85,
        "risk_score": 0.12,
        "coverage_score": 0.92,
        "concepts": ["security.authentication.hash_comparison"],
        "behaviors": ["auth_bcrypt_verification"],
        "flows": ["flow_123"],
        "entities": ["python:src/domain/services/identity_service.py:bcrypt_verify"],
        "relationships": [],
        "created_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

### `GET /capabilities/{capability_id}/health-risk`
Retrieve stability, cohesion, coupling, and boundary leakage diagnostics.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "capability_id": "e81d4fae-7dec-11d0-a765-00a0c91e6bf6",
      "health_score": 0.88,
      "risk_score": 0.15,
      "stability_score": 0.91,
      "cohesion_score": 0.78,
      "coupling_score": 0.22,
      "boundary_strength": 0.85,
      "boundary_leakage_detected": false
    }
    ```

### `GET /capabilities/{capability_id}/blast-radius`
Determine downstream impact metrics.
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "capability_id": "e81d4fae-7dec-11d0-a765-00a0c91e6bf6",
      "blast_radius_score": 0.35,
      "impacted_capability_ids": ["c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c"],
      "impact_depth": 2
    }
    ```

---

## 7. Deterministic Reasoning Layer

### `POST /reasoning/query`
Execute a deterministic query planner logic query.
*   **Request Body**:
    ```json
    {
      "repository_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "commit_hash": "abcdef1234567890",
      "query": "Which capabilities write to database tables without authorization checks?",
      "use_cache": true
    }
    ```
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "execution_id": "reasoning_987654",
      "question": "Which capabilities write to database tables without authorization checks?",
      "answer": "The capability 'caching' has 2 execution flows writing to databases where authorization is missing.",
      "confidence": {
        "score": 0.92,
        "level": "HIGH",
        "rationale": "Direct data-flow path matches database transaction APIs with zero RBAC path overlaps."
      },
      "reasoning_chain": {
        "execution_id": "reasoning_987654",
        "total_steps": 3,
        "steps": [
          {
            "step_index": 1,
            "step_type": "PATH_TRAVERSAL",
            "description": "Tracing write flows to repository models",
            "inputs": ["db_transaction"],
            "outputs": ["flow_4231", "flow_9012"],
            "executed_at": "2026-06-20T12:10:00Z",
            "duration_ms": 12.5
          }
        ]
      },
      "provenance_graph": {
        "conclusion_id": "conclusion_1",
        "conclusion": "Lack of RBAC on db_transaction flow_4231",
        "derived_from": ["flow_4231", "authz_rbac"],
        "nodes": [
          { "node_id": "flow_4231", "node_type": "Flow", "label": "SQL Execution Path" }
        ],
        "edges": [
          { "from": "flow_4231", "to": "conclusion_1", "relationship": "SUPPORTED_BY" }
        ]
      },
      "evidence": [
        {
          "source_id": "flow_4231",
          "source_type": "Flow",
          "description": "Database write execution without auth boundary check",
          "weight": 0.85,
          "validated": true
        }
      ],
      "limitations": [],
      "generated_at": "2026-06-20T12:10:02Z"
    }
    ```

---

## 8. Decision Intelligence Layer (DIL)

All DIL endpoints are mounted under `/api/v1`.

### Repository-Scoped Endpoints

#### `GET /api/v1/repositories/{repository_id}/decisions`
Returns all architectural, technology, and capability decisions discovered for the given repository.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "d81d4fae-7dec-11d0-a765-00a0c91e6bf6",
        "name": "Adopt Apache Kafka",
        "description": "Introduced dependency: kafka-python",
        "decision_type": "TECHNOLOGY_ADOPTION",
        "status": "ACTIVE",
        "confidence_score": 0.85,
        "first_seen_commit": "abcdef1234567890",
        "last_seen_commit": "abcdef1234567890",
        "repository_id": "repo-123",
        "created_at": "2026-06-20T12:00:00Z",
        "updated_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

#### `GET /api/v1/repositories/{repository_id}/decisions/summary`
Returns a high-level portfolio summary including totals, average confidence, and type/status breakdowns.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "total_decisions": 12,
      "total_intents": 4,
      "average_confidence": 0.82,
      "by_type": {
        "TECHNOLOGY_ADOPTION": 8,
        "TECHNOLOGY_REMOVAL": 2,
        "ARCHITECTURAL": 2
      },
      "by_status": {
        "ACTIVE": 10,
        "SUPERSEDED": 2
      }
    }
    ```

#### `GET /api/v1/repositories/{repository_id}/decisions/active`
Returns only decisions currently in `ACTIVE` status (the current decision baseline).
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`

#### `GET /api/v1/repositories/{repository_id}/decisions/search`
Performs a search over decisions by matching text keywords or filtering by type/status.
*   **Parameters**:
    *   `repository_id` (path, string)
    *   `q` (query, string, optional) — search keyword
    *   `type` (query, string, optional) — filter by type
    *   `status` (query, string, optional) — filter by status
*   **Response Status**: `200 OK`

#### `GET /api/v1/repositories/{repository_id}/decisions/timeline`
Returns the historical decision snapshots (co-temporal active sets) across the commit history.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "id": "a51d4fae-7dec-11d0-a765-00a0c91e6bf0",
        "repository_id": "repo-123",
        "commit_hash": "abcdef1234567890",
        "decisions_json": ["d81d4fae-7dec-11d0-a765-00a0c91e6bf6"],
        "generated_at": "2026-06-20T12:00:00Z"
      }
    ]
    ```

#### `GET /api/v1/repositories/{repository_id}/decisions/lifecycles`
Returns technology lifecycle arcs pairing adoption and removal events.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    [
      {
        "technology_key": "django",
        "display_name": "Django",
        "adoption_decision_id": "d81d4fae-7dec-11d0-a765-00a0c91e6bf6",
        "removal_decision_id": "f81d4fae-7dec-11d0-a765-00a0c91e6bf8",
        "adoption_commit": "c1",
        "removal_commit": "c3",
        "repository_id": "repo-123",
        "status": "RETIRED",
        "stability_index": 0.8,
        "lifespan_days": 45,
        "adoption_decision_name": "Adopt Django",
        "removal_decision_name": "Remove Django"
      }
    ]
    ```

#### `GET /api/v1/repositories/{repository_id}/decisions/graph`
Returns a directed dependency graph representation of all decisions.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`
*   **Response Body**:
    ```json
    {
      "nodes": [
        { "id": "d1", "label": "Adopt Django", "type": "TECHNOLOGY_ADOPTION" }
      ],
      "edges": [
        { "source": "d1", "target": "d2", "relationship_type": "DEPENDS_ON", "confidence": 1.0 }
      ]
    }
    ```

#### `GET /api/v1/repositories/{repository_id}/decisions/conflicts`
Lists all detected architectural or technology conflicts in the repository.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`

#### `GET /api/v1/repositories/{repository_id}/decisions/intents`
Lists all strategic intents (motivations) mapped to decisions in the repository.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`

#### `GET /api/v1/repositories/{repository_id}/decisions/causal-chains`
Lists multi-hop causal chains explaining "why" decisions were made.
*   **Parameters**: `repository_id` (path, string)
*   **Response Status**: `200 OK`

---

### Decision-Scoped Endpoints

#### `GET /api/v1/decisions/{decision_id}`
Returns complete details of a specific decision including evidence, history, and impacts.
*   **Parameters**: `decision_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`

#### `GET /api/v1/decisions/{decision_id}/versions`
Returns the historical version timeline of the decision.
*   **Parameters**: `decision_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`

#### `GET /api/v1/decisions/{decision_id}/fitness`
Evaluates and returns the multi-dimensional fitness metrics for the decision.
*   **Parameters**: `decision_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`

#### `GET /api/v1/decisions/{decision_id}/conflicts`
Returns any active conflicts involving this specific decision.
*   **Parameters**: `decision_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`

#### `GET /api/v1/decisions/{decision_id}/causal`
Returns causal relationships (causes and effects) involving this specific decision.
*   **Parameters**: `decision_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`

---

### Intent-Scoped Endpoints

#### `GET /api/v1/intents/{intent_id}`
Returns details of a strategic intent.
*   **Parameters**: `intent_id` (path, UUID)
*   **Response Status**: `200 OK` / `404 Not Found`


---

## 9. Error Response Formats

The API returns standard RFC 7807 problem details on error:

### `400 Bad Request`
```json
{
  "type": "https://git-graph.platform/errors/bad-request",
  "title": "Invalid Request Parameters",
  "status": 400,
  "detail": "The repository_url parameter must be a valid git URL format.",
  "instance": "/api/v1/repositories"
}
```

### `404 Not Found`
```json
{
  "type": "https://git-graph.platform/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "The requested repository UUID 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d' does not exist.",
  "instance": "/api/v1/repositories/a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
}
```
