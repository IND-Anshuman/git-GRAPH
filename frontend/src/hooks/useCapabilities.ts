import { useQuery, useMutation, useQueryClient, type UseQueryResult } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import { capabilitiesApi } from "@/services/api/endpoints";
import type { CapabilityFilters, Capability, CapabilityHealthRisk, CapabilityBlastRadius, CapabilityTimeline, CapabilityCandidate } from "@/types/platform";

export function useCapabilities(
  repositoryId: string | null,
  filters?: CapabilityFilters
) {
  return useQuery<Capability[], Error>({
    queryKey: queryKeys.capabilities.byRepoWithParams(repositoryId ?? "", filters as Record<string, unknown>),
    queryFn: () => capabilitiesApi.listByRepository(repositoryId!, filters),
    enabled: !!repositoryId,
    staleTime: CACHE.CAPABILITIES,
  }) as UseQueryResult<Capability[], Error>;
}

export function useCapability(capabilityId: string | null) {
  return useQuery<Capability, Error>({
    queryKey: queryKeys.capabilities.detail(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.get(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_DETAIL,
  }) as UseQueryResult<Capability, Error>;
}

export function useCapabilityHealth(capabilityId: string | null) {
  return useQuery<CapabilityHealthRisk, Error>({
    queryKey: queryKeys.capabilities.health(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getHealthRisk(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_HEALTH,
  }) as UseQueryResult<CapabilityHealthRisk, Error>;
}

export function useCapabilityBlastRadius(capabilityId: string | null) {
  return useQuery<CapabilityBlastRadius, Error>({
    queryKey: queryKeys.capabilities.blastRadius(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getBlastRadius(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_TIMELINE,
  }) as UseQueryResult<CapabilityBlastRadius, Error>;
}

export function useCapabilityTimeline(capabilityId: string | null) {
  return useQuery<CapabilityTimeline, Error>({
    queryKey: queryKeys.capabilities.timeline(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getTimeline(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_TIMELINE,
  }) as UseQueryResult<CapabilityTimeline, Error>;
}

export function useCapabilityCandidates(repositoryId: string | null) {
  return useQuery<CapabilityCandidate[], Error>({
    queryKey: queryKeys.capabilities.candidates(repositoryId ?? ""),
    queryFn: () => capabilitiesApi.listCandidates(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.CAPABILITIES,
  }) as UseQueryResult<CapabilityCandidate[], Error>;
}





export function useApproveCapability() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (candidateId: string) => capabilitiesApi.approve(candidateId),
    onSuccess: (_, candidateId) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.capabilities.all() });
    },
  });
}

export function useDiscoverCapabilities() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (repositoryId: string) => capabilitiesApi.discover(repositoryId),
    onSuccess: (_, repositoryId) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.capabilities.candidates(repositoryId),
      });
    },
  });
}
