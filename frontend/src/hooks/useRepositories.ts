import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { CACHE } from "@/lib/constants";
import { repositoriesApi } from "@/services/api/endpoints";
import type { Repository } from "@/types/platform";

export function useRepositories() {
  return useQuery<Repository[], Error>({
    queryKey: queryKeys.repositories.all(),
    queryFn: repositoriesApi.list,
    staleTime: CACHE.REPOSITORIES,
    refetchOnWindowFocus: false,
  }) as UseQueryResult<Repository[], Error>;
}

export function useRepository(id: string | null) {
  return useQuery<Repository, Error>({
    queryKey: queryKeys.repositories.detail(id ?? ""),
    queryFn: () => repositoriesApi.get(id!),
    enabled: !!id,
    staleTime: CACHE.REPOSITORIES,
    refetchOnWindowFocus: false,
  }) as UseQueryResult<Repository, Error>;
}




