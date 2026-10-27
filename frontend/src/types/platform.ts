/**
 * TypeScript types for the Software Intelligence Platform.
 * All types mirror actual FastAPI backend schemas in src/presentation/schemas/.
 *
 * Keep this file as the single source of truth for frontend data shapes —
 * every API method in `lib/api/endpoints.ts` is typed against an interface here.
 */

// ============================================================
// REPOSITORY
// ============================================================

export interface Repository {
  id: string;
  name: string;
  url: string;
  default_branch: string;
  status: string;
  entity_count?: number;
  file_count?: number;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface IngestRepositoryRequest {
  url: string;
  branch?: string;
  name?: string;
}

export interface IngestionResult {
  repository_id: string;
  status: string; // PENDING | COMPLETED | FAILED | ...
  files_scanned: number;
  entities_extracted: number;
  relationships_extracted?: number;
  errors?: string[];
}

export interface RepositoryHealth {
  status: "healthy" | "warning" | "critical" | "unknown";
  score: number;
  message: string;
  risk_score?: number;
  coverage_score?: number;
  drift_score?: number;
  architecture_type?: string;
}

// ============================================================
// CAPABILITY
// ============================================================

export interface Capability {
  id: string;
  repository_id: string;
  name: string;
  description?: string;
  confidence: number;
  capability_type: string;
  maturity_score: number;
  risk_score: number;
  coverage_score: number;
  concepts: string[];
  behaviors: string[];
  flows: string[];
  entities: string[];
  relationships: string[];
  created_at: string;
  // Derived/computed fields
  health_score?: number;
  owner?: string;
  category?: string;
}

export interface CapabilityCandidate {
  id: string;
  repository_id: string;
  name: string;
  description?: string;
  confidence: number;
  status: "PENDING" | "APPROVED" | "REJECTED";
  evidence: CapabilityEvidence;
  capability_type: string;
  created_at: string;
}

export interface CapabilityEvidence {
  concepts: string[];
  behaviors: string[];
  flows: string[];
  entities: string[];
  supporting_relationships: string[];
  confidence_breakdown: Record<string, number>;
}

export interface CapabilityHealthRisk {
  capability_id: string;
  health_score: number;
  risk_score: number;
  stability_score: number;
  cohesion_score: number;
  coupling_score: number;
  boundary_strength: number;
  boundary_leakage_detected: boolean;
}

export interface CapabilityBlastRadius {
  capability_id: string;
  blast_radius_score: number;
  impacted_capability_ids: string[];
  impact_depth: number;
}

export interface CapabilityTimelineEntry {
  commit_hash: string;
  timestamp: string;
  features: Record<string, unknown>;
}

export interface CapabilityTimeline {
  capability_id: string;
  timeline: CapabilityTimelineEntry[];
}

export interface CapabilityRelationship {
  id: string;
  repository_id: string;
  source_capability_id: string;
  target_capability_id: string;
  relationship_type: string;
  dependency_type: string;
}

export interface CapabilityFilters {
  search?: string;
  category?: string;
  risk_level?: string;
  capability_type?: string;
  limit?: number;
  offset?: number;
}

// ============================================================
// CONCEPTS
// ============================================================

export interface Concept {
  id: string;
  name: string;
  description?: string;
  concept_type?: string;
  version?: string;
  related_capabilities?: string[];
  health_score?: number;
  created_at?: string;
}

export interface ConceptMapNode {
  concept_id: string;
  name: string;
  layer: string;
  health_score: number;
  related_capabilities: string[];
}

export interface ConceptMapEdge {
  from_concept_id: string;
  to_concept_id: string;
  relationship: string;
  weight: number;
}

export interface ConceptMapResponse {
  repository_id: string;
  nodes: ConceptMapNode[];
  edges: ConceptMapEdge[];
  generated_at: string;
}

export interface ConceptDriftResponse {
  concept_id: string;
  drift_score: number;
  drifted_dimensions: Record<string, number>;
  from_commit: string;
  to_commit: string;
  detected_at: string;
}

export interface ConceptExplanationResponse {
  concept_id: string;
  summary: string;
  evidence: Array<{
    entity_seid: string;
    relationship_id?: string;
    excerpt: string;
  }>;
  confidence: number;
}

export interface BackfillResponse {
  job_id: string;
  status: string;
  queued_count: number;
  estimated_duration_seconds?: number;
}

export interface FrameworkDefinitionResponse {
  framework_id: string;
  name: string;
  version: string;
  concept_ids: string[];
  description?: string;
}

export interface FrameworkVersionResponse {
  framework_id: string;
  version: string;
  released_at: string;
  breaking_changes: string[];
}

export interface BehaviorFamilyResponse {
  family_id: string;
  name: string;
  description: string;
  behavior_ids: string[];
}

export interface CanonicalBehaviorResponse {
  behavior_id: string;
  name: string;
  family_id: string;
  description: string;
}

export interface BehaviorAliasResponse {
  alias: string;
  canonical_behavior_id: string;
  occurrences: number;
}

export interface CanonicalFlowResponse {
  flow_id: string;
  flow_type: string;
  source_entity_id: string;
  target_entity_id: string;
  concept_ids: string[];
}

export interface ConceptEvolutionResponse {
  concept_id: string;
  timeline: Array<{
    commit_hash: string;
    timestamp: string;
    state: Record<string, unknown>;
  }>;
}

// ============================================================
// SEARCH
// ============================================================

export interface CapabilityQueryRequest {
  query_text: string;
  limit?: number;
}

export interface CapabilityQueryResult {
  capability: Capability;
  relevance_score: number;
  matching_evidence: string[];
}

export interface CapabilityQueryResponse {
  results: CapabilityQueryResult[];
}

export interface SearchResult {
  capabilities: CapabilityQueryResult[];
  concepts: Concept[];
  total: number;
  query: string;
}

// ============================================================
// API COMMON
// ============================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiError {
  code: string;
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

export class DomainError extends Error {
  public readonly code: string;
  public readonly status: number;
  public readonly details?: Record<string, unknown>;

