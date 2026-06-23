import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import { capabilitiesApi } from "@/services/api/endpoints";
import type { CapabilityFilters } from "@/types/platform";

export function useCapabilities(repositoryId: string | null, filters?: CapabilityFilters) {
  return useQuery({
    queryKey: queryKeys.capabilities.byRepoWithParams(repositoryId ?? "", filters),
    queryFn: () => capabilitiesApi.listByRepository(repositoryId!, filters),
    enabled: !!repositoryId,
    staleTime: CACHE.CAPABILITIES,
    refetchOnWindowFocus: "stale",
  });
}

export function useCapability(capabilityId: string | null) {
  return useQuery({
    queryKey: queryKeys.capabilities.detail(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.get(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_DETAIL,
  });
}

export function useCapabilityHealth(capabilityId: string | null) {
  return useQuery({
    queryKey: queryKeys.capabilities.health(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getHealthRisk(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_HEALTH,
  });
}

export function useCapabilityBlastRadius(capabilityId: string | null) {
  return useQuery({
    queryKey: queryKeys.capabilities.blastRadius(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getBlastRadius(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_TIMELINE,
  });
}

export function useCapabilityTimeline(capabilityId: string | null) {
  return useQuery({
    queryKey: queryKeys.capabilities.timeline(capabilityId ?? ""),
    queryFn: () => capabilitiesApi.getTimeline(capabilityId!),
    enabled: !!capabilityId,
    staleTime: CACHE.CAPABILITY_TIMELINE,
  });
}

export function useCapabilityCandidates(repositoryId: string | null) {
  return useQuery({
    queryKey: queryKeys.capabilities.candidates(repositoryId ?? ""),
    queryFn: () => capabilitiesApi.listCandidates(repositoryId!),
    enabled: !!repositoryId,
    staleTime: CACHE.CAPABILITIES,
  });
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
