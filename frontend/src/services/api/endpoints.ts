import { apiClient } from "./client";
import type {
  Repository,
  Capability,
  CapabilityCandidate,
  CapabilityHealthRisk,
  CapabilityBlastRadius,
  CapabilityTimeline,
  CapabilityQueryRequest,
  CapabilityQueryResponse,
  Concept,
} from "@/types/platform";

// ============================================================
// REPOSITORIES
// ============================================================

export const repositoriesApi = {
  list: async (): Promise<Repository[]> => {
    const res = await apiClient.get<Repository[]>("/repositories");
    return res.data;
  },

  get: async (id: string): Promise<Repository> => {
    const res = await apiClient.get<Repository>(`/repositories/${id}`);
    return res.data;
  },
};

// ============================================================
// CAPABILITIES
// ============================================================

export const capabilitiesApi = {
  listByRepository: async (
    repositoryId: string,
    params?: { limit?: number; offset?: number }
  ): Promise<Capability[]> => {
    const res = await apiClient.get<Capability[]>(
      `/repositories/${repositoryId}/capabilities`,
      { params }
    );
    return res.data;
  },

  listCandidates: async (repositoryId: string): Promise<CapabilityCandidate[]> => {
    const res = await apiClient.get<CapabilityCandidate[]>(
      `/repositories/${repositoryId}/capabilities/candidates`
    );
    return res.data;
  },

  get: async (capabilityId: string): Promise<Capability> => {
    const res = await apiClient.get<Capability>(`/capabilities/${capabilityId}`);
    return res.data;
  },

  getHealthRisk: async (capabilityId: string): Promise<CapabilityHealthRisk> => {
    const res = await apiClient.get<CapabilityHealthRisk>(
      `/capabilities/${capabilityId}/health-risk`
    );
    return res.data;
  },

  getBlastRadius: async (capabilityId: string): Promise<CapabilityBlastRadius> => {
    const res = await apiClient.get<CapabilityBlastRadius>(
      `/capabilities/${capabilityId}/blast-radius`
    );
    return res.data;
  },

  getTimeline: async (capabilityId: string): Promise<CapabilityTimeline> => {
    const res = await apiClient.get<CapabilityTimeline>(
      `/capabilities/${capabilityId}/timeline`
    );
    return res.data;
  },

  query: async (
    repositoryId: string,
    request: CapabilityQueryRequest
  ): Promise<CapabilityQueryResponse> => {
    const res = await apiClient.post<CapabilityQueryResponse>(
      `/repositories/${repositoryId}/capabilities/query`,
      request
    );
    return res.data;
  },

  approve: async (candidateId: string): Promise<Capability> => {
    const res = await apiClient.post<Capability>(`/capabilities/${candidateId}/approve`);
    return res.data;
  },

  reject: async (candidateId: string): Promise<void> => {
    await apiClient.post(`/capabilities/${candidateId}/reject`);
  },

  discover: async (repositoryId: string): Promise<CapabilityCandidate[]> => {
    const res = await apiClient.post<CapabilityCandidate[]>(
      `/repositories/${repositoryId}/capabilities/discover`
    );
    return res.data;
  },
};

// ============================================================
// CONCEPTS
// ============================================================

export const conceptsApi = {
  listByRepository: async (
    repositoryId: string,
    commitHash?: string
  ): Promise<Concept[]> => {
    try {
      const res = await apiClient.get<Concept[]>(
        `/repositories/${repositoryId}/concepts`,
        commitHash ? { params: { commit_hash: commitHash } } : undefined
      );
      return res.data;
    } catch {
      return []; // concepts may not be extracted yet
    }
  },
};

// ============================================================
// REASONING (Future stub — Stage 3)
// ============================================================

export const reasoningApi = {
  // Reserved for Stage 3 integration
};

// ============================================================
// ARCHITECTURE (Future stub — Stage 2)
// ============================================================

export const architectureApi = {
  // Reserved for Stage 2 integration
};

// ============================================================
// DECISIONS (Future stub — Stage 2)
// ============================================================

export const decisionsApi = {
  // Reserved for Stage 2 integration
};