  constructor(code: string, message: string, status: number, details?: Record<string, unknown>) {
    super(message);
    this.name = "DomainError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

// HTTP status → domain error code mapping
export const HTTP_ERROR_CODES: Record<number, string> = {
  400: "VALIDATION_ERROR",
  401: "UNAUTHORIZED",
  403: "FORBIDDEN",
  404: "NOT_FOUND",
  408: "TIMEOUT",
  409: "CONFLICT",
  422: "VALIDATION_ERROR",
  429: "RATE_LIMITED",
  500: "INTERNAL_ERROR",
  502: "BAD_GATEWAY",
  503: "SERVICE_UNAVAILABLE",
  504: "GATEWAY_TIMEOUT",
};

// ============================================================
// PLATFORM / GRAPH TYPES
// ============================================================

export interface GraphNode<T = Record<string, unknown>> {
  id: string;
  type: string;
  label: string;
  data: T;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  animated?: boolean;
}

export type SemanticLayer =
  | "structural"
  | "semantic"
  | "behavior"
  | "concept"
  | "capability"
  | "architecture"
  | "decision";

export type RiskLevel = "low" | "medium" | "high" | "critical";
export type HealthStatus = "healthy" | "warning" | "critical" | "unknown";
export type CapabilityType = "AI" | "BUSINESS" | "TECHNICAL" | "INFRASTRUCTURE" | "SECURITY" | "INTEGRATION";

// ============================================================
// ENTITIES / RELATIONSHIPS / GRAPH
// ============================================================

export type EntityType = "MODULE" | "CLASS" | "FUNCTION" | "METHOD" | string;

export interface GraphEntity {
  seid: string;
  entity_type: EntityType;
  name: string;
  qualified_name: string;
  file_path?: string;
  language?: string;
  layer?: string;
  start_line?: number;
  end_line?: number;
  parent_seid?: string | null;
  metadata?: Record<string, unknown>;
}

export interface GraphRelationship {
  id: string;
  relationship_type: string;
  source_seid: string;
  target_seid: string;
  source_name?: string | null;
  target_name?: string | null;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface GraphNeighborhood {
  seed_seid: string;
  nodes: GraphEntity[];
  edges: GraphRelationship[];
  truncated: boolean;
}

// ============================================================
// TEMPORAL
// ============================================================

export interface Commit {
  hash: string;
  repository_id: string;
  author: string;
  email: string;
  message: string;
  timestamp: string;
  parent_hashes: string[];
  is_merge?: boolean;
  is_root?: boolean;
  files_changed?: number;
  insertions?: number;
  deletions?: number;
}

export interface CommitChange {
  id: string;
  repository_id: string;
  commit_hash: string;
  seid: string;
  change_type: "ADDED" | "MODIFIED" | "REMOVED" | string;
  mutation_type?: string;
  metadata?: Record<string, unknown>;
}

export interface TemporalGraph {
  entities: GraphEntity[];
  relationships: GraphRelationship[];
  commit_hash?: string;
}

export interface EntityVersion {
  id: string;
  seid: string;
  commit_hash: string;
  version_ordinal: number;
  state?: Record<string, unknown>;
  canonical_name?: string;
  file_path?: string;
  start_line?: number;
  end_line?: number;
  content_hash?: string;
  structural_fingerprint?: string;
  source_text?: string | null;
  mutation_type?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
}

export interface TimelineEntry {
  commit_hash: string;
  timestamp: string;
  message: string;
  changes: CommitChange[];
}

// ============================================================
// ARCHITECTURE INTELLIGENCE
// ============================================================

export type ArchitectureType =
  | "LAYERED"
  | "CLEAN"
  | "HEXAGONAL"
  | "ONION"
  | "CQRS"
  | "EVENT_DRIVEN"
  | "EVENT_SOURCED"
  | "SAGA"
  | "MICROSERVICE"
  | "MODULAR_MONOLITH"
  | "DOMAIN_DRIVEN_DESIGN"
  | (string & {});

export type ViolationSeverity = "INFO" | "WARNING" | "ERROR" | "CRITICAL";

export type ArchitectureDriftType =
  | "DEPENDENCY_DRIFT"
  | "FLOW_DRIFT"
  | "CAPABILITY_DRIFT"
  | "OWNERSHIP_DRIFT"
  | "TOPOLOGY_DRIFT"
  | "STYLE_DRIFT";

export type RefactoringCandidateType =
  | "GOD_CLASS"
  | "BLOB_SERVICE"
  | "FEATURE_ENVY"
  | "SHOTGUN_SURGERY"
  | "LARGE_METHOD"
  | "CYCLE"
  | "LOW_COHESION"
  | "HIGH_COUPLING"
  | "ARCHITECTURE_VIOLATION"
  | "CAPABILITY_OVERLOAD"
  | "SERVICE_OVERLOAD";

export type RefactoringPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface ArchitectureConfidence {
  score: number;
  topology_match: number;
  dependency_match: number;
  flow_match: number;
  capability_match: number;
  ownership_match: number;
  historical_match: number;
  evidence_coverage: number;
}

export interface ArchitectureFitness {
  coupling_score: number;
  cohesion_score: number;
  instability_score: number;
  abstractness_score: number;
  distance_from_main_sequence: number;
  cyclicity_score: number;
  layer_violation_score: number;
  overall_score: number;
  formulas: Record<string, string>;
}

export interface ArchitectureViolation {
  id: string;
  rule_name: string;
  severity: ViolationSeverity;
  affected_entities: string[];
  affected_capabilities: string[];
  reason: string;
  evidence: Record<string, unknown>;
}

export interface ArchitectureInvariant {
  name: string;
  description: string;
  rule_expression: string;
  severity: ViolationSeverity;
}

export interface ArchitectureDrift {
  id: string;
  drift_type: ArchitectureDriftType;
  previous_state: Record<string, unknown>;
  current_state: Record<string, unknown>;
  delta: Record<string, unknown>;
  confidence: number;
  from_commit: string;
  to_commit: string;
  detected_at: string;
}

export interface ArchitectureTimelineEntry {
  commit_hash: string;
  architecture_type: ArchitectureType;
  key_changes: string[];
  fitness_score: number;
  timestamp: string;
}

export interface ArchitectureTimeline {
  id: string;
  repository_id: string;
  entries: ArchitectureTimelineEntry[];
  generated_at: string;
}

export interface ArchitectureBenchmark {
  id: string;
  repository_id: string;
  commit_hash: string;
  current_fitness: number;
  historical_average: number;
  best_fitness: number;
  worst_fitness: number;
  measured_at: string;
}

export interface ArchitectureSimilarity {
  id: string;
  source_repository_id: string;
  target_repository_id: string;
  similarity_score: number;
  shared_capabilities: string[];
  measured_at: string;
}

export interface ArchitectureSnapshot {
  snapshot_id: string;
  repository_id: string;
  commit_hash: string;
  architecture_profiles: Array<Record<string, unknown>>;
  created_at: string;
}

export interface ArchitectureProfile {
  id: string;
  architecture_type: ArchitectureType;
  confidence: ArchitectureConfidence;
  description: string;
  evidence: Record<string, unknown>;
  detected_at: string;
  repository_id: string;
  commit_hash: string;
}

export interface ArchitectureRecommendation {
  id: string;
  recommendation_type: string;
  target_elements: string[];
  action_description: string;
  priority: RefactoringPriority;
  expected_benefit: string;
}

export interface OwnershipProfile {
  id: string;
  repository_id: string;
  commit_hash: string;
  capability_ownership: Record<string, string[]>;
  knowledge_silos: string[];
  bus_factor_risks: Array<Record<string, unknown>>;
  unowned_capabilities: string[];
  overloaded_teams: Array<Record<string, unknown>>;
  ownership_drift: Array<Record<string, unknown>>;
  detected_at: string;
  evidence_sources: string[];
}

export interface RefactoringCandidate {
  id: string;
  candidate_type: RefactoringCandidateType;
  priority: RefactoringPriority;
  target_entities: string[];
  evidence: Record<string, unknown>;
  expected_benefit: string;
  fitness_impact: number;
  detected_at: string;
}

export interface ArchitectureGraphNode {
  node_id: string;
  node_type: string;
  label: string;
  metadata: Record<string, unknown>;
}

export interface ArchitectureGraphEdge {
  from_id: string;
  to_id: string;
  relationship: string;
}

export interface ArchitectureGraph {
  nodes: Record<string, ArchitectureGraphNode>;
  edges: ArchitectureGraphEdge[];
}

// ============================================================
// DECISIONS
// ============================================================

export type DecisionType =
  | "TECHNOLOGY_ADOPTION"
  | "TECHNOLOGY_REMOVAL"
  | "ARCHITECTURAL_PATTERN"
  | "TRADE_OFF"
  | "DEFERRED"
  | (string & {});

export type DecisionStatus = "ACTIVE" | "DEPRECATED" | "PROPOSED" | (string & {});

export interface Decision {
  id: string;
  repository_id: string;
  name: string;
  description: string;
  decision_type: DecisionType;
  status: DecisionStatus;
  intent_ids?: string[];
  commit_hash?: string;
  detected_at: string;
  confidence?: number;
  evidence?: DecisionEvidence;
  versions?: DecisionVersion[];
  fitness?: DecisionFitness;
  conflicts?: DecisionConflict[];
  causal_relationships?: CausalRelationship[];
}

export interface DecisionDetail extends Decision {
  // DecisionDetail extends Decision with the same fields plus a few more
  // resolved at fetch time.
  summary?: string;
  rationale?: string;
}

export interface DecisionEvidence {
  commit_hashes: string[];
  source_files: string[];
  confidence_breakdown?: Record<string, number>;
  rationale?: string;
}

export interface DecisionVersion {
  id: string;
  decision_id: string;
  version_ordinal: number;
  state: Record<string, unknown>;
  commit_hash: string;
  detected_at: string;
}

export interface DecisionFitness {
  decision_id: string;
  fitness_score: number;
  alignment_score: number;
  risk_score: number;
  rationale: string;
  evaluated_at: string;
}

export interface DecisionConflict {
  id: string;
  conflict_type: string;
  severity: string;
  rationale: string;
  involved_decision_ids: string[];
  detected_at: string;
}

export interface CausalRelationship {
  id: string;
  source_decision_id: string;
  target_decision_id: string;
  relationship_type: "CAUSED" | "ENABLED" | "CONSTRAINED" | "DEPRECATED";
  rationale: string;
  confidence: number;
}

export interface CausalChain {
  id: string;
  chain_label: string;
  decision_ids: string[];
  relationships: CausalRelationship[];
  depth: number;
  generated_at: string;
}

export interface Intent {
  id: string;
  repository_id: string;
  name: string;
  description: string;
  supporting_decision_ids: string[];
  confidence: number;
  detected_at: string;
}

export interface DecisionSummary {
  repository_id: string;
  total_decisions: number;
  total_intents: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  generated_at: string;
}

export interface DecisionGraphNode {
  id: string;
  name: string;
  decision_type: DecisionType;
  status: DecisionStatus;
}

export interface DecisionGraphEdge {
  source: string;
  target: string;
  relationship_type: string;
  confidence: number;
}

export interface DecisionGraph {
  nodes: DecisionGraphNode[];
  edges: DecisionGraphEdge[];
}

// ============================================================
// REASONING
// ============================================================

export interface ReasoningQueryRequest {
  repository_id: string;
  commit_hash: string;
  query: string;
  capability_version?: string;
}

export interface ReasoningStep {
  step_index: number;
  step_type: string;
  description: string;
  inputs: string[];
  outputs?: string[];
}

export interface ReasoningChain {
  execution_id: string;
  total_steps: number;
  steps: ReasoningStep[];
}

export interface Hypothesis {
  hypothesis_id: string;
  statement: string;
  supporting_ids: string[];
  contradicting_ids: string[];
  confidence: number;
}

export interface Limitation {
  reason: string;
  affected_area: string;
  impact: string;
}

export interface Confidence {
  score: number;
  level: string;
  rationale: string;
}

export interface Evidence {
  source_id: string;
  source_type: string;
  description: string;
  weight: number;
}

export interface ReasoningResult {
  execution_id: string;
  question: string;
  answer: string;
  confidence: Confidence;
  chain: ReasoningChain;
  hypotheses: Hypothesis[];
  evidence: Evidence[];
  limitations: Limitation[];
  snapshot: Record<string, unknown>;
  generated_at: string;
}

export interface ReasoningHealth {
  status: string;
  reasoning_version: string;
  cache_size: number;
  registered_strategies: string[];
}

export interface CacheStatus {
  cache_size: number;
  message: string;
  total_entries?: number;
  oldest_entry?: string;
}

export interface CacheInvalidationResult {
  repository_id: string;
  entries_removed: number;
  message: string;
}

// ============================================================
// DIAGNOSTICS
// ============================================================

export interface HealthScore {
  health_score: number;
  reconstruction_score: number;
  integrity_score: number;
  confidence_score: number;
  measured_at: string;
}

export interface IntegrityViolation {
  id: string;
  repository_id: string;
  violation_type: string;
  severity: string;
  description: string;
  detected_at: string;
  affected_seids: string[];
}

export interface RepairAudit {
  id: string;
  repository_id: string;
  operator: string;
  issue_ids: string[];
  started_at: string;
  completed_at?: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  resolved_count?: number;
}

export interface RepairRequest {
  issue_ids: string[];
  operator?: string;
}

export interface BenchmarkReport {
  id: string;
  repository_id: string;
  commit_hash: string;
  scan_duration_ms: number;
  reconstruction_latency_ms: number;
  db_size_bytes: number;
  memory_rss_bytes: number;
  measured_at: string;
}

// ============================================================
// LOGIC ENGINE
// ============================================================

export interface LogicValidationIssue {
  issue_type: string;
  severity: string;
  description: string;
  target_id: string;
}

export interface LogicValidationReport {
  is_valid: boolean;
  issues: LogicValidationIssue[];
  validated_at: string;
}

export interface LogicSignature {
  id: string;
  repository_id: string;
  canonical_name: string;
  language: string;
  fingerprint: { structure_hash: string; dependency_hash: string; behavioral_hash: string; composite: string };
  first_seen_commit: string;
  last_seen_commit: string;
  occurrence_count: number;
}

export interface LogicVersion {
  id: string;
  logic_signature_id: string;
  code_entity_seid: string;
  commit_hash: string;
  state: Record<string, unknown>;
  detected_at: string;
}

export interface LogicTransition {
  id: string;
  from_logic_version_id?: string;
  to_logic_version_id: string;
  transition_type: string;
  rationale?: string;
  detected_at: string;
}

export interface BehaviorExplanation {
  id: string;
  logic_version_id: string;
  behavior_name: string;
  ontology_path: string;
  explanation: string;
  confidence: number;
}

export interface BehaviorDrift {
  id: string;
  logic_transition_id: string;
  from_logic_version_id: string;
  to_logic_version_id: string;
  drift_dimensions: {
    structural_drift: number;
    dependency_drift: number;
    api_surface_drift: number;
    control_flow_drift: number;
  };
  detected_at: string;
}

export interface BehaviorEvolutionGraph {
  versions: LogicVersion[];
  transitions: LogicTransition[];
}

export interface SignatureTimeline {
  signature: LogicSignature;
  versions: LogicVersion[];
  transitions: LogicTransition[];
  explanations: BehaviorExplanation[];
}

export interface RepositoryLogicTimeline {
  repository_id: string;
  signatures: SignatureTimeline[];
  generated_at: string;
}

// ============================================================
// META-ONTOLOGY (GOVERNANCE)
// ============================================================

export type MetaTypeStatus = "EXPERIMENTAL" | "ACTIVE" | "DEPRECATED" | (string & {});

export interface MetaType {
  id: string;
  name: string;
  category: string;
  status: MetaTypeStatus;
  description?: string;
  created_at: string;
  active_version?: string;
}

export interface MetaDefinition {
  id: string;
  type_id: string;
  major_version: number;
  minor_version: number;
  patch_version: number;
  schema_definition: Record<string, unknown>;
  semantic_signature?: Record<string, unknown>;
  registered_by: string;
  created_at: string;
}

export interface EmbeddingModel {
  id: string;
  model_name: string;
  provider: string;
  dimensions: number;
  is_active: boolean;
  created_at: string;
}

export interface EmbeddingVersion {
  id: string;
  model_id: string;
  version_string: string;
  configuration: Record<string, unknown>;
  created_at: string;
}

export interface RegisterTypeRequest {
  id: string;
  name: string;
  category: string;
  status?: MetaTypeStatus;
  description?: string;
}

export interface RegisterDefinitionRequest {
  schema_definition: Record<string, unknown>;
  semantic_signature?: Record<string, unknown>;
  version_string?: string;
  registered_by?: string;
}

export interface RegisterModelRequest {
  id: string;
  model_name: string;
  provider: string;
  dimensions: number;
}

export interface RegisterVersionRequest {
  version_string: string;
  configuration?: Record<string, unknown>;
}

export interface PromotionApprovalRequest {
  approver: string;
  rationale?: string;
}

export interface DiscoveredCandidate {
  meta_type: MetaType;
  definition: MetaDefinition;
  confidence: number;
  rationale: string;
}

export interface DiscoveryResponse {
  candidates: DiscoveredCandidate[];
  scan_duration_ms: number;
  repository_id?: string;
}

export interface EvolutionGraph {
  nodes: Array<{ id: string; type: string; label: string; metadata: Record<string, unknown> }>;
  edges: Array<{ from: string; to: string; relationship: string }>;
  generated_at: string;
}

export interface EvolutionDiff {
  added: Array<{ id: string; type: string; label: string }>;
  removed: Array<{ id: string; type: string; label: string }>;
  modified: Array<{ id: string; changes: Record<string, unknown> }>;
  from_version: string;
  to_version: string;
}
