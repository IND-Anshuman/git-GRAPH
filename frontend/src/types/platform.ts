/**
 * TypeScript types for the Software Intelligence Platform.
 * All types mirror actual FastAPI backend schemas.
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
  429: "RATE_LIMITED",
  500: "INTERNAL_ERROR",
  502: "BAD_GATEWAY",
  503: "SERVICE_UNAVAILABLE",
  504: "GATEWAY_TIMEOUT",
};

// ============================================================
// PLATFORM / GRAPH TYPES (Future-ready)
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
