# Supported Logics, Languages, and Schemas

This document lists the active behavioral logics, programming languages, and metadata configuration schemas supported by the **Temporal Code Knowledge Graph Platform**.

---

## 1. Supported Programming Languages

The platform parses codebase source trees and extracts entities using Tree-sitter. The following programming languages are supported:

| Language | Tree-sitter Parser | File Extensions |
| :--- | :--- | :--- |
| **Python** | `tree-sitter-python` | `.py` |
| **JavaScript** | `tree-sitter-javascript` | `.js`, `.mjs` |
| **TypeScript** | `tree-sitter-typescript` | `.ts`, `.tsx` |
| **Go** | `tree-sitter-go` | `.go` |
| **Java** | `tree-sitter-java` | `.java` |

---

## 2. Supported Behavioral Logics (Ontology Patterns)

The behavioral intelligence engine supports **33 active detection patterns** classified under four primary domain areas:

### 🔒 Security (Authentication & Authorization)
* **`auth_direct_compare`** (Direct Credential Comparison): Detects raw equality comparisons (`==` / `!=`) of secret parameters without hashing.
* **`auth_sha256_verification`** (SHA256 Password Verification): Detects password verification using `hashlib.sha256` and hex digests with password parameters flowing into the sink.
* **`auth_bcrypt_verification`** (Bcrypt Password Verification): Detects password checks via `bcrypt.checkpw`.
* **`auth_bcrypt_hash`** (Bcrypt Password Hashing): Detects password salt-generation and hashing via `bcrypt.hashpw` / `bcrypt.gensalt`.
* **`auth_jwt_generation`** (JWT Token Generation): Detects token generation via `jwt.encode`.
* **`auth_jwt_verification`** (JWT Token Verification): Detects token validation via `jwt.decode`.
* **`auth_passlib_verify`** (Passlib Password Verification): Detects password verification using `passlib.context`.
* **`auth_argon2_verification`** (Argon2 Password Verification): Detects password checks via `argon2`.
* **`authz_permission_check`** (Permission Check): Detects calls verifying scopes or permissions (e.g., `has_permission`, `check_permission`, `is_authorized`).
* **`authz_rbac`** (Role-Based Access Control Check): Detects calls verifying user role memberships (e.g., `has_role`, `check_role`, `is_in_role`).

### 💾 Data Management (Caching, Database, Serialization)
* **`cache_memory_dict`** (In-Memory Dictionary Cache): Detects local process dictionary lookup structures.
* **`cache_lru_cache`** (LRU Cache): Detects local caching using Python's `functools.lru_cache` or `functools.cache` decorators.
* **`cache_redis_lookup`** (Redis Cache Lookup): Detects cache read operations via `redis.get` / `Redis.get`.
* **`cache_redis_set`** (Redis Cache Write): Detects cache writes via `redis.set` / `Redis.set`.
* **`cache_redis_cluster`** (Redis Cluster Cache): Detects caching operations on clustered nodes (`redis.cluster.RedisCluster`).
* **`cache_invalidation`** (Cache Invalidation): Detects cache deletion or clearing (e.g., `redis.delete`, `cache.clear`).
* **`db_raw_sql_execute`** (Raw SQL Execution): Detects direct SQL execution on connection cursors (e.g., `cursor.execute`, `connection.execute`).
* **`db_orm_sqlalchemy_query`** (SQLAlchemy ORM Query): Detects SQLAlchemy database queries (`session.query`, `query`, `filter`).
* **`db_repository_pattern`** (Repository Pattern): Detects repository classes wrapping database operations.
* **`db_transaction`** (Database Transaction): Detects explicit transactional boundaries (e.g., `commit`, `rollback`, `begin`).

### 🔄 Reliability (Retry & Circuit Breaker)
* **`circuit_breaker_pybreaker`** (Circuit Breaker via Pybreaker): Detects circuit breaker policies using `pybreaker`.
* **`circuit_breaker_manual`** (Manual Circuit Breaker): Detects custom state-based circuit checking.
* **`retry_tenacity`** (Retry with Tenacity): Detects automated method retries using `@retry` decorators from the `tenacity` library.
* **`retry_manual_loop`** (Manual Retry Loop): Detects custom try-except loops wrapping retry indices.
* **`retry_backoff`** (Exponential Backoff Retry): Detects backoff loop structures calling `time.sleep` with exponential calculations.

### 🌐 Integration (HTTP API Client & Messaging)
* **`api_requests_call`** (HTTP REST API Call via requests): Detects HTTP client methods (e.g. `requests.get`, `requests.post`).
* **`api_httpx_call`** (HTTP REST API Call via httpx): Detects async/sync HTTP client calls via `httpx`.
* **`api_endpoint_handler`** (API Endpoint Handler): Detects server endpoint routing decorators (e.g., `@app.get`, `@router.post`).
* **`api_gemini_client`** (Gemini GenAI Client Call): Detects generative AI calls using `google.genai.Client.models.generate_content`.
* **`tts_parler_generation`** (Parler TTS Audio Generation): Detects Parler Text-to-Speech audio generation calls using `parler_tts`.
* **`msg_publish_kafka`** (Kafka Message Publishing): Detects message publishing via `kafka` producers.
* **`msg_publish_rabbitmq`** (RabbitMQ Message Publishing): Detects message publishing via `pika` (e.g. `basic_publish`).
* **`msg_consume`** (Message Consumption): Detects subscriber consumer routines (e.g. `consume`, `subscribe`, `@consumer`).

