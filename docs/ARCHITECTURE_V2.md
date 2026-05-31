# Temporal Code Knowledge Graph Platform
# Formal Architecture Specification

**Version**: 2.0  
**Classification**: Foundational Architecture Document  
**Review Panel**: Principal Software Architect, Staff Knowledge Graph Engineer, Compiler Systems Engineer, Database Architect, Staff RAG Engineer, Distributed Systems Architect, Senior Git Internals Engineer, Domain-Driven Design Expert

---

# Table of Contents

1. [System Thinking Analysis](#section-1-system-thinking-analysis)
2. [Domain Decomposition](#section-2-domain-decomposition)
3. [Complete Ontology Design](#section-3-complete-ontology-design)
4. [Entity Identity Model](#section-4-entity-identity-model)
5. [Relationship Ontology](#section-5-relationship-ontology)
6. [Temporal Model](#section-6-temporal-model)
7. [Graph Architecture](#section-7-graph-architecture)
8. [Metadata Architecture](#section-8-metadata-architecture)
9. [Semantic Enrichment Architecture](#section-9-semantic-enrichment-architecture)
10. [Database Architecture](#section-10-database-architecture)
11. [Query Requirements](#section-11-query-requirements)
12. [Future Compatibility](#section-12-future-compatibility)
13. [Architectural Review](#section-13-architectural-review)

---

# Section 1: System Thinking Analysis

## 1.1 Project Analysis

This platform sits at the intersection of four distinct engineering disciplines: **compiler engineering** (parsing source code into structured representations), **knowledge graph engineering** (modeling relationships between entities), **temporal data engineering** (tracking evolution of state over time), and **information retrieval engineering** (enabling semantic search and reasoning over the graph). The fundamental difficulty lies not in any single discipline but in the interaction effects between them.

The system's primary subject is not source code. Source code is an artifact. The system's primary subject is the **conceptual entity** — the function, the class, the module — which exists as an evolving idea that happens to be serialized into text files committed to a version control system. This distinction is critical because it means every design decision must prioritize entity identity and entity evolution over file-level or line-level tracking.

A conventional code indexer operates on a single snapshot: parse the current HEAD, index symbols, serve queries. This platform must operate across the **entire temporal axis** simultaneously, which introduces combinatorial complexity at every layer: entities multiplied by versions, relationships multiplied by temporal validity, graphs multiplied by commit points. The architecture must be designed to contain this combinatorial explosion without sacrificing query capability.

## 1.2 Core Challenges

### Challenge 1: Entity Identity Persistence

**Severity: Critical**

The hardest problem in this system is determining that a function `calculate_tax` in `billing/tax.py` at commit `abc123` is the **same conceptual entity** as `compute_tax` in `finance/taxation.py` at commit `def456`. The entity was renamed, moved to a different directory, and placed in a different module. A naive system would treat these as two unrelated entities — one deleted, one created — destroying the temporal chain.

Entity identity must survive:
- Renaming (symbol name changes, file name changes)
- Movement (file relocated to a different directory)
- Refactoring (signature changes, body changes, parameter reordering)
- Extraction (method extracted from a class into a standalone function)
- Inlining (standalone function absorbed into a class)
- Splitting (one function split into two)
- Merging (two functions merged into one)

No single heuristic handles all cases. Content hashing fails on any modification. Path-based identity fails on any movement. Name-based identity fails on any rename. The identity model must be a composite strategy with confidence scoring.

### Challenge 2: Graph Complexity Explosion

**Severity: High**

For a repository with `N` entities, the potential relationship space is `O(N²)`. A moderately sized Python project (50,000 lines) might contain 3,000–5,000 extractable entities. At the upper bound this yields ~25 million potential relationships, of which perhaps 15,000–50,000 are actual. Now multiply by the temporal dimension: if the project has 10,000 commits and each commit touches an average of 5 entities, the system must track 50,000 entity-version records and corresponding relationship-version records.

For large repositories (Linux kernel: 30M+ lines, 1M+ commits), naive approaches will fail catastrophically. The graph must be designed for sparse storage, lazy evaluation, and incremental computation.

### Challenge 3: Git History Complexity

**Severity: High**

Git history is not linear. It is a directed acyclic graph of commits. Merge commits have multiple parents. Rebases rewrite history. Cherry-picks duplicate changes. Squash merges collapse entire branches into single commits.

Specific complications include:
- **Merge commits**: A merge commit may introduce no actual code changes but represents the convergence of two development branches. The system must decide whether to analyze both parents or treat the merge as a single event.
- **Rebases**: A rebased branch contains commits with different hashes but identical or near-identical patches. The system must not treat these as new events if the repository has been re-analyzed after a force push.
- **Shallow clones**: If the system operates on a shallow clone, historical commits are unavailable. The architecture must degrade gracefully.
- **Rename detection**: Git's rename detection is heuristic-based (similarity threshold). The system inherits this imprecision and must decide whether to trust Git's rename detection or implement its own.
- **Binary files and generated code**: Not all files in a repository are parseable source code. The system must classify files and skip non-relevant content.

### Challenge 4: Temporal Versioning Complexity

**Severity: High**

The temporal model introduces a fundamental tension: **storage efficiency vs. reconstruction speed**. 

Approach A: Store a complete snapshot of every entity at every commit. Reconstruction is O(1) but storage is O(entities × commits), which is prohibitive for large repositories.

Approach B: Store only deltas (diffs) between versions. Storage is efficient but reconstruction requires replaying all deltas from the initial state to the target commit, which is O(commits) per entity.

Approach C: Store snapshots at periodic checkpoints and deltas between checkpoints. This is the classic database WAL approach and likely the correct tradeoff, but it introduces checkpoint management complexity.

The temporal model must also handle the fact that "time" in a repository is not wall-clock time. It is commit ordering, which is a partial order (not total order) due to branches. Two commits on different branches may have overlapping wall-clock timestamps but no causal relationship.

### Challenge 5: Semantic Enrichment Complexity

**Severity: Medium**

LLM-generated metadata (summaries, business purpose descriptions, risk assessments) is:
- **Non-deterministic**: The same input may produce different outputs across invocations.
- **Expensive**: Each entity enrichment costs API tokens and latency.
- **Perishable**: A summary generated for version N of an entity may be inaccurate for version N+1 even if the code change was minor.
- **Context-dependent**: A function's "business purpose" depends not only on its own code but on its callers, callees, and the broader system architecture.

The architecture must distinguish between deterministic metadata (extracted from code structure) and probabilistic metadata (generated by AI models), store them differently, version them independently, and provide mechanisms for invalidation and regeneration.

### Challenge 6: Scalability Considerations

The system must handle repositories ranging from small projects (100 files, 500 commits) to enterprise monorepos (100,000+ files, 500,000+ commits). The difference is roughly three orders of magnitude across every dimension:

| Metric | Small Project | Enterprise Monorepo | Scale Factor |
|---|---|---|---|
| Files | 100 | 100,000 | 1,000× |
| Commits | 500 | 500,000 | 1,000× |
| Entities | 500 | 500,000 | 1,000× |
| Relationships | 2,000 | 5,000,000 | 2,500× |
| Entity Versions | 2,500 | 50,000,000 | 20,000× |

Any design that works for small projects but does not account for the enterprise case will fail. Any design that optimizes for the enterprise case but is overly complex for small projects will impede adoption. The architecture must scale gracefully across this range.

### Challenge 7: Storage Concerns

A back-of-the-envelope calculation for a medium-large repository (10,000 files, 50,000 commits, 30,000 entities):

- Entity records: 30,000 × ~2 KB = 60 MB
- Entity versions: 30,000 × 20 avg versions × ~1 KB = 600 MB  
- Relationships: 100,000 × ~500 bytes = 50 MB
- Relationship versions: 100,000 × 10 avg versions × ~300 bytes = 300 MB
- Embeddings: 30,000 × 1536 dimensions × 4 bytes = 184 MB
- Semantic metadata: 30,000 × ~5 KB = 150 MB
- Git metadata: 50,000 commits × ~2 KB = 100 MB

**Total estimated storage per repository: ~1.5 GB**

For multi-repository analysis across 100 repositories, this approaches 150 GB in PostgreSQL alone, before indexes. This is manageable but demands attention to indexing strategy, partitioning, and archival policies.

## 1.3 Architectural Tradeoffs

### Tradeoff 1: Granularity of Extraction

Extracting every variable declaration and every constant produces a more complete graph but dramatically increases storage, processing time, and noise. Extracting only top-level classes and functions produces a cleaner graph but misses important relationships (a method reading a module-level variable, a function depending on a constant).

**Recommendation**: Default to **function/method-level granularity** with configurable depth. Variables and constants should be extracted only when they participate in cross-scope relationships (module-level exports, class fields referenced externally). This can be refined per-language.

### Tradeoff 2: Eagerness of Analysis

Should the system analyze every commit in history during initial ingestion, or start from HEAD and lazily process historical commits on demand?

Full-history analysis provides complete temporal data but may take hours for large repositories. HEAD-first analysis provides immediate utility but incomplete temporal coverage.

**Recommendation**: **HEAD-first with background historical backfill**. Analyze the latest commit immediately to provide instant value. Queue historical commits for background processing, prioritizing recent history. Allow users to query incomplete temporal data with explicit "coverage" indicators.

### Tradeoff 3: Storage Model

Materialized snapshots vs. event-sourced deltas for entity versions.

**Recommendation**: **Event-sourced with materialized views**. Store the canonical data as a sequence of mutation events (CREATED, MODIFIED, RENAMED, MOVED, DELETED). Maintain materialized views for the current state and for frequently-queried historical points. This provides both storage efficiency and query performance.

### Tradeoff 4: Graph Storage Engine

PostgreSQL adjacency lists vs. a native graph database (Neo4j).

PostgreSQL provides transactional consistency, mature tooling, and colocation with relational and vector data. Neo4j provides superior multi-hop traversal performance and a more natural graph query language (Cypher).

**Recommendation**: **PostgreSQL initially, with the graph layer abstracted behind repository interfaces** that allow future migration to Neo4j. The adjacency list model in PostgreSQL is sufficient for graphs under ~10M edges with proper indexing. The abstraction layer must not leak PostgreSQL-specific query patterns into the application logic.

---

# Section 2: Domain Decomposition

## 2.1 Bounded Context Identification

The platform decomposes into **eight bounded contexts**, each representing a distinct area of domain expertise with clear ownership boundaries.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM BOUNDARY                                     │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │
│  │  Repository  │───▶│    Git      │───▶│   Parsing   │───▶│  Extraction  │  │
│  │  Management  │    │  Analysis   │    │   Engine    │    │   Engine     │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────┬───────┘  │
│                                                                   │          │
│                                                                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────┐  │
│  │   Agentic   │◀───│  Retrieval  │◀───│  Semantic   │◀───│    Graph     │  │
│  │   Engine    │    │   Engine    │    │  Enrichment │    │   Engine     │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Bounded Context Definitions

### Context 1: Repository Management

**Responsibility**: Lifecycle management of Git repository references. Handles cloning, updating, branch tracking, and storage path management. This context knows about repositories as configuration objects — URLs, credentials, sync schedules — but does **not** understand Git internals, file content, or code semantics.

**Ownership**: Owns the `Repository` and `RepositoryConfiguration` aggregates.

**Boundaries**: 
- Accepts: Repository registration requests (URL, credentials, sync policy).
- Produces: Events indicating a repository is ready for analysis (`RepositoryCloned`, `RepositoryUpdated`).
- Does NOT: Parse files, read commit history, or understand code structure.

**Dependencies**: None (root context).

**Interactions**: 
- Emits `RepositoryReady` events consumed by the Git Analysis context.
- Provides repository metadata to any context that requests it.

---

### Context 2: Git Analysis

**Responsibility**: Extraction and interpretation of Git history. Reads commit DAGs, computes diffs, detects file-level changes (additions, deletions, renames, modifications), and produces structured change sets. This context understands Git's internal data model — commits, trees, blobs, refs — but does **not** understand code structure within files.

**Ownership**: Owns the `Commit`, `Branch`, `Tag`, `FileChange`, and `DiffHunk` aggregates.

**Boundaries**:
- Accepts: Repository path references and sync triggers.
- Produces: Ordered sequences of commit records with associated file-level change sets.
- Does NOT: Parse file contents into ASTs or extract code entities.

**Dependencies**: Repository Management (for repository paths and metadata).

**Interactions**:
- Consumes `RepositoryReady` events.
- Emits `CommitsDiscovered` events with file change manifests consumed by the Parsing Engine.

---

### Context 3: Parsing Engine

**Responsibility**: Transformation of raw source code text into language-agnostic Abstract Syntax Tree (AST) representations. Manages Tree-sitter grammar compilation, language detection, and AST generation. This context understands syntax but does **not** understand semantics.

**Ownership**: Owns the `SyntaxTree`, `ASTNode`, and `LanguageGrammar` aggregates.

**Boundaries**:
- Accepts: File content (text) and language identifiers.
- Produces: Structured AST representations.
- Does NOT: Determine what constitutes a "function" vs. a "method" in business terms, resolve cross-file references, or build relationship graphs.

**Dependencies**: None for core parsing. Receives file content from Git Analysis context.

**Interactions**:
- Consumes file content provided alongside `CommitsDiscovered` events.
- Produces `FileParsed` events with AST payloads consumed by the Extraction Engine.

**Assumption**: Tree-sitter grammars are treated as external dependencies managed at the infrastructure level. The Parsing Engine does not own grammar development.

---

### Context 4: Extraction Engine

**Responsibility**: Identification and classification of code entities and their relationships from AST representations. This is the **semantic interpretation layer** that transforms syntactic structures into domain-meaningful entities. It understands language-specific conventions (e.g., a Python function defined inside a class body is a method; a top-level function is a standalone function).

**Ownership**: Owns the `ExtractedEntity`, `ExtractedRelationship`, and `ExtractionResult` aggregates. Also owns language-specific extraction strategy definitions.

**Boundaries**:
- Accepts: AST representations and file metadata.
- Produces: Collections of typed entities and relationships with structural metadata.
- Does NOT: Persist entities to the graph, compute temporal diffs, or generate semantic summaries.

**Dependencies**: Parsing Engine (for AST inputs).

**Interactions**:
- Consumes `FileParsed` events.
- Emits `EntitiesExtracted` events consumed by the Graph Engine.

---

### Context 5: Graph Engine

**Responsibility**: Construction and maintenance of the temporal knowledge graph. This is the **core domain** of the entire platform. It receives extracted entities and relationships, resolves entity identity across versions, computes temporal diffs (CREATED, MODIFIED, RENAMED, MOVED, DELETED), builds and updates the graph structure, and maintains version histories.

**Ownership**: Owns the `GraphNode`, `GraphEdge`, `EntityVersion`, `RelationshipVersion`, `TemporalMutation`, and `GraphSnapshot` aggregates.

**Boundaries**:
- Accepts: Extracted entities and relationships with commit context.
- Produces: A queryable temporal knowledge graph.
- Does NOT: Generate semantic metadata, compute embeddings, or execute user-facing queries.

**Dependencies**: Extraction Engine (for entity and relationship inputs), Repository Management (for repository context).

**Interactions**:
- Consumes `EntitiesExtracted` events.
- Emits `GraphUpdated` events consumed by Semantic Enrichment and Retrieval Engine.
- Exposes graph traversal interfaces consumed by Retrieval Engine and Agentic Engine.

---

### Context 6: Semantic Enrichment

**Responsibility**: Generation of AI-powered metadata for graph entities. Produces summaries, business purpose descriptions, architectural role classifications, risk assessments, domain labels, and vector embeddings. This context is the boundary between deterministic code analysis and probabilistic AI inference.

**Ownership**: Owns the `SemanticSummary`, `EntityEmbedding`, `DomainClassification`, and `EnrichmentJob` aggregates.

**Boundaries**:
- Accepts: Entity content, structural metadata, and graph context.
- Produces: Semantic metadata records and vector embeddings.
- Does NOT: Modify the graph structure, resolve entity identity, or execute user queries.

**Dependencies**: Graph Engine (for entity content and graph context).

**Interactions**:
- Consumes `GraphUpdated` events to identify entities requiring enrichment.
- Writes semantic metadata and embeddings to shared storage.
- Emits `EnrichmentCompleted` events.

---

### Context 7: Retrieval Engine

**Responsibility**: Query execution across the knowledge graph. Implements hybrid search combining graph traversal, vector similarity, keyword matching, and temporal filtering. Compiles retrieval results into structured context windows suitable for RAG pipelines and user-facing query results.

**Ownership**: Owns the `Query`, `RetrievalContext`, `SearchResult`, and `ContextWindow` aggregates.

**Boundaries**:
- Accepts: Structured or natural language queries.
- Produces: Ranked, contextualized result sets.
- Does NOT: Modify the graph, generate embeddings, or perform autonomous reasoning.

**Dependencies**: Graph Engine (for graph traversal), Semantic Enrichment (for embeddings and semantic metadata).

**Interactions**:
- Reads from graph storage and vector indexes.
- Provides context to the Agentic Engine.

---

### Context 8: Agentic Engine

**Responsibility**: Autonomous reasoning and multi-step query resolution. Orchestrates complex analytical workflows (impact analysis, root cause analysis, architecture review) by composing queries against the Retrieval Engine and interpreting results through LLM-powered reasoning chains.

**Ownership**: Owns the `AgentSession`, `ReasoningPlan`, `ToolInvocation`, and `AnalysisReport` aggregates.

**Boundaries**:
- Accepts: Complex analytical questions or workflow triggers.
- Produces: Structured analysis reports with evidence chains.
- Does NOT: Directly access the database, modify the graph, or parse source code.

**Dependencies**: Retrieval Engine (for all data access).

**Interactions**:
- Invokes Retrieval Engine queries as "tools."
- May trigger Semantic Enrichment for on-demand entity analysis.

## 2.3 Domain Interaction Map

```
Repository Management ──(RepositoryReady)──▶ Git Analysis
Git Analysis ──(CommitsDiscovered)──▶ Parsing Engine
Parsing Engine ──(FileParsed)──▶ Extraction Engine
Extraction Engine ──(EntitiesExtracted)──▶ Graph Engine
Graph Engine ──(GraphUpdated)──▶ Semantic Enrichment
Graph Engine ──(graph reads)──▶ Retrieval Engine
Semantic Enrichment ──(embeddings, metadata)──▶ Retrieval Engine
Retrieval Engine ──(context, results)──▶ Agentic Engine
```

**Key Principle**: Each context communicates with its neighbors via domain events or well-defined query interfaces. No context reaches across more than one boundary. The Agentic Engine cannot directly query the Graph Engine — it must go through the Retrieval Engine. This enforces a clean dependency chain and prevents the God Object anti-pattern.

---

# Section 3: Complete Ontology Design

## 3.1 Ontology Design Principles

Before enumerating entities, the following principles govern the ontology:

1. **An entity exists if and only if it has independent identity and lifecycle.** A function parameter is part of a function's signature; it does not have independent identity. A module-level constant that is imported by other modules does have independent identity.

2. **Entity types are language-agnostic abstractions.** A Python `class` and a Java `class` and a Go `struct` are all represented by the same `Class` entity type. Language-specific attributes are captured in metadata, not in entity type differentiation.

3. **Entities are organized in a containment hierarchy.** Every entity (except Repository) has exactly one parent in the containment tree. A Method belongs to a Class. A Class belongs to a Module. A Module belongs to a Package. A Package belongs to a Repository.

4. **The ontology must be extensible.** New entity types will emerge as the platform supports more languages and frameworks. The schema must accommodate this without migrations that alter core tables.

## 3.2 Entity Catalog

### Tier 1: Structural Containers

These entities represent organizational boundaries in source code.

---

#### Entity: Repository

**Purpose**: The root container. Represents a single Git repository as a unit of analysis. All other entities exist within the scope of a repository.

**Attributes**:
- `id`: UUID. System-assigned unique identifier.
- `name`: String. Human-readable repository name (e.g., `payment-service`).
- `origin_url`: String. The Git remote URL.
- `default_branch`: String. The primary branch (e.g., `main`).
- `created_at`: Timestamp. When the repository was registered in the system.
- `last_analyzed_commit`: String. The most recently processed commit hash.

**Metadata**:
- Primary language
- Total file count
- Total entity count (computed)
- Analysis coverage percentage

**Ownership Rules**: A repository is created by explicit user registration. It is never auto-discovered.

**Lifecycle**: Created → Active → Archived. Deletion cascades to all child entities.

---

#### Entity: Package

**Purpose**: Represents a logical grouping of modules. In Python, a directory containing `__init__.py`. In Java, a directory corresponding to a package declaration. In Go, a directory containing `.go` files with a shared `package` declaration.

**Attributes**:
- `id`: UUID.
- `canonical_name`: String. The fully qualified package name (e.g., `com.company.billing`).
- `repository_id`: FK → Repository.
- `parent_package_id`: FK → Package (nullable, for nested packages).
- `directory_path`: String. The filesystem path relative to repository root.

**Metadata**:
- Language
- Module count (computed)
- Entity count (computed)

**Ownership Rules**: A package belongs to exactly one repository. Packages may nest (parent-child).

**Lifecycle**: Exists as long as the corresponding directory with appropriate markers exists in the repository.

**Justification**: Packages are critical for architectural analysis. "What packages depend on the billing package?" is a foundational query. Without explicit package entities, this query requires reconstructing package boundaries from file paths at query time, which is fragile and slow.

---

#### Entity: Module

**Purpose**: Represents a single source file as a logical unit. In Python, a `.py` file. In Java, a `.java` file. In TypeScript, a `.ts` file. The module is the **primary unit of parsing** — each module produces one AST.

**Attributes**:
- `id`: UUID.
- `canonical_name`: String. Module name derived from file path and language conventions (e.g., `billing.invoice_processor`).
- `file_path`: String. Relative path from repository root.
- `package_id`: FK → Package.
- `language`: Enum. The programming language.
- `line_count`: Integer. Total lines in the file.

**Metadata**:
- File size in bytes
- Last modified commit hash
- Parse status (success/failure/skipped)

**Ownership Rules**: A module belongs to exactly one package.

**Lifecycle**: Created when a file is first seen. Modified when content changes. Deleted when file is removed. Moved/Renamed when file path changes.

**Justification**: Modules are the bridge between the filesystem world (files, paths) and the code world (classes, functions). Every entity below Module level is discovered by parsing the module's AST. The module entity preserves the mapping between file identity and code identity.

---

#### Entity: Namespace

**Purpose**: Represents an explicit namespace declaration within a module. Relevant for languages like C++, C#, PHP, and TypeScript that support namespace constructs independent of file structure.

**Attributes**:
- `id`: UUID.
- `qualified_name`: String. Fully qualified namespace (e.g., `MyApp::Controllers`).
- `module_id`: FK → Module.
- `parent_namespace_id`: FK → Namespace (nullable, for nested namespaces).

**Metadata**:
- Language
- Nesting depth

**Ownership Rules**: A namespace belongs to exactly one module.

**Lifecycle**: Tied to the source code declaration.

**Justification**: In languages with explicit namespaces, the namespace is a structural container that affects symbol resolution, dependency graphs, and architectural boundaries. Omitting it would lose information about code organization in C++, C#, and similar languages.

**Assumption**: For languages without explicit namespaces (Python, Go), this entity type is not generated. The module itself serves as the implicit namespace.

---

### Tier 2: Type Definitions

These entities represent programmer-defined types.

---

#### Entity: Class

**Purpose**: Represents a class, struct, record, or equivalent type definition. This is the primary container for methods and fields in object-oriented and hybrid languages.

**Attributes**:
- `id`: UUID.
- `name`: String. The class name (e.g., `InvoiceProcessor`).
- `qualified_name`: String. Fully qualified name including package/module path.
- `module_id`: FK → Module.
- `parent_class_id`: FK → Class (nullable, for nested/inner classes).
- `is_abstract`: Boolean.
- `visibility`: Enum (PUBLIC, PRIVATE, PROTECTED, INTERNAL).
- `decorators`: JSON array of decorator/annotation names.
- `start_line`: Integer.
- `end_line`: Integer.

**Metadata**:
- Base classes (names, for resolution)
- Implemented interfaces (names)
- Generic type parameters
- Language-specific modifiers (e.g., `final`, `sealed`, `dataclass`)

**Ownership Rules**: Belongs to one module. May contain methods, fields, and nested classes.

**Lifecycle**: Standard entity lifecycle (CREATED, MODIFIED, RENAMED, MOVED, DELETED).

**Justification**: Classes are the primary organizational unit in the majority of production codebases. They define data structures, behavior, and API surfaces. Class-level tracking is essential for dependency analysis, impact analysis, and architectural understanding.

---

#### Entity: Interface

**Purpose**: Represents an explicit interface, protocol, trait, or abstract base type definition. Separated from Class because interfaces have distinct semantics: they define contracts without implementation.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `visibility`: Enum.
- `start_line`: Integer.
- `end_line`: Integer.

**Metadata**:
- Extended interfaces
- Generic type parameters

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Interfaces represent architectural boundaries. "What implements the PaymentGateway interface?" and "How has the PaymentGateway contract changed over time?" are critical architectural queries. Conflating interfaces with classes would obscure the distinction between contract definition and implementation.

---

#### Entity: Enum

**Purpose**: Represents an enumeration type definition.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `members`: JSON array of `{name, value}` pairs.
- `start_line`: Integer.
- `end_line`: Integer.

**Metadata**:
- Visibility
- Whether members have associated values or methods

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Enums often represent domain concepts (order statuses, permission levels) and are referenced across many parts of a codebase. Tracking their evolution (members added, removed, reordered) is valuable for understanding domain model changes.

---

#### Entity: TypeAlias

**Purpose**: Represents a type alias, typedef, or type abbreviation.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `target_type`: String. The type expression being aliased.

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Type aliases reveal abstraction intentions. Tracking when `UserId = str` changes to `UserId = UUID` reveals meaningful type system evolution.

---

### Tier 3: Callable Entities

These entities represent executable units of code.

---

#### Entity: Function

**Purpose**: Represents a standalone function defined at module or namespace level. Not attached to a class.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `parameters`: JSON array of `{name, type_annotation, default_value}`.
- `return_type`: String (nullable).
- `is_async`: Boolean.
- `decorators`: JSON array.
- `visibility`: Enum.
- `start_line`: Integer.
- `end_line`: Integer.
- `complexity`: Integer (nullable). Cyclomatic complexity if computed.

**Metadata**:
- Docstring (raw text)
- Line count
- Local variable count

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Functions are the fundamental unit of behavior in procedural and functional codebases. They are the most common subject of queries like "what calls this function?" and "how has this function changed?"

---

#### Entity: Method

**Purpose**: Represents a function defined within a class, struct, or interface. Semantically distinct from a standalone function because it has a receiver/owner and participates in inheritance hierarchies.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String. Includes class name (e.g., `InvoiceProcessor.calculate_total`).
- `class_id`: FK → Class.
- `parameters`: JSON array (excludes `self`/`this`).
- `return_type`: String (nullable).
- `is_async`: Boolean.
- `is_static`: Boolean.
- `is_class_method`: Boolean.
- `is_property`: Boolean.
- `visibility`: Enum.
- `decorators`: JSON array.
- `start_line`: Integer.
- `end_line`: Integer.
- `complexity`: Integer (nullable).

**Metadata**:
- Docstring
- Whether it overrides a parent method
- Line count

**Ownership Rules**: Belongs to exactly one class.

**Lifecycle**: Standard entity lifecycle. Additionally, a method may be "inherited" — present in a subclass through inheritance without explicit definition. The system should track only explicitly defined methods, not inherited ones, to avoid phantom entities.

**Justification**: Methods carry different semantics than standalone functions: they participate in polymorphism, encapsulation, and inheritance. Separating them from functions enables queries like "which methods override `process_payment`?" that would be impossible if methods and functions were conflated.

---

### Tier 4: Data Entities

These entities represent data declarations.

---

#### Entity: Variable

**Purpose**: Represents a module-level or namespace-level variable declaration. Does NOT include function-local variables (which have no independent lifecycle).

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `type_annotation`: String (nullable).
- `is_exported`: Boolean.
- `start_line`: Integer.

**Metadata**:
- Initial value expression (truncated)

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Module-level variables that are imported by other modules represent shared state and coupling points. A global `DATABASE_URL` or `logger` instance has system-wide implications. Function-local variables are excluded because they do not participate in cross-module relationships and would dramatically inflate the entity count without proportional analytical value.

---

#### Entity: Constant

**Purpose**: Represents an immutable value declaration. Distinguished from Variable by intent: constants represent fixed configuration or domain values.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `value`: String (the literal value, if extractable).
- `type_annotation`: String (nullable).
- `start_line`: Integer.

**Metadata**:
- Naming convention match (ALL_CAPS, etc.)

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Constants often encode business rules (tax rates, permission flags, configuration defaults). Tracking their evolution reveals business logic changes that might not be apparent from function-level analysis.

---

#### Entity: Field

**Purpose**: Represents a class-level attribute, property, or member variable.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `class_id`: FK → Class.
- `type_annotation`: String (nullable).
- `visibility`: Enum.
- `is_static`: Boolean.
- `default_value`: String (nullable).
- `start_line`: Integer.

**Ownership Rules**: Belongs to exactly one class.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Fields define the data model of classes. Tracking field additions, removals, and type changes is essential for understanding data model evolution, particularly for database-backed models.

---

### Tier 5: Integration Entities

These entities represent external-facing contracts and integrations.

---

#### Entity: APIEndpoint

**Purpose**: Represents an HTTP/RPC endpoint exposed by the application. Extracted from framework-specific decorators or route definitions (e.g., `@app.get("/users/{id}")`, `@RequestMapping`).

**Attributes**:
- `id`: UUID.
- `http_method`: Enum (GET, POST, PUT, DELETE, PATCH).
- `route_pattern`: String (e.g., `/api/v1/users/{user_id}`).
- `handler_entity_id`: FK → Function or Method (the handler function).
- `module_id`: FK → Module.
- `framework`: String (e.g., `fastapi`, `flask`, `spring`).

**Metadata**:
- Request body schema (if extractable)
- Response schema (if extractable)
- Authentication requirements (if extractable from decorators)
- Rate limit annotations

**Ownership Rules**: Belongs to one module. Associated with one handler function/method.

**Lifecycle**: Standard entity lifecycle.

**Justification**: API endpoints represent the external contract of the application. Tracking endpoint evolution (route changes, method changes, schema changes) is critical for API compatibility analysis and consumer impact assessment.

---

#### Entity: DatabaseModel

**Purpose**: Represents an ORM model or database table definition. Extracted from framework-specific patterns (SQLAlchemy models, Django models, TypeORM entities).

**Attributes**:
- `id`: UUID.
- `name`: String. The model class name.
- `table_name`: String. The database table name (if extractable).
- `class_id`: FK → Class (the ORM model class).
- `module_id`: FK → Module.
- `framework`: String (e.g., `sqlalchemy`, `django`, `typeorm`).

**Metadata**:
- Column definitions: JSON array of `{name, type, nullable, primary_key, foreign_key_target}`
- Index definitions
- Constraint definitions

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Database models define the persistence layer contract. Changes to database models have cascading implications: migrations, API schema changes, downstream consumer updates. Tracking model evolution enables migration impact analysis.

---

#### Entity: Dependency

**Purpose**: Represents an external package dependency declared in project configuration files (requirements.txt, package.json, go.mod, pom.xml).

**Attributes**:
- `id`: UUID.
- `name`: String. The package name (e.g., `sqlalchemy`).
- `version_constraint`: String (e.g., `^2.0.0`, `>=1.4,<2.0`).
- `repository_id`: FK → Repository.
- `dependency_type`: Enum (RUNTIME, DEV, OPTIONAL, PEER).
- `source_file`: String. The manifest file path.

**Metadata**:
- Registry (PyPI, npm, Maven, etc.)
- Resolved version (if lockfile is available)

**Ownership Rules**: Belongs to one repository.

**Lifecycle**: Created when dependency is added to manifest. Modified when version changes. Deleted when removed.

**Justification**: External dependencies are a critical dimension of software architecture. "What changed when we upgraded SQLAlchemy from 1.4 to 2.0?" and "Which modules depend on this external library?" are essential queries.

---

#### Entity: Configuration

**Purpose**: Represents a configuration value or setting defined in configuration files (YAML, TOML, JSON, .env, settings modules).

**Attributes**:
- `id`: UUID.
- `key`: String. The configuration key (e.g., `DATABASE_URL`, `MAX_RETRY_COUNT`).
- `value`: String (nullable; may be a placeholder or environment variable reference).
- `source_file`: String. The file where the configuration is defined.
- `module_id`: FK → Module (nullable; may not live in a code module).
- `repository_id`: FK → Repository.

**Metadata**:
- Data type (string, integer, boolean, URL)
- Whether it references an environment variable
- Default value

**Ownership Rules**: Belongs to one repository.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Configuration values control runtime behavior. Tracking configuration changes reveals operational modifications that are invisible in code-level analysis.

---

#### Entity: Import

**Purpose**: Represents an import/include statement that establishes a dependency from one module to another module or to an external package.

**Attributes**:
- `id`: UUID.
- `source_module_id`: FK → Module. The module containing the import statement.
- `target_qualified_name`: String. The fully qualified name being imported.
- `alias`: String (nullable). Import alias if used.
- `is_wildcard`: Boolean. Whether this is a wildcard import (`from x import *`).
- `start_line`: Integer.

**Ownership Rules**: Belongs to the importing module.

**Lifecycle**: Tied to the import statement's presence in source code.

**Justification**: Imports are the primary mechanism for establishing module-level dependencies. While the relationship graph captures IMPORTS edges, the Import entity preserves details (aliases, wildcards, specific symbols imported) that are lost in a simple relationship edge.

---

### Tier 6: Testing Entities

---

#### Entity: TestCase

**Purpose**: Represents an individual test function or method.

**Attributes**:
- `id`: UUID.
- `name`: String.
- `qualified_name`: String.
- `module_id`: FK → Module.
- `class_id`: FK → Class (nullable; for test methods in test classes).
- `test_framework`: String (e.g., `pytest`, `unittest`, `jest`).
- `start_line`: Integer.
- `end_line`: Integer.

**Metadata**:
- Decorators/markers (e.g., `@pytest.mark.slow`)
- Fixture dependencies

**Ownership Rules**: Belongs to one module.

**Lifecycle**: Standard entity lifecycle.

**Justification**: Tests are first-class entities for quality analysis. "What tests cover the billing module?" and "Which tests were added or removed in the last sprint?" are valuable queries. Tests also establish TESTS relationships to production entities, enriching the dependency graph.

---

## 3.3 Entity Type Extensibility

The ontology is designed for extension. Future entity types that may be added include:

- **Decorator/Annotation**: For languages where decorators carry significant semantic weight (Python, Java).
- **Middleware**: For web framework middleware definitions.
- **EventHandler**: For event-driven systems.
- **GraphQLType / GraphQLResolver**: For GraphQL APIs.
- **ProtobufMessage**: For gRPC services.
- **MigrationScript**: For database migration files.

The database schema should support entity types as an extensible enumeration (stored as strings, not database-level enums) to allow new types without schema migrations.

---

# Section 4: Entity Identity Model

## 4.1 The Identity Problem

Entity identity is the single most critical design challenge in this system. The entire temporal model depends on correctly answering the question: "Is entity A at commit N the same conceptual entity as entity B at commit N+1?"

If identity tracking fails, the temporal graph fractures. A renamed function appears as a deletion and a creation rather than a rename. The function's history is severed. Queries about the function's evolution return incomplete results. Users lose trust in the system.

The problem is fundamentally one of **entity resolution** across time, which is a well-studied but unsolved general problem. In the code domain, we have structural cues that constrain the problem, but we cannot achieve perfect accuracy. The design must acknowledge this and provide confidence scoring rather than binary identity assertions.

## 4.2 Identity Dimensions

An entity's identity can be characterized along four dimensions:

### Dimension 1: Positional Identity
**Definition**: The entity's location in the file system and containment hierarchy.
**Signal**: `repository/package/module/class/method` path.
**Strength**: Very strong when nothing has moved. Completely useless when files are reorganized.
**Example**: `payment-service/src/billing/invoice.py::InvoiceProcessor::calculate_total`

### Dimension 2: Nominal Identity
**Definition**: The entity's name and qualified name.
**Signal**: The symbol name and its parent chain.
**Strength**: Strong for distinctive names. Weak for generic names (`process`, `handle`, `get`). Fails on rename.
**Example**: `InvoiceProcessor.calculate_total`

### Dimension 3: Structural Identity
**Definition**: The entity's AST shape — its syntactic structure independent of naming.
**Signal**: A hash of the AST subtree with identifiers normalized (replaced with positional tokens).
**Strength**: Survives renaming. Survives movement. Fails on refactoring that changes structure.
**Example**: A function with 3 parameters, 2 if-statements, 1 loop, and 1 return has a structural fingerprint distinct from a function with 2 parameters and no control flow.

### Dimension 4: Semantic Identity
**Definition**: The entity's meaning — what it does, not how it's written.
**Signal**: Vector embedding of the entity's code content.
**Strength**: Survives structural refactoring if behavior is preserved. Expensive to compute. Subject to embedding model drift.
**Example**: Two implementations of "calculate invoice total" using different algorithms will have similar embeddings.

## 4.3 Identity Strategy Options

### Option A: Path-Based Identity (Naive)

**Mechanism**: Entity identity = `repository_id + file_path + entity_type + name`.

**Advantages**: Simple, deterministic, no computation required.

**Failures**: Any file rename, file move, or entity rename creates a new identity. The temporal chain breaks on every refactoring commit.

**Assessment**: Unacceptable for a temporal tracking system. Mentioned only to establish the baseline.

---

### Option B: Content Hash Identity

**Mechanism**: Entity identity = hash of the entity's complete source code text.

**Advantages**: Deterministic. Two identical functions have the same identity regardless of location.

**Failures**: Any modification, no matter how trivial (adding a comment, reformatting), creates a new identity. This makes version tracking impossible since every version would be a "new" entity.

**Assessment**: Useful as a version fingerprint (detecting whether content changed) but unusable as a stable identity.

---

### Option C: Structural Fingerprint Identity

**Mechanism**: Entity identity = hash of the normalized AST subtree. Normalization replaces all identifier names with positional tokens (ARG_0, VAR_1, FUNC_CALL_0, etc.), strips comments and whitespace, and hashes the resulting structure.

**Advantages**: Survives renaming, comment changes, formatting changes. Fairly cheap to compute (requires AST, which is already being produced).

**Failures**: Any structural change (adding a parameter, changing control flow) alters the fingerprint. Cannot handle identity across refactoring that changes code structure.

**Assessment**: Strong signal but insufficient alone. Two structurally identical functions in different locations would be falsely unified. Must be combined with positional information.

---

### Option D: Composite Identity with Confidence Scoring (Recommended)

**Mechanism**: Each entity is assigned a **Stable Entity ID** (SEID) that persists across versions. When processing a new commit, the system attempts to match each newly extracted entity against the set of entities known from the previous commit using a multi-signal scoring model.

**Identity Resolution Process**:

```
For each entity E_new extracted from commit C_n:
  1. Compute positional key: (file_path, entity_type, name)
  2. Compute structural fingerprint: normalized AST hash
  3. Compute parent context: (containing class/module name, parameter count, position ordinal among siblings)

  4. Search for candidates in commit C_{n-1}:
     a. Exact positional match → confidence 1.0, assign same SEID
     b. Same name + same parent + different file → likely MOVED → confidence 0.9
     c. Different name + same file + same structural fingerprint → likely RENAMED → confidence 0.85
     d. Different name + different file + same structural fingerprint + same parent type → confidence 0.75
     e. Git rename detection says file was renamed → boost confidence by 0.1 for all entities in that file

  5. If best candidate confidence ≥ THRESHOLD (default 0.7):
     Assign same SEID. Record the mutation type (MODIFIED, RENAMED, MOVED).
  
  6. If no candidate meets threshold:
     Assign new SEID. Record CREATED mutation.
  
  7. For entities in C_{n-1} not matched by any entity in C_n:
     Record DELETED mutation.
```

**Advantages**: 
- Handles the common cases (modification, rename, move) with high accuracy.
- Provides explicit confidence scores that enable downstream systems to flag uncertain matches for human review.
- Leverages Git's own rename detection as an additional signal.
- Degrades gracefully: when identity is uncertain, it creates a new entity rather than making a wrong linkage.

**Failures / Limitations**:
- Cannot reliably handle **splits** (one function divided into two) or **merges** (two functions combined into one). These are recorded as deletion + creation events with a metadata annotation suggesting the relationship.
- The confidence threshold is a tunable parameter. Too low → false linkages. Too high → broken chains. The default of 0.7 is a starting point that should be validated empirically.
- Requires processing commits in order. Cannot independently process commit N without knowing the state at commit N-1.

**Assessment**: This is the recommended approach. It balances accuracy, computational cost, and explainability. The confidence scores provide transparency that no binary approach can offer.

## 4.4 Identity Schema

```
Entity:
  seid: UUID              # Stable Entity ID — persists across versions
  version_id: UUID         # Unique per (seid, commit) pair
  entity_type: String      # CLASS, FUNCTION, METHOD, etc.
  canonical_name: String   # Current qualified name
  structural_fingerprint: String  # Normalized AST hash
  identity_confidence: Float      # How confident the system is in the SEID assignment
```

## 4.5 Handling Ambiguity

When the identity resolution system encounters ambiguous matches (multiple candidates with similar confidence scores), it should:

1. **Record all candidates** in an `identity_candidates` metadata field.
2. **Select the highest-confidence candidate** as the primary match.
3. **Emit an `IdentityAmbiguous` event** that can be surfaced to users or consumed by a future review workflow.
4. **Allow manual override**: The system should expose an API for users to manually assert or correct entity identity linkages.

---

# Section 5: Relationship Ontology

## 5.1 Relationship Design Principles

1. **Every relationship is directed.** "A calls B" is not the same as "B calls A." Directionality encodes causality and dependency flow.
2. **Every relationship has a temporal scope.** A relationship exists "as of commit X." Relationships are created, modified, and deleted alongside the entities they connect.
3. **Relationships connect entities, not files.** "Module A imports Module B" is a relationship between two Module entities. The import statement is evidence for the relationship, not the relationship itself.
4. **Relationships are typed and constrained.** Not all entity type pairs can participate in all relationship types. A Variable cannot EXTENDS another Variable. These constraints must be enforced.

## 5.2 Relationship Catalog

### BELONGS_TO

**Meaning**: Containment relationship. Entity A is structurally contained within Entity B.

**Direction**: Child → Parent. `Method BELONGS_TO Class`.

**Cardinality**: Many-to-One. An entity belongs to exactly one parent (except Repository, which has no parent).

**Valid Source → Target Pairs**:
- Package → Repository
- Module → Package
- Namespace → Module
- Class → Module | Namespace | Class (nested)
- Interface → Module | Namespace
- Enum → Module | Namespace
- Function → Module | Namespace
- Method → Class | Interface
- Field → Class
- Constant → Module
- Variable → Module

**Validation Rules**: Every entity except Repository must have exactly one BELONGS_TO relationship. The target must be a valid container for the source type.

**Traversal Implications**: BELONGS_TO edges form a tree (the containment hierarchy). Traversing BELONGS_TO upward from any entity yields its full qualified path. Traversing BELONGS_TO downward from a Module yields all entities defined in that module.

---

### CALLS

**Meaning**: Runtime invocation. Entity A contains code that will invoke Entity B during execution.

**Direction**: Caller → Callee. `FunctionA CALLS FunctionB`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Function → Function | Method
- Method → Function | Method

**Validation Rules**: Self-calls (recursion) are valid. The callee must be a callable entity.

**Traversal Implications**: CALLS edges form the **call graph**. Forward traversal (following CALLS from A) answers "what does A depend on at runtime?" Reverse traversal (finding all entities that CALL A) answers "what breaks if A changes its signature?"

**Detection Strategy**: Identify function/method invocation nodes in the AST. Resolve the callee to a known entity using import resolution and scope analysis. Unresolved callees (external library calls, dynamic dispatch) are recorded as relationships to synthetic placeholder entities or annotated as "unresolved."

**Example**: `InvoiceProcessor.calculate_total CALLS tax_calculator.compute_tax`

---

### IMPORTS

**Meaning**: Static dependency declaration. Module A contains an import statement referencing Module B or symbols from Module B.

**Direction**: Importer → Imported. `ModuleA IMPORTS ModuleB`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Module → Module
- Module → Package (package-level import)

**Validation Rules**: Self-imports are invalid (should be flagged as anomalies). Circular imports are valid but should be annotated.

**Traversal Implications**: IMPORTS edges form the **module dependency graph**. This is the coarsest-grained dependency structure and is useful for architectural analysis. Forward traversal answers "what does this module depend on?" Reverse traversal answers "what modules would be affected by changes to this module?"

**Detection Strategy**: Parse import statements. Resolve target module using language-specific import resolution rules and the known module set.

---

### DEPENDS_ON

**Meaning**: Generalized dependency. Entity A requires Entity B to function correctly, where the dependency type is not captured by a more specific relationship (CALLS, IMPORTS, EXTENDS, IMPLEMENTS).

**Direction**: Dependent → Dependency. `ClassA DEPENDS_ON ConstantB`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**: Any entity type → Any entity type, where there is a semantic dependency that does not fit a more specific relationship.

**Validation Rules**: This is a fallback relationship type. Prefer more specific types when applicable.

**Traversal Implications**: DEPENDS_ON edges, combined with CALLS, IMPORTS, EXTENDS, and IMPLEMENTS, form the **complete dependency graph**. Impact analysis traverses this composite graph.

**Example**: `APIEndpoint("/users") DEPENDS_ON DatabaseModel(User)` — the endpoint handler reads from the User table, but this dependency may not be a direct CALLS relationship if it passes through ORM abstractions.

---

### EXTENDS

**Meaning**: Inheritance. Entity A is a subclass/subtype of Entity B.

**Direction**: Subclass → Superclass. `AdminUser EXTENDS User`.

**Cardinality**: Many-to-Many (multiple inheritance in Python, C++; single inheritance in Java, C#, Go).

**Valid Source → Target Pairs**:
- Class → Class
- Interface → Interface

**Validation Rules**: Circular inheritance is invalid. The depth of the inheritance chain should be tracked as metadata.

**Traversal Implications**: EXTENDS edges form the **inheritance tree/DAG**. Downward traversal answers "what specializes this class?" Upward traversal answers "what is the ancestry of this class?" Combined with IMPLEMENTS, this reveals the complete type hierarchy.

---

### IMPLEMENTS

**Meaning**: Contract fulfillment. Entity A provides a concrete implementation of Interface B.

**Direction**: Implementor → Interface. `StripeGateway IMPLEMENTS PaymentGateway`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Class → Interface

**Validation Rules**: The implementing class should define methods matching the interface's declared methods (enforcement depends on language).

**Traversal Implications**: IMPLEMENTS edges bridge the abstract and concrete layers of the architecture. "What classes implement this interface?" reveals the polymorphic variants. "What interfaces does this class implement?" reveals its contract surface.

---

### READS

**Meaning**: Data access. Entity A reads the value of Entity B without modifying it.

**Direction**: Reader → Data source. `Method.process READS Field.config_value`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Function | Method → Variable | Constant | Field | Configuration

**Validation Rules**: Reading a constant or a field requires the reader to have access (scope, visibility).

**Traversal Implications**: READS edges reveal data flow. "What functions read this configuration value?" answers "what is affected if this config changes?"

**Detection Strategy**: Identify variable reference nodes in the AST where the referenced variable is not on the left-hand side of an assignment.

---

### WRITES

**Meaning**: Data mutation. Entity A assigns or modifies the value of Entity B.

**Direction**: Writer → Data target. `Method.update_status WRITES Field.status`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Function | Method → Variable | Field

**Validation Rules**: Writing to a constant should be flagged as an anomaly.

**Traversal Implications**: WRITES edges reveal mutation points. "What modifies this field?" is essential for debugging state corruption and understanding data flow.

---

### USES

**Meaning**: General reference. Entity A references Entity B in a way that is not captured by CALLS, READS, WRITES, EXTENDS, or IMPLEMENTS. This covers type references in annotations, generic parameters, decorator arguments, and similar structural references.

**Direction**: User → Used. `Function.get_user USES TypeAlias.UserId` (as a return type annotation).

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**: Any callable or type entity → Any type entity.

**Traversal Implications**: USES edges complete the dependency picture for type-level dependencies that do not involve runtime invocation or data access.

---

### TESTS

**Meaning**: Verification. Entity A is a test that validates the behavior of Entity B.

**Direction**: Test → Subject. `TestCase.test_calculate_total TESTS Method.calculate_total`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- TestCase → Function | Method | Class

**Detection Strategy**: Analyze test function bodies for calls to production code. Use naming conventions (test function name contains production function name) as a secondary signal. Exact detection is difficult and may require heuristic analysis.

**Traversal Implications**: "What tests cover this function?" is a fundamental quality assurance query. "What production code is untested?" (entities with no inbound TESTS edges) reveals coverage gaps.

---

### DECORATES

**Meaning**: Annotation/decoration. A decorator, annotation, or attribute is applied to an entity, modifying its behavior or metadata.

**Direction**: Decorator → Decorated entity. `@cache DECORATES Function.get_user`.

**Cardinality**: Many-to-Many.

**Valid Source → Target Pairs**:
- Decorator → Function | Method | Class

**Traversal Implications**: "What functions are cached?" (find all entities decorated by `@cache`). "What decorators are applied to this endpoint?" (find all DECORATES relationships targeting a handler).

---

## 5.3 Relationship Metadata

Every relationship instance carries metadata:

```
RelationshipInstance:
  id: UUID
  relationship_type: Enum (CALLS, IMPORTS, etc.)
  source_entity_seid: UUID
  target_entity_seid: UUID
  commit_hash: String           # The commit at which this relationship was observed
  confidence: Float             # How confident the extraction is (1.0 for explicit, lower for inferred)
  evidence_location: String     # File path and line number of the evidence (e.g., the import statement)
  metadata: JSON                # Type-specific additional data
```

---

# Section 6: Temporal Model

## 6.1 Temporal Events

The temporal model tracks five mutation event types. Each describes a specific kind of change that an entity undergoes between consecutive analyzed commits.

### Event: CREATED

**Meaning**: An entity is observed for the first time. No prior version exists in the graph.

**Detection Strategy**: After entity extraction for commit `C_n`, any entity that cannot be matched to an entity in commit `C_{n-1}` (using the identity resolution algorithm from Section 4) is classified as CREATED.

**Storage Strategy**: A new `entity_version` record is created with `mutation_type = CREATED`. The entity's SEID is newly generated. The full entity snapshot (all attributes, source code text, structural fingerprint) is stored.

**Edge Cases**:
- The very first commit analyzed for a repository produces CREATED events for all entities. This is correct.
- If a file was added in a merge commit, the CREATED event is attributed to the merge commit, not to the original branch commit.

---

### Event: MODIFIED

**Meaning**: An entity exists in both `C_{n-1}` and `C_n` with the same SEID, but its content has changed (different content hash or structural fingerprint).

**Detection Strategy**: An entity is matched to a prior version (same SEID, confidence above threshold) but its content hash differs.

**Storage Strategy**: A new `entity_version` record is created with `mutation_type = MODIFIED`. The record contains the new full snapshot. A diff between the previous and current source text is computed and stored in metadata.

**Subtypes of Modification** (stored as metadata, not separate event types):
- **Signature change**: Parameters, return type, or visibility changed.
- **Body change**: Implementation changed but signature is stable.
- **Documentation change**: Only docstring/comments changed.
- **Formatting change**: Only whitespace/formatting changed (should be filtered if not semantically meaningful).

---

### Event: RENAMED

**Meaning**: An entity exists in both `C_{n-1}` and `C_n` with the same SEID, but its name has changed while remaining in the same file and parent container.

**Detection Strategy**: Entity matched by structural fingerprint or positional context, but the `name` attribute differs and the `file_path` is unchanged.

**Storage Strategy**: A new `entity_version` record with `mutation_type = RENAMED`. Both the old name and new name are stored. The entity's `canonical_name` is updated.

---

### Event: MOVED

**Meaning**: An entity exists in both `C_{n-1}` and `C_n` with the same SEID, but its file location has changed.

**Detection Strategy**: Entity matched by name and/or structural fingerprint, but the `file_path` or `module_id` differs. Git's rename detection at the file level is a strong corroborating signal.

**Storage Strategy**: A new `entity_version` record with `mutation_type = MOVED`. Both the old path and new path are stored.

**Combined Events**: MOVED + RENAMED can occur simultaneously (file moved and entity renamed in the same commit). This is stored as a single event with `mutation_type = MOVED_AND_RENAMED` or as two separate events linked to the same commit. The recommendation is a single event with a combined type to avoid implying a temporal ordering between the move and the rename within a single commit.

---

### Event: DELETED

**Meaning**: An entity that existed in `C_{n-1}` is not present in `C_n` and was not matched to any entity in `C_n`.

**Detection Strategy**: After all entities in `C_n` have been matched, any entity from `C_{n-1}` that was not matched is classified as DELETED.

**Storage Strategy**: A new `entity_version` record with `mutation_type = DELETED`. The record references the last known state of the entity. No source code is stored (the previous version already has it).

**Soft Delete**: Deleted entities are never physically removed from the database. They exist in the temporal graph as historical nodes. Queries for "current state" filter out deleted entities; queries for "state at commit X" include them if they were alive at that point.

---

### Future Events: MERGED and SPLIT

**MERGED**: Two or more entities in `C_{n-1}` correspond to a single entity in `C_n`. Detection requires matching multiple prior entities to one current entity, which the identity algorithm handles by allowing multiple candidates to be linked.

**SPLIT**: One entity in `C_{n-1}` corresponds to two or more entities in `C_n`. Detection is the reverse: one prior entity matches multiple current entities by structural similarity.

These events are architecturally reserved but not implemented in the initial version. The database schema accommodates them by allowing mutation events to reference multiple source or target SEIDs.

## 6.2 Temporal Reconstruction

The system must answer the question: **"What did the knowledge graph look like at commit X?"**

### Reconstruction Algorithm

```
To reconstruct state at commit C_target:

1. Determine the commit ordering from the repository root to C_target.
   (For linear history, this is simply the ancestor chain.
    For DAG history, this requires topological sort of the commit subgraph.)

2. Initialize an empty entity set.

3. For each commit C_i in order from the root to C_target:
   a. Apply all mutation events associated with C_i:
      - CREATED: Add entity to set.
      - MODIFIED: Update entity attributes in set.
      - RENAMED: Update entity name in set.
      - MOVED: Update entity path/module in set.
      - DELETED: Remove entity from set.

4. The resulting entity set represents the graph state at C_target.
```

### Performance Optimization: Snapshot Checkpoints

For large repositories, replaying events from the root commit is prohibitively slow. The system maintains **snapshot checkpoints** at configurable intervals (e.g., every 1,000 commits or at every tagged release).

A checkpoint is a materialized view of the complete entity set at a specific commit. Reconstruction from a checkpoint requires replaying only the events between the checkpoint and the target commit.

**Checkpoint Selection**: When reconstructing state at `C_target`, find the nearest checkpoint `C_checkpoint` such that `C_checkpoint` is an ancestor of `C_target`. Replay events from `C_checkpoint` to `C_target`.

### The HEAD Materialized View

The most common query is "what is the current state?" The system maintains a **continuously updated materialized view** of the graph at HEAD. This view is updated incrementally as new commits are processed, avoiding full reconstruction.

---

# Section 7: Graph Architecture

## 7.1 Multi-Layer Graph Model

The knowledge graph is not a single flat graph. It is composed of three conceptually distinct layers that share entities (nodes) but differ in their edge semantics and query patterns.

```
┌────────────────────────────────────────────────────────────────┐
│                     QUERY LAYER                                │
│         (Unified query interface across all layers)            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  STRUCTURAL      │  │  SEMANTIC    │  │  TEMPORAL       │  │
│  │  GRAPH LAYER     │  │  GRAPH LAYER │  │  GRAPH LAYER    │  │
│  │                  │  │              │  │                 │  │
│  │  • BELONGS_TO    │  │  • Embeddings│  │  • CREATED      │  │
│  │  • CALLS         │  │  • Summaries │  │  • MODIFIED     │  │
│  │  • IMPORTS       │  │  • Domain    │  │  • RENAMED      │  │
│  │  • EXTENDS       │  │    labels    │  │  • MOVED        │  │
│  │  • IMPLEMENTS    │  │  • Business  │  │  • DELETED      │  │
│  │  • READS/WRITES  │  │    purpose   │  │  • Version      │  │
│  │  • DEPENDS_ON    │  │  • Similarity│  │    chains       │  │
│  │  • TESTS         │  │    edges     │  │  • Commit refs  │  │
│  │  • DECORATES     │  │              │  │                 │  │
│  └──────────────────┘  └──────────────┘  └─────────────────┘  │
│           │                    │                  │             │
│           └────────────────────┼──────────────────┘             │
│                                │                               │
│                    ┌───────────▼────────────┐                  │
│                    │   SHARED NODE SET      │                  │
│                    │   (Entity instances    │                  │
│                    │    identified by SEID) │                  │
│                    └───────────────────────-┘                  │
└────────────────────────────────────────────────────────────────┘
```

## 7.2 Layer 1: Structural Graph

**Purpose**: Represents the static code structure as extracted from source code at a specific point in time. This is the "what does the code look like?" graph.

**Nodes**: All entity types from the ontology (Section 3).

**Edges**: All relationship types from the relationship ontology (Section 5) except temporal mutations.

**Properties**:
- Deterministic: Fully derived from source code parsing and extraction. No AI inference.
- Snapshot-based: Represents the state at a specific commit.
- Reconstructable: Can be rebuilt from scratch by re-parsing the source code at any commit.

**Use Cases**:
- "What classes are in the billing package?"
- "What does `InvoiceProcessor` depend on?"
- "Show me the call graph for `process_payment`."
- "What implements the `PaymentGateway` interface?"

**Query Patterns**: Primarily graph traversal (BFS/DFS from a starting node), subgraph extraction (all entities within N hops of a target), and path finding (is there a dependency path from A to B?).

## 7.3 Layer 2: Semantic Graph

**Purpose**: Represents the meaning and conceptual relationships of code entities. This is the "what does the code mean?" graph.

**Nodes**: Same shared node set, augmented with semantic metadata (summaries, domain labels, risk scores).

**Edges**:
- **SEMANTICALLY_SIMILAR**: Weighted edges between entities whose vector embeddings are within a similarity threshold. These are not code-level dependencies but conceptual relationships. Two functions that both deal with "user authentication" are semantically similar even if they never call each other.
- **SAME_DOMAIN**: Edges between entities classified into the same business domain (e.g., all entities labeled "billing" are connected).

**Properties**:
- Probabilistic: Derived from AI model inference. Non-deterministic and subject to model updates.
- Expensive: Requires LLM API calls and embedding computations.
- Cached: Recomputed only when the underlying entity content changes.

**Use Cases**:
- "Find all code related to authentication."
- "What entities are similar to this function?"
- "What is the business purpose of this class?"

**Query Patterns**: Vector similarity search (nearest neighbors in embedding space), filtered by structural constraints (same repository, same language), combined with metadata filtering (domain = "billing").

## 7.4 Layer 3: Temporal Graph

**Purpose**: Represents the evolution of entities and relationships over time. This is the "how has the code changed?" graph.

**Nodes**: Entity versions (each version is a node, linked to the base entity by SEID).

**Edges**:
- **NEXT_VERSION**: Links consecutive versions of the same entity. `EntityV1 NEXT_VERSION EntityV2`.
- **CAUSED_BY**: Links an entity version to the commit that caused it. `EntityV2 CAUSED_BY Commit_abc123`.
- **COCHANGED_WITH**: Links entities that were modified in the same commit. `EntityA_V3 COCHANGED_WITH EntityB_V5` if both were modified in the same commit. This edge is valuable for discovering hidden coupling.

**Properties**:
- Append-only: Temporal edges are never modified or deleted. New versions are appended.
- Causally ordered: The NEXT_VERSION chain follows commit ordering.

**Use Cases**:
- "How has `InvoiceProcessor` evolved over time?"
- "What changed in the billing module between v1.0 and v2.0?"
- "Which entities are always modified together?" (co-change analysis)
- "When was `calculate_tax` deleted, and in which commit?"

**Query Patterns**: Version chain traversal (follow NEXT_VERSION from a starting version), temporal range queries (all mutations between commit A and commit B), co-change analysis (aggregate COCHANGED_WITH edges to find coupling patterns).

## 7.5 Cross-Layer Interactions

The power of the system comes from queries that span multiple layers:

- **Structural + Temporal**: "What dependencies of `UserService` have changed in the last month?" (traverse CALLS/IMPORTS edges from `UserService` in the structural layer, then check each dependent entity's temporal chain for recent MODIFIED events).
- **Semantic + Structural**: "Find all authentication-related code and show me its dependency graph." (vector search in the semantic layer for "authentication," then expand each result in the structural layer).
- **Semantic + Temporal**: "How has authentication code evolved?" (semantic search → temporal chain traversal for each result).
- **All three layers**: "What changed in the billing domain that might affect the payment gateway, and how has the payment gateway's test coverage evolved?" (semantic filter → structural dependency traversal → temporal version analysis → TESTS relationship analysis).

---

# Section 8: Metadata Architecture

## 8.1 Metadata Categories

The system manages five distinct metadata categories, each with different provenance, reliability, and update cadences.

### Category 1: Source Metadata

**Provenance**: Extracted directly from source code by the Parsing and Extraction engines.
**Reliability**: Deterministic and authoritative. If the parser is correct, this metadata is correct.
**Update Cadence**: Updated whenever the entity's source code changes.

**Required Fields**:
- `source_text`: String. The raw source code of the entity.
- `language`: Enum. Programming language.
- `start_line`: Integer. Starting line number in the source file.
- `end_line`: Integer. Ending line number.
- `character_offset_start`: Integer. Byte offset from file start.
- `character_offset_end`: Integer. Byte offset.
- `line_count`: Integer. Number of lines.
- `content_hash`: String. SHA-256 of the source text.
- `structural_fingerprint`: String. Normalized AST hash.

**Optional Fields**:
- `docstring`: String. Extracted documentation string.
- `complexity`: Integer. Cyclomatic complexity.
- `parameter_count`: Integer. For callables.
- `decorators`: JSON array. Applied decorators/annotations.

**Future Fields**:
- `ast_serialized`: Binary/JSON. Serialized AST subtree for deep structural analysis.
- `type_annotations_coverage`: Float. Percentage of parameters with type annotations.

---

### Category 2: Git Metadata

**Provenance**: Extracted from Git commit data and diff analysis.
**Reliability**: Deterministic and authoritative (based on Git's own records).
**Update Cadence**: Appended per commit.

**Required Fields**:
- `commit_hash`: String. The commit SHA.
- `commit_message`: String. Full commit message.
- `author_name`: String.
- `author_email`: String.
- `authored_date`: Timestamp.
- `committer_name`: String.
- `committer_email`: String.
- `committed_date`: Timestamp.
- `parent_hashes`: Array of String. Parent commit SHAs.

**Optional Fields**:
- `branch_name`: String. The branch on which this commit was first observed.
- `tag_names`: Array of String. Tags pointing to this commit.
- `is_merge`: Boolean.
- `diff_stats`: JSON. `{files_changed, insertions, deletions}`.

**Future Fields**:
- `pull_request_id`: String. Associated PR/MR identifier (requires forge API integration).
- `issue_references`: Array of String. Extracted issue numbers from commit message.

---

### Category 3: Semantic Metadata

**Provenance**: Generated by LLM inference.
**Reliability**: Probabilistic. Subject to model variation, prompt engineering, and hallucination.
**Update Cadence**: Recomputed when entity content changes. May be periodically refreshed with improved models.

**Required Fields**:
- `summary`: String. One-paragraph plain-English summary of what the entity does.
- `enrichment_model`: String. The model identifier used for generation (e.g., `gpt-4o-2024-05-13`).
- `enrichment_timestamp`: Timestamp. When the summary was generated.
- `enrichment_version`: Integer. Incremented on each re-enrichment.

**Optional Fields**:
- `business_purpose`: String. Why this entity exists from a business perspective.
- `architectural_role`: Enum. (CONTROLLER, SERVICE, REPOSITORY, UTILITY, CONFIGURATION, TEST, MIDDLEWARE, MODEL, ADAPTER, GATEWAY).
- `domain_classification`: Array of String. Business domains this entity relates to (e.g., `["billing", "invoicing"]`).
- `risk_level`: Enum. (LOW, MEDIUM, HIGH, CRITICAL). Based on dependency fan-in, mutation frequency, and business criticality.
- `complexity_assessment`: String. Human-readable assessment of code complexity.

**Future Fields**:
- `security_concerns`: Array of String. Identified security-relevant patterns.
- `performance_concerns`: Array of String. Identified performance anti-patterns.
- `suggested_refactoring`: String. AI-suggested improvements.

---

### Category 4: Version Metadata

**Provenance**: Computed by the Graph Engine during temporal analysis.
**Reliability**: Deterministic, derived from identity resolution and diff computation.
**Update Cadence**: Appended per entity version.

**Required Fields**:
- `seid`: UUID. Stable Entity ID.
- `version_ordinal`: Integer. Sequential version number for this entity (1, 2, 3...).
- `mutation_type`: Enum. (CREATED, MODIFIED, RENAMED, MOVED, DELETED).
- `commit_hash`: String. The commit that caused this version.
- `identity_confidence`: Float. Confidence that this version is correctly linked to the SEID.

**Optional Fields**:
- `previous_name`: String. If RENAMED, the prior name.
- `previous_path`: String. If MOVED, the prior file path.
- `diff_summary`: String. Human-readable summary of changes.
- `lines_added`: Integer.
- `lines_removed`: Integer.

**Future Fields**:
- `breaking_change`: Boolean. Whether this modification breaks the entity's public contract.
- `semantic_diff`: String. AI-generated description of what changed semantically, not just syntactically.

---

### Category 5: Analysis Metadata

**Provenance**: Computed by various analysis passes over the graph.
**Reliability**: Deterministic (based on graph structure and algorithms).
**Update Cadence**: Recomputed on graph updates.

**Required Fields**: None initially. All analysis metadata is optional and computed on demand.

**Optional Fields**:
- `dependency_fan_in`: Integer. Number of entities that depend on this entity.
- `dependency_fan_out`: Integer. Number of entities this entity depends on.
- `change_frequency`: Float. Average modifications per month over the entity's lifetime.
- `co_change_partners`: Array of UUID. Entities most frequently modified alongside this entity.
- `test_coverage_score`: Float. Ratio of TESTS relationships to total callable surface.

**Future Fields**:
- `instability_index`: Float. Fan-out / (Fan-in + Fan-out). Measures how likely an entity is to change due to external changes.
- `abstractness_index`: Float. For packages: ratio of abstract types to total types.
- `architectural_zone`: Enum. (ZONE_OF_PAIN, ZONE_OF_USELESSNESS, MAIN_SEQUENCE). Based on instability and abstractness.

---

# Section 9: Semantic Enrichment Architecture

## 9.1 Boundary Between Deterministic and AI-Generated Data

This boundary is critical and must be enforced architecturally:

**Deterministic (extracted from code, always recomputable)**:
- Entity names, types, signatures, line numbers
- Relationships (CALLS, IMPORTS, etc.)
- Structural fingerprints
- Cyclomatic complexity
- Line counts
- Content hashes
- Import chains
- Inheritance hierarchies

**AI-Generated (produced by LLMs, probabilistic, may vary)**:
- Natural language summaries
- Business purpose descriptions
- Domain classifications
- Risk assessments
- Architectural role labels
- Complexity assessments in natural language
- Suggested refactorings

**The rule**: Deterministic data is stored in primary entity and relationship tables. AI-generated data is stored in a separate `semantic_metadata` table with explicit provenance tracking (model, timestamp, version). No query should treat AI-generated data as authoritative without the user being aware of its provenance.

## 9.2 What Should Be Generated

### Priority 1: Entity Summaries (Essential)

Every entity at the Function, Method, and Class level should receive a one-paragraph summary explaining what it does in plain English. This is the foundation for semantic search and RAG context compilation.

**Input**: Entity source code, docstring, parameter names and types, return type.  
**Output**: 2–4 sentence summary.  
**Regeneration Trigger**: Entity content changes (MODIFIED event).

### Priority 2: Business Purpose (High Value)

A description of why this entity exists from a business perspective. "Calculates applicable sales tax for a line item based on jurisdiction rules" is more useful for non-technical stakeholders than "Iterates through tax_rules list and applies matching rule to amount."

**Input**: Entity source code + summaries of related entities (callers, callees) for context.  
**Output**: 1–2 sentence business justification.  
**Regeneration Trigger**: Entity content changes or significant relationship changes.

### Priority 3: Architectural Role Classification (High Value)

Classifying entities into architectural roles enables structural queries like "show me all repositories in the codebase" or "find all controller classes."

**Input**: Entity source code, name, containing module path, decorators, base classes.  
**Output**: One of a fixed set of roles (CONTROLLER, SERVICE, REPOSITORY, MODEL, UTILITY, ADAPTER, GATEWAY, MIDDLEWARE, CONFIGURATION, TEST).  
**Regeneration Trigger**: Entity content changes.

**Assumption**: Many architectural roles can be inferred deterministically from naming conventions and framework patterns (e.g., a class decorated with `@app.route` is a CONTROLLER). LLM inference should be used only for ambiguous cases. The enrichment pipeline should attempt deterministic classification first and fall back to LLM only when heuristics are inconclusive.

### Priority 4: Domain Classification (Medium Value)

Tagging entities with business domain labels (billing, authentication, user management, inventory).

**Input**: Entity source code + module path + related entity summaries.  
**Output**: Array of domain labels from a configurable taxonomy.  
**Regeneration Trigger**: Entity content changes.

### Priority 5: Risk Level Assessment (Medium Value)

Estimating how risky it is to modify an entity based on its dependency fan-in, change frequency, test coverage, and business criticality.

**Input**: Graph-derived metrics (fan-in, fan-out, change frequency, test coverage) + entity summary.  
**Output**: Risk level (LOW, MEDIUM, HIGH, CRITICAL) + justification.  
**Regeneration Trigger**: Graph metric changes or periodic recomputation.

## 9.3 Vector Embeddings

Every entity at the Function, Method, Class, and Module level should have a vector embedding computed from its source code content.

**Embedding Model**: Provider-agnostic. The system should support OpenAI `text-embedding-3-small` (1536 dimensions), Anthropic, Cohere, and local models (via Ollama). The embedding model identifier and dimension count must be stored alongside every embedding vector.

**Embedding Content**: The input to the embedding model should be a structured text representation:

```
[ENTITY_TYPE] [QUALIFIED_NAME]
[SIGNATURE OR DECLARATION]
[DOCSTRING IF PRESENT]
[SUMMARY IF AVAILABLE]
[SOURCE_CODE FIRST 2000 CHARACTERS]
```

This structured input ensures the embedding captures both structural and semantic information.

**Storage**: pgvector column in PostgreSQL. Indexed with IVFFlat or HNSW for approximate nearest neighbor search.

**Regeneration Trigger**: Entity content changes or embedding model upgrade.

**Model Migration**: When the embedding model changes, all embeddings must be recomputed. The system should support running two embedding models concurrently during migration (old embeddings for continuity, new embeddings being computed in the background).

## 9.4 Enrichment Pipeline Design

The enrichment pipeline must be:

1. **Asynchronous**: Enrichment should not block the ingestion pipeline. Entities are available in the graph immediately after extraction; enrichment happens in the background.
2. **Idempotent**: Re-running enrichment for the same entity version produces the same result (modulo LLM non-determinism, which is tracked via provenance).
3. **Prioritized**: Entities with high fan-in (many dependents) should be enriched before low-impact utility functions.
4. **Throttled**: LLM API calls must be rate-limited to avoid cost explosions. Embedding computations should be batched.
5. **Incremental**: Only entities whose content has changed since the last enrichment run should be re-enriched.

---

# Section 10: Database Architecture

## 10.1 Technology Selection Rationale

PostgreSQL with pgvector is selected as the unified storage engine for the initial implementation:

- **Relational + Graph**: Adjacency list representation in PostgreSQL handles graph queries up to 3–5 hops efficiently with recursive CTEs. This covers the majority of practical code analysis queries.
- **Relational + Vector**: pgvector eliminates the need for a separate vector database, reducing operational complexity.
- **Transactional consistency**: Entity extraction, graph updates, and version tracking can occur within a single ACID transaction.
- **Mature ecosystem**: Alembic for migrations, SQLAlchemy for ORM, extensive monitoring tools.

**Trade-off acknowledged**: PostgreSQL will underperform a native graph database (Neo4j) for deep traversals (6+ hops) and complex pattern matching. The abstraction layer (repository interfaces) allows Neo4j integration when this becomes a bottleneck.

## 10.2 Table Definitions

### Table: `repositories`

**Purpose**: Stores registered repository metadata.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | System-generated identifier |
| `name` | VARCHAR(255) | NOT NULL | Human-readable name |
| `origin_url` | TEXT | NOT NULL, UNIQUE | Git remote URL |
| `default_branch` | VARCHAR(100) | NOT NULL, DEFAULT 'main' | Primary branch |
| `last_analyzed_commit` | CHAR(40) | NULLABLE | Most recent processed commit hash |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | (pending, cloning, active, error, archived) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Registration timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification timestamp |
| `metadata` | JSONB | DEFAULT '{}' | Extensible metadata (language, file count, etc.) |

**Indexes**:
- `idx_repositories_origin_url` UNIQUE on `origin_url`
- `idx_repositories_status` on `status`

---

### Table: `commits`

**Purpose**: Stores Git commit records.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `hash` | CHAR(40) | PK | Full SHA-1 hash |
| `repository_id` | UUID | FK → repositories, NOT NULL | Parent repository |
| `message` | TEXT | NOT NULL | Full commit message |
| `author_name` | VARCHAR(255) | NOT NULL | Author name |
| `author_email` | VARCHAR(255) | NOT NULL | Author email |
| `authored_date` | TIMESTAMPTZ | NOT NULL | Author timestamp |
| `committer_name` | VARCHAR(255) | NOT NULL | Committer name |
| `committer_email` | VARCHAR(255) | NOT NULL | Committer email |
| `committed_date` | TIMESTAMPTZ | NOT NULL | Committer timestamp |
| `parent_hashes` | TEXT[] | NOT NULL, DEFAULT '{}' | Parent commit SHAs (array) |
| `is_merge` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether this is a merge commit |
| `analysis_status` | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | (pending, processing, completed, failed) |
| `metadata` | JSONB | DEFAULT '{}' | Extensible (branch, tags, diff stats) |

**Indexes**:
- `idx_commits_repository_id` on `repository_id`
- `idx_commits_authored_date` on `(repository_id, authored_date DESC)`
- `idx_commits_analysis_status` on `analysis_status` WHERE `analysis_status != 'completed'`

---

### Table: `entities`

**Purpose**: Stores the canonical, current-state representation of each entity. One row per Stable Entity ID. This table represents the HEAD state of the graph.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `seid` | UUID | PK | Stable Entity ID |
| `repository_id` | UUID | FK → repositories, NOT NULL | Parent repository |
| `entity_type` | VARCHAR(50) | NOT NULL | (CLASS, FUNCTION, METHOD, MODULE, PACKAGE, etc.) |
| `canonical_name` | VARCHAR(1000) | NOT NULL | Current fully qualified name |
| `simple_name` | VARCHAR(255) | NOT NULL | Unqualified name |
| `file_path` | TEXT | NOT NULL | Current relative file path |
| `parent_seid` | UUID | FK → entities, NULLABLE | Parent entity in containment hierarchy |
| `language` | VARCHAR(20) | NOT NULL | Programming language |
| `start_line` | INTEGER | NULLABLE | Current start line |
| `end_line` | INTEGER | NULLABLE | Current end line |
| `content_hash` | CHAR(64) | NULLABLE | SHA-256 of current source text |
| `structural_fingerprint` | CHAR(64) | NULLABLE | Normalized AST hash |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether entity has been deleted |
| `first_seen_commit` | CHAR(40) | NOT NULL | Commit where entity was first observed |
| `last_seen_commit` | CHAR(40) | NOT NULL | Most recent commit where entity was observed |
| `version_count` | INTEGER | NOT NULL, DEFAULT 1 | Total number of versions |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | System creation timestamp |
| `metadata` | JSONB | DEFAULT '{}' | Type-specific attributes (parameters, decorators, visibility, etc.) |

**Indexes**:
- `idx_entities_repository_type` on `(repository_id, entity_type)`
- `idx_entities_file_path` on `(repository_id, file_path)`
- `idx_entities_canonical_name` on `(repository_id, canonical_name)`
- `idx_entities_parent` on `parent_seid`
- `idx_entities_not_deleted` on `(repository_id, entity_type)` WHERE `is_deleted = FALSE`
- `idx_entities_content_hash` on `content_hash`
- `idx_entities_structural_fp` on `structural_fingerprint`

**Constraint**: UNIQUE on `(repository_id, entity_type, canonical_name)` WHERE `is_deleted = FALSE`. Ensures no two live entities in the same repository share a type and qualified name.

---

### Table: `entity_versions`

**Purpose**: Stores the complete version history of every entity. One row per (SEID, commit) pair. This is the temporal backbone of the system.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Version record identifier |
| `seid` | UUID | FK → entities, NOT NULL | Stable Entity ID |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | The commit causing this version |
| `version_ordinal` | INTEGER | NOT NULL | Sequential version number (1, 2, 3...) |
| `mutation_type` | VARCHAR(20) | NOT NULL | (CREATED, MODIFIED, RENAMED, MOVED, DELETED) |
| `canonical_name` | VARCHAR(1000) | NOT NULL | Name at this version |
| `file_path` | TEXT | NOT NULL | File path at this version |
| `source_text` | TEXT | NULLABLE | Full source code at this version |
| `content_hash` | CHAR(64) | NULLABLE | SHA-256 of source text |
| `structural_fingerprint` | CHAR(64) | NULLABLE | Normalized AST hash |
| `start_line` | INTEGER | NULLABLE | Start line at this version |
| `end_line` | INTEGER | NULLABLE | End line at this version |
| `identity_confidence` | REAL | NOT NULL, DEFAULT 1.0 | Confidence of SEID linkage |
| `previous_name` | VARCHAR(1000) | NULLABLE | Prior name (if RENAMED) |
| `previous_path` | TEXT | NULLABLE | Prior path (if MOVED) |
| `diff_metadata` | JSONB | DEFAULT '{}' | Lines added/removed, change summary |
| `entity_metadata` | JSONB | DEFAULT '{}' | Full attribute snapshot at this version |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record creation timestamp |

**Indexes**:
- `idx_entity_versions_seid` on `(seid, version_ordinal DESC)`
- `idx_entity_versions_commit` on `commit_hash`
- `idx_entity_versions_mutation` on `(seid, mutation_type)`
- `idx_entity_versions_seid_commit` UNIQUE on `(seid, commit_hash)`

**Partitioning Consideration**: For repositories with millions of entity versions, consider range-partitioning by `commit_hash` prefix or by `created_at` month. This allows older partitions to be moved to cold storage.

---

### Table: `relationships`

**Purpose**: Stores the current-state relationships between entities. One row per directed edge in the structural graph at HEAD.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Relationship identifier |
| `repository_id` | UUID | FK → repositories, NOT NULL | Parent repository |
| `relationship_type` | VARCHAR(30) | NOT NULL | (CALLS, IMPORTS, EXTENDS, IMPLEMENTS, etc.) |
| `source_seid` | UUID | FK → entities, NOT NULL | Source entity |
| `target_seid` | UUID | FK → entities, NOT NULL | Target entity |
| `confidence` | REAL | NOT NULL, DEFAULT 1.0 | Extraction confidence |
| `evidence_file` | TEXT | NULLABLE | File containing the evidence |
| `evidence_line` | INTEGER | NULLABLE | Line number of evidence |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether relationship has been removed |
| `first_seen_commit` | CHAR(40) | NOT NULL | First commit where observed |
| `last_seen_commit` | CHAR(40) | NOT NULL | Most recent commit where observed |
| `metadata` | JSONB | DEFAULT '{}' | Relationship-specific attributes |

**Indexes**:
- `idx_relationships_source` on `(source_seid, relationship_type)`
- `idx_relationships_target` on `(target_seid, relationship_type)`
- `idx_relationships_type` on `(repository_id, relationship_type)`
- `idx_relationships_active` on `(repository_id, relationship_type)` WHERE `is_deleted = FALSE`

**Constraint**: UNIQUE on `(source_seid, target_seid, relationship_type)` WHERE `is_deleted = FALSE`.

---

### Table: `relationship_versions`

**Purpose**: Stores the temporal history of relationship changes. Records when relationships were created, modified, or deleted.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Version record identifier |
| `relationship_id` | UUID | FK → relationships, NOT NULL | Parent relationship |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Causing commit |
| `mutation_type` | VARCHAR(20) | NOT NULL | (CREATED, MODIFIED, DELETED) |
| `version_ordinal` | INTEGER | NOT NULL | Sequential version number |
| `metadata` | JSONB | DEFAULT '{}' | Change details |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Record timestamp |

**Indexes**:
- `idx_rel_versions_relationship` on `(relationship_id, version_ordinal DESC)`
- `idx_rel_versions_commit` on `commit_hash`

---

### Table: `semantic_metadata`

**Purpose**: Stores AI-generated metadata for entities. Separated from the `entities` table to maintain the boundary between deterministic and probabilistic data.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Record identifier |
| `seid` | UUID | FK → entities, NOT NULL | Target entity |
| `metadata_type` | VARCHAR(30) | NOT NULL | (SUMMARY, BUSINESS_PURPOSE, ARCH_ROLE, DOMAIN, RISK) |
| `content` | TEXT | NOT NULL | The generated metadata content |
| `model_identifier` | VARCHAR(100) | NOT NULL | LLM model used |
| `model_version` | VARCHAR(50) | NULLABLE | Model version string |
| `prompt_version` | VARCHAR(20) | NOT NULL | Version of the prompt template used |
| `entity_content_hash` | CHAR(64) | NOT NULL | Content hash of the entity when enrichment was run |
| `confidence` | REAL | NULLABLE | Model-reported confidence if available |
| `enrichment_version` | INTEGER | NOT NULL, DEFAULT 1 | Incremented on re-enrichment |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Generation timestamp |

**Indexes**:
- `idx_semantic_seid_type` UNIQUE on `(seid, metadata_type, enrichment_version)`
- `idx_semantic_seid` on `seid`

---

### Table: `embeddings`

**Purpose**: Stores vector embeddings for entities. Separated from semantic_metadata because embeddings have different query patterns (vector similarity) and storage characteristics (fixed-width dense vectors).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Record identifier |
| `seid` | UUID | FK → entities, NOT NULL | Target entity |
| `embedding` | VECTOR(1536) | NOT NULL | The embedding vector (dimension configurable) |
| `model_identifier` | VARCHAR(100) | NOT NULL | Embedding model used |
| `input_hash` | CHAR(64) | NOT NULL | Hash of the text input used for embedding |
| `dimensions` | INTEGER | NOT NULL | Vector dimensionality |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Generation timestamp |

**Indexes**:
- `idx_embeddings_seid` UNIQUE on `(seid, model_identifier)`
- `idx_embeddings_vector` using HNSW on `embedding vector_cosine_ops` (for approximate nearest neighbor queries)

**Note on HNSW vs. IVFFlat**: HNSW provides better recall and does not require training on a data sample, making it preferable for incrementally growing datasets. IVFFlat is faster to build but requires periodic re-training as data grows.

---

### Table: `graph_snapshots`

**Purpose**: Stores materialized checkpoints of the entity graph at specific commits, enabling fast temporal reconstruction without replaying all events from the beginning.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Snapshot identifier |
| `repository_id` | UUID | FK → repositories, NOT NULL | Repository |
| `commit_hash` | CHAR(40) | FK → commits, NOT NULL | Snapshot commit |
| `entity_seids` | UUID[] | NOT NULL | Array of all live SEIDs at this commit |
| `snapshot_data` | JSONB | NOT NULL | Serialized entity states (compressed) |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_snapshots_repo_commit` UNIQUE on `(repository_id, commit_hash)`

---

## 10.3 Entity-Relationship Diagram

```
┌──────────────┐       ┌──────────────┐
│ repositories │       │   commits    │
│──────────────│       │──────────────│
│ id (PK)      │◀──────│ repository_id│
│ name         │       │ hash (PK)    │
│ origin_url   │       │ message      │
│ ...          │       │ author_*     │
└──────┬───────┘       │ parent_hashes│
       │               └──────┬───────┘
       │                      │
       ▼                      │
┌──────────────┐              │
│   entities   │              │
│──────────────│              │
│ seid (PK)    │◀─────────────┤ (first/last_seen_commit)
│ repository_id│              │
│ entity_type  │              │
│ canonical_   │              │
│   name       │              │
│ parent_seid  │──┐ (self-ref)│
│ is_deleted   │◀─┘           │
│ ...          │              │
└──┬───┬───┬───┘              │
   │   │   │                  │
   │   │   │   ┌──────────────▼───────┐
   │   │   │   │  entity_versions     │
   │   │   │   │─────────────────────-│
   │   │   └──▶│ seid (FK)            │
   │   │       │ commit_hash (FK)     │
   │   │       │ mutation_type        │
   │   │       │ source_text          │
   │   │       │ ...                  │
   │   │       └──────────────────────┘
   │   │
   │   │       ┌──────────────────────┐
   │   │       │  semantic_metadata   │
   │   │       │──────────────────────│
   │   └──────▶│ seid (FK)            │
   │           │ metadata_type        │
   │           │ content              │
   │           │ model_identifier     │
   │           │ ...                  │
   │           └──────────────────────┘
   │
   │           ┌──────────────────────┐
   │           │     embeddings       │
   │           │──────────────────────│
   └──────────▶│ seid (FK)            │
               │ embedding (VECTOR)   │
               │ model_identifier     │
               │ ...                  │
               └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────────────┐
│   relationships      │     │  relationship_versions       │
│──────────────────────│     │──────────────────────────────│
│ id (PK)              │◀────│ relationship_id (FK)         │
│ source_seid (FK)     │     │ commit_hash (FK)             │
│ target_seid (FK)     │     │ mutation_type                │
│ relationship_type    │     │ ...                          │
│ ...                  │     └──────────────────────────────┘
└──────────────────────┘
```

## 10.4 Normalization Decisions

**Entities vs. Entity Versions**: The `entities` table is denormalized for the HEAD state to optimize the most common query pattern (current graph traversal). The `entity_versions` table is the normalized source of truth. If the `entities` table were lost, it could be reconstructed by replaying `entity_versions`.

**Metadata as JSONB**: Entity-type-specific attributes (parameters for functions, base classes for classes, members for enums) are stored in JSONB `metadata` columns rather than in type-specific tables. This is a deliberate denormalization that avoids a proliferation of tables (one per entity type) and supports ontology extension without schema migrations. The trade-off is weaker type enforcement at the database level, which must be compensated by application-layer validation.

**Semantic Metadata Separated**: AI-generated metadata is stored in a separate table rather than as columns on `entities` because:
1. It has different provenance and reliability characteristics.
2. It has different update cadences (may be regenerated independently of entity changes).
3. It supports versioning (multiple enrichment versions per entity).
4. It avoids polluting the deterministic entity schema with probabilistic data.

---

# Section 11: Query Requirements

## 11.1 Query Categories

The system must support five categories of queries, each with distinct execution characteristics.

### Category 1: Dependency Analysis

**Purpose**: Understanding what an entity depends on and what depends on it.

**Example Queries**:

**Q1**: "What does `UserService` depend on?"
```
Execution:
1. Resolve "UserService" to SEID via canonical_name lookup in entities table.
2. Query relationships WHERE source_seid = SEID AND is_deleted = FALSE.
3. For each relationship, join to entities to get target entity details.
4. Group by relationship_type.
Result: Categorized list of dependencies (calls, imports, extends, uses).
```

**Q2**: "What breaks if `PaymentGateway` changes?"
```
Execution:
1. Resolve "PaymentGateway" to SEID.
2. Recursive CTE: Find all entities that transitively depend on PaymentGateway.
   WITH RECURSIVE dependents AS (
     SELECT target_seid AS seid FROM relationships 
     WHERE source_seid = :gateway_seid AND is_deleted = FALSE
     UNION
     SELECT r.target_seid FROM relationships r
     JOIN dependents d ON r.source_seid = d.seid
     WHERE r.is_deleted = FALSE
   )
3. Return all entities in the dependent set with their entity_type and canonical_name.
Result: Transitive impact set, ordered by hop distance.
```

**Q3**: "Which packages have circular dependencies?"
```
Execution:
1. Extract all IMPORTS relationships between Module entities.
2. Aggregate to package level (group by parent_seid of source and target modules).
3. Build directed adjacency list of package-level imports.
4. Run cycle detection (Tarjan's algorithm or DFS-based).
Result: List of strongly connected components containing more than one package.
```

### Category 2: Impact Analysis

**Purpose**: Predicting the consequences of a proposed change.

**Q4**: "If I modify `calculate_tax`, what tests need to run?"
```
Execution:
1. Resolve "calculate_tax" to SEID.
2. Find all entities connected by TESTS relationship targeting calculate_tax's SEID.
3. Additionally, find all callers of calculate_tax (reverse CALLS edges).
4. For each caller, find TESTS relationships targeting the caller.
5. Union the test sets.
Result: Direct tests + indirect tests (tests of callers).
```

**Q5**: "What API endpoints are affected if the User database model changes?"
```
Execution:
1. Resolve User DatabaseModel to SEID.
2. Find all entities with DEPENDS_ON or READS/WRITES edges to User model.
3. For each dependent entity, traverse CALLS graph upward until reaching an APIEndpoint entity.
4. Return the set of reached APIEndpoints with their route patterns.
Result: API endpoints transitively depending on the User model.
```

### Category 3: Architecture Exploration

**Purpose**: Understanding system structure and organization.

**Q6**: "Show me the architecture of the billing module."
```
Execution:
1. Resolve "billing" to a Package SEID.
2. Recursive BELONGS_TO traversal: Find all entities contained within the billing package.
3. Find all relationships (any type) between entities in the result set.
4. Return the entity set and relationship set as a subgraph.
Result: Complete subgraph of the billing package.
```

**Q7**: "What are the most central classes in the system?" (PageRank-style)
```
Execution:
1. Extract all non-deleted entities of type CLASS.
2. Extract all relationships between them.
3. Compute in-degree (fan-in) for each class.
4. Optionally compute eigenvector centrality or PageRank on the subgraph.
5. Return top-N classes by centrality score.
Result: Ranked list of architecturally central classes.
```

### Category 4: Temporal Reconstruction

**Purpose**: Understanding code evolution over time.

**Q8**: "How has `InvoiceProcessor` evolved over the last 6 months?"
```
Execution:
1. Resolve "InvoiceProcessor" to SEID.
2. Query entity_versions WHERE seid = SEID
   AND commit_hash IN (SELECT hash FROM commits WHERE authored_date >= NOW() - INTERVAL '6 months')
   ORDER BY version_ordinal ASC.
3. Return the version chain with mutation types and diff metadata.
Result: Chronological list of modifications with diffs.
```

**Q9**: "What did the billing module look like at tag v2.0?"
```
Execution:
1. Resolve tag v2.0 to commit hash.
2. Find nearest graph_snapshot before that commit, or replay entity_versions up to that commit.
3. Filter reconstructed entity set to those belonging to the billing package.
4. Reconstruct relationships at that point in time.
Result: Full snapshot of billing module at v2.0.
```

### Category 5: Historical Comparison

**Purpose**: Comparing system state across time points.

**Q10**: "What entities were added or removed between v1.0 and v2.0?"
```
Execution:
1. Resolve v1.0 and v2.0 to commit hashes.
2. Reconstruct entity sets at both commits.
3. Compute set difference:
   - Added = entities in v2.0 not in v1.0 (by SEID)
   - Removed = entities in v1.0 not in v2.0 (by SEID)
   - Modified = entities in both with different content_hash
Result: Three categorized lists.
```

**Q11**: "Which commit introduced a bug in the payment flow?"
```
Execution:
1. Semantic search for "payment flow" → set of relevant entity SEIDs.
2. For each entity, retrieve version chain.
3. Present to user (or agent) for bisection analysis.
4. Agent can examine source_text at each version to identify the problematic change.
Result: Candidate commits with associated entity changes.
```

---

# Section 12: Future Compatibility

## 12.1 Neo4j Integration Path

The current architecture stores graph data in PostgreSQL adjacency lists. The migration path to Neo4j is enabled by the repository interface pattern:

1. The `graph` bounded context defines `ITemporalGraphRepository`, `IEntityRepository`, and `IRelationshipRepository` as abstract interfaces in the domain layer.
2. The current implementation (`PostgresTemporalGraphRepository`) resides in the infrastructure layer.
3. To add Neo4j: Create `Neo4jTemporalGraphRepository` implementing the same interfaces. This class translates domain operations into Cypher queries.
4. Both implementations can coexist: PostgreSQL as the system of record, Neo4j as a read-optimized projection synced via domain events.

**What must be preserved**: The interface must not expose storage-specific query patterns. Methods like `find_transitive_dependents(seid, max_depth)` are acceptable. Methods like `execute_cypher(query_string)` or `execute_recursive_cte(sql)` are not.

## 12.2 LangGraph Integration Path

LangGraph integration maps naturally onto the `agentic` bounded context:

1. **State**: LangGraph state objects are defined in `agentic/domain/state.py`. They contain the current query, retrieved context, intermediate reasoning steps, and planned next actions.
2. **Nodes**: Each LangGraph node is an application service function that receives state, performs an operation (query the graph, summarize results, plan next step), and returns updated state.
3. **Tools**: LangGraph tools wrap Retrieval Engine use cases. A `search_entities` tool calls `ExecuteHybridSearchUseCase`. A `get_dependencies` tool calls `GetEntityDependenciesUseCase`. Tools are defined in `agentic/application/tools/`.
4. **Graph Definition**: The LangGraph execution graph (nodes + edges + conditional routing) is defined in `agentic/infrastructure/framework/`. This is infrastructure because it depends on the LangGraph library.

**Key constraint**: The Agentic Engine must not bypass the Retrieval Engine to access the database directly. All data access flows through the established query interfaces. This ensures that access control, caching, and observability instrumentation applied at the Retrieval layer also apply to agent queries.

## 12.3 Multi-Agent Systems

Multi-agent workflows (e.g., an "Architect Agent" that coordinates a "Dependency Analyst Agent" and a "Change Impact Agent") are supported by:

1. **Agent Composition**: The `agentic/application/agents/` directory contains agent blueprints. Each agent is a LangGraph graph definition with a specific tool set and prompt strategy.
2. **Agent Communication**: Agents communicate through a shared state store (LangGraph checkpointer) or through an event bus. The architecture does not prescribe a specific inter-agent protocol; this is a future design decision.
3. **Tool Isolation**: Each agent has access to a defined subset of tools. The Dependency Analyst Agent cannot directly modify the graph; it can only query.

## 12.4 Event Sourcing

The `entity_versions` and `relationship_versions` tables already constitute an event store. Full event sourcing requires:

1. **Event Bus**: Introduce an in-process event bus (initially) or a distributed event bus (Kafka, Redis Streams) for cross-context event propagation.
2. **Event Handlers**: Each bounded context subscribes to events it cares about. The Semantic Enrichment context subscribes to `EntityModified` events to trigger re-enrichment.
3. **Event Replay**: The ability to reconstruct any bounded context's state by replaying its event log from the beginning.

The current architecture is event-sourcing-ready because the `entity_versions` table is append-only and causally ordered. The remaining work is adding the event bus and making context interactions event-driven rather than synchronous.

## 12.5 Distributed Workers

The bounded context architecture enables horizontal scaling:

1. **Stateless Workers**: The Parsing Engine and Extraction Engine contexts are stateless — they receive input, produce output, and maintain no local state. They can be scaled horizontally behind a task queue (Celery + Redis).
2. **Task Granularity**: The natural unit of work is one file per task (for parsing) or one commit per task (for extraction and graph building).
3. **Ordering Constraints**: Graph building must process commits in topological order (parent before child) within a single repository. This constrains parallelism to cross-repository or cross-file within a single commit, but not cross-commit within a single repository.

## 12.6 Multi-Repository Analysis

Multi-repository analysis requires:

1. **Cross-Repository Relationships**: A new relationship type `EXTERNAL_DEPENDS_ON` connecting entities in one repository to entities in another. This arises from shared libraries, API contracts, and protobuf/IDL definitions.
2. **Repository Groups**: A new aggregate `RepositoryGroup` that defines a set of repositories to be analyzed together.
3. **Global Entity Resolution**: When Repository A imports `payment-sdk`, and Repository B publishes `payment-sdk`, the system must link entities across repository boundaries. This requires a global entity registry.

The current schema supports this: the `entities` and `relationships` tables include `repository_id`, allowing cross-repository queries. The SEID is globally unique (UUID), so cross-repository relationships can reference entities in different repositories.

## 12.7 Architecture Intelligence and Automated Code Review

These are consumer applications built on top of the knowledge graph:

1. **Architecture Intelligence**: Queries the graph for structural patterns (dependency cycles, god classes, feature envy), computes architectural metrics (instability, abstractness), and generates architecture reports. This is a new bounded context (`architecture_intelligence`) that reads from the graph and produces reports.
2. **Automated Code Review**: For a given pull request (set of changed files), queries the graph to identify affected entities, assesses impact, checks for architectural violations, and generates review comments. This is another consumer context (`code_review`) that combines temporal analysis (what changed) with structural analysis (what is affected).

Both are enabled by the existing architecture without modifications to the core graph or temporal model.

---

# Section 13: Architectural Review

## 13.1 Self-Critique

### Weakness 1: Entity Identity Accuracy

**Risk**: The composite identity resolution algorithm (Section 4) relies on heuristic matching. False positives (incorrectly linking two different entities) corrupt the temporal chain. False negatives (failing to link the same entity across versions) fragment the history.

**Severity**: High. Identity errors compound over time — once a chain is broken, all subsequent versions are orphaned.

**Mitigation**:
- Store `identity_confidence` on every version record. Expose low-confidence linkages in the UI for human review.
- Implement a "re-resolution" capability that can retroactively correct identity linkages when better information is available.
- Log all identity decisions to enable post-hoc analysis of resolution quality.
- Establish a benchmark dataset of known renames/moves to validate the algorithm's accuracy before production deployment.

---

### Weakness 2: PostgreSQL Graph Traversal Performance

**Risk**: Recursive CTEs in PostgreSQL for multi-hop graph traversal (impact analysis, transitive dependency computation) will degrade on large graphs. A recursive CTE visiting 50,000 edges across 5 hops can take seconds, which is unacceptable for interactive queries.

**Severity**: Medium initially, High at scale.

**Mitigation**:
- **Materialized transitive closure**: For critical relationships (CALLS, IMPORTS), precompute and materialize the transitive closure as a separate table. Update incrementally on graph changes.
- **Depth limits**: All recursive queries must enforce a maximum depth (default: 5 hops). Unbounded recursion is architecturally forbidden.
- **Query caching**: Cache frequently-executed graph queries with TTL-based invalidation on graph updates.
- **Neo4j fallback**: The repository interface abstraction allows migrating traversal-heavy queries to Neo4j without changing application code.

---

### Weakness 3: Storage Growth for Large Repositories

**Risk**: Storing full `source_text` in every `entity_version` record for a repository with 30,000 entities and 20 average versions each produces 600,000 text records. If average source text is 2 KB, that is 1.2 GB of text data for a single repository.

**Severity**: Medium.

**Mitigation**:
- **Content-addressable storage**: Deduplicate source text by content hash. If 40% of versions are formatting-only changes that don't alter the content hash, deduplication saves significant space. Store source text in a separate `source_content` table keyed by content_hash, and reference it from `entity_versions`.
- **Compression**: Apply TOAST compression (PostgreSQL's default for large text) and consider explicit zstd compression for the source_content table.
- **Tiered retention**: Full source text for the last N versions (e.g., 10); only content_hash and diff_metadata for older versions. Source text for old versions can be reconstructed from the Git repository on demand.

---

### Weakness 4: Semantic Enrichment Staleness

**Risk**: When an entity is modified, its semantic metadata (summary, domain classification) may become stale. If re-enrichment is delayed or fails, users receive outdated semantic data without warning.

**Severity**: Medium.

**Mitigation**:
- Store `entity_content_hash` alongside every semantic metadata record. At query time, compare this hash against the entity's current content_hash. If they differ, annotate the result as "semantic metadata may be outdated."
- Implement a background process that scans for stale semantic metadata (entity_content_hash != current content_hash) and queues re-enrichment.
- Never block entity ingestion on enrichment completion. Entities should be queryable (via structural and temporal layers) immediately; semantic data arrives asynchronously.

---

### Weakness 5: Handling of Dynamic Languages

**Risk**: In dynamically typed languages (Python, JavaScript, Ruby), static analysis cannot resolve all CALLS and DEPENDS_ON relationships. Dynamic dispatch, monkey-patching, metaprogramming, and string-based imports create relationship edges that are invisible to AST analysis.

**Severity**: Medium. The graph will be incomplete for dynamic language codebases.

**Mitigation**:
- Accept that the extracted graph is a **lower bound** on the true dependency graph. Document this limitation clearly.
- Use heuristic inference (naming conventions, common patterns) to infer likely relationships with lower confidence scores.
- Flag entities using metaprogramming patterns (e.g., `getattr`, `eval`, `importlib`) for human review.
- Reserve the architecture for future integration of runtime trace analysis, which would provide ground-truth call graphs for dynamic languages.

---

### Weakness 6: Merge Commit Semantics

**Risk**: Merge commits create ambiguity in temporal analysis. If branch A modifies entity X at commit A3, and branch B modifies entity X at commit B2, and these are merged at commit M, what is entity X's version history? Does M create a new version? Which branch's version takes precedence?

**Severity**: Medium. Incorrect merge handling can produce duplicate or conflicting version records.

**Mitigation**:
- **Merge commit analysis policy**: When processing a merge commit, compare the merged state against both parents. Only record a version if the merged content differs from the entity's state in the first parent (the mainline). If the merge simply fast-forwards, no new version is recorded.
- **Branch tracking**: Entity versions optionally track the branch on which they were created. This allows users to view branch-specific history.
- **Conflict detection**: If entity X was modified in both branches being merged, record a `MERGE_MODIFIED` event (a subtype of MODIFIED) with metadata referencing both parent versions.

---

### Weakness 7: Initial Ingestion Time

**Risk**: Full historical analysis of a large repository (100,000 commits) may take many hours. During this time, the system has incomplete data. Users may not wait.

**Severity**: Medium for user adoption.

**Mitigation**:
- **HEAD-first ingestion**: Process the latest commit immediately (minutes), providing a complete current-state graph. Queue historical commits for background processing.
- **Progress reporting**: Expose ingestion progress via API (e.g., "analyzed 15,000 of 100,000 commits, estimated time remaining: 4 hours").
- **Incremental availability**: As historical commits are processed, new temporal data becomes available for queries without requiring a full re-index.
- **Prioritized history**: Process recent history first (last 1,000 commits), then backfill older history. This aligns with user query patterns (most temporal queries focus on recent changes).

---

### Weakness 8: Schema Evolution

**Risk**: The JSONB `metadata` columns provide flexibility but lack schema enforcement. As the system evolves, different versions of the code may write different metadata structures, leading to inconsistent data.

**Severity**: Low initially, Medium over time.

**Mitigation**:
- Define Pydantic models for all JSONB structures. Validate metadata at the application layer before writing. Reject invalid metadata.
- Version the metadata schema. Include a `metadata_schema_version` field in JSONB payloads.
- Write migration scripts that can transform old metadata formats to new formats when schemas evolve.

---

This concludes the formal architecture specification. The document provides sufficient detail for an engineering team to begin implementation across all bounded contexts, starting with the Repository Management and Git Analysis contexts, proceeding through Parsing and Extraction, building the Graph Engine core, and layering Semantic Enrichment and Retrieval capabilities on top.
