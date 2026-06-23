import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import { repositoriesApi } from "@/services/api/endpoints";

export function useRepositories() {
  return useQuery({
    queryKey: queryKeys.repositories.all(),
    queryFn: repositoriesApi.list,
    staleTime: CACHE.REPOSITORIES,
    refetchOnWindowFocus: false,
  });
}

export function useRepository(id: string | null) {
  return useQuery({
    queryKey: queryKeys.repositories.detail(id ?? ""),
    queryFn: () => repositoriesApi.get(id!),
    enabled: !!id,
    staleTime: CACHE.REPOSITORIES,
    refetchOnWindowFocus: false,
  });
}