---

## 3. Configuration & Schema Specifications

The platform uses YAML schemas to dynamically load ontology nodes and behavioral detection rules:

### A. Ontology Definition Schema (`ontology/*.yaml`)
Describes the hierarchical behavior classification tree:
```yaml
schema_version: "1.0"
ontology_version: "3.0.0"
domain: Security # Top-level domain: Security, Data_Management, Reliability, Integration
nodes:
  - id: security.authentication
    name: Authentication
    parent_id: null
    is_leaf: false
    description: "Mechanisms that verify identity."
    children:
      - id: security.authentication.hash_comparison
        name: Cryptographic Hash Verification
        parent_id: security.authentication
        is_leaf: true
        description: "Verification via cryptographic hash check."
```

### B. Behavior Pattern Schema (`patterns/*.yaml`)
Defines the pattern rules for matching code AST features:
```yaml
schema_version: "1.0"
patterns:
  - pattern_id: auth_bcrypt_verification
    name: Bcrypt Password Verification
    pattern_version: "1.0.0"
    ontology_node_id: security.authentication.hash_comparison
    base_confidence: 0.95
    index_keys:
      - "call:bcrypt.checkpw"
      - "import:bcrypt"
      - "call:checkpw"
    rules:
      ast_features:
        - match_type: call
          target_module: bcrypt
          target_function: checkpw
          description: "bcrypt.checkpw invocation"
      negative_indicators:
        - symbol: sha1
      data_flow:
        - source_param_pattern: "(password|passwd|pwd|secret)"
          sink_call: checkpw
```

---

## 4. Relational Database Schema (SQLAlchemy Models)

The relational schema representing Phase 3 Behavioral Intelligence entities is structured as follows:

```mermaid
erDiagram
    ontology_nodes ||--o{ behavior_patterns : "classifies"
    ontology_nodes ||--o{ logic_signatures : "categorizes"
    behavior_patterns ||--o{ logic_version_patterns : "matched_in"
    logic_signatures ||--o{ logic_versions : "has_versions"
    logic_versions ||--o{ logic_evidence : "supported_by"
    logic_versions ||--o{ logic_transitions : "transitions"
    logic_versions ||--o{ behavior_explanations : "has_explanation"
    logic_versions ||--o{ logic_version_patterns : "satisfies"
    logic_transitions ||--o{ behavior_drift : "measures_drift"
    logic_clusters ||--o{ logic_cluster_members : "groups"
    logic_signatures ||--o{ logic_cluster_members : "belongs_to"

    ontology_nodes {
        uuid id PK
        string node_id UK
        string name
        string domain
        string parent_node_id FK
        boolean is_leaf
        string description
        string ontology_version
        string schema_version
        datetime created_at
        datetime updated_at
    }

    behavior_patterns {
        uuid id PK
        string pattern_id UK
        string name
        string pattern_version
        string ontology_node_id FK
        float base_confidence
        json index_keys
        json rules
        string schema_version
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    logic_signatures {
        uuid id PK
        uuid repository_id FK
        string entity_seid
        string entity_name
        string entity_type
        string file_path
        string primary_ontology_node_id FK
        float overall_confidence
        json metadata
        datetime first_seen_at
        datetime last_seen_at
        datetime created_at
        datetime updated_at
    }

    logic_versions {
        uuid id PK
        uuid signature_id FK
        string commit_hash
        int version_number
        float confidence
        json index_keys
        string ast_fingerprint
        float complexity_score
        int line_start
        int line_end
        string raw_source_hash
        json metadata
        datetime observed_at
        datetime created_at
    }

    logic_evidence {
        uuid id PK
        uuid version_id FK
        string evidence_type
        string pattern_id FK
        string matched_text
        int line_number
        int column_offset
        float confidence
        float weight
        json metadata
        datetime created_at
    }

    logic_transitions {
        uuid id PK
        uuid from_version_id FK
        uuid to_version_id FK
        string transition_type
        string from_commit_hash
        string to_commit_hash
        float similarity_score
        float drift_magnitude
        boolean is_breaking_change
        string change_summary
        json metadata
        datetime detected_at
        datetime created_at
    }

    behavior_explanations {
        uuid id PK
        uuid version_id FK
        string explanation_type
        string summary
        string detail
        string security_implications
        string recommended_action
        float confidence
        string generated_by
        json metadata
        datetime created_at
    }

    behavior_drift {
        uuid id PK
        uuid transition_id FK
        uuid baseline_version_id FK
        uuid current_version_id FK
        float drift_score
        string drift_category
        boolean ontology_shift
        string from_ontology_node_id FK
        string to_ontology_node_id FK
        json pattern_additions
        json pattern_removals
        json pattern_modifications
        json metadata
        datetime computed_at
        datetime created_at
    }

    logic_clusters {
        uuid id PK
        string cluster_key UK
        string cluster_label
        string ontology_node_id FK
        string centroid_fingerprint
        int member_count
        float cohesion_score
        json metadata
        datetime created_at
        datetime updated_at
    }

    logic_cluster_members {
        uuid id PK
        uuid cluster_id FK
        uuid signature_id FK
        float distance_to_centroid
        boolean is_centroid
        datetime joined_at
        datetime created_at
    }

    logic_version_patterns {
        uuid id PK
        uuid version_id FK
        uuid behavior_pattern_id FK
        float confidence
        int evidence_count
        boolean is_primary
        json metadata
        datetime created_at
    }
}
