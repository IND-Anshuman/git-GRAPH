import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { RECENT_SEARCHES_MAX } from "@/lib/constants";

export interface RecentSearch {
  query: string;
  timestamp: number;
  resultCount: number;
}

interface SearchState {
  recentSearches: RecentSearch[];
  addRecentSearch: (query: string, resultCount?: number) => void;
  clearRecentSearches: () => void;
  removeRecentSearch: (query: string) => void;
}

export const useSearchStore = create<SearchState>()(
  persist(
    (set) => ({
      recentSearches: [],

      addRecentSearch: (query, resultCount = 0) =>
        set((s) => {
          // Dedup by query text (replace old entry)
          const filtered = s.recentSearches.filter(
            (r) => r.query.toLowerCase() !== query.toLowerCase()
          );
          const next: RecentSearch = { query, timestamp: Date.now(), resultCount };
          return {
            recentSearches: [next, ...filtered].slice(0, RECENT_SEARCHES_MAX),
          };
        }),

      clearRecentSearches: () => set({ recentSearches: [] }),

      removeRecentSearch: (query) =>
        set((s) => ({
          recentSearches: s.recentSearches.filter((r) => r.query !== query),
        })),
    }),
    {
      name: "sip-search-store",
      storage: createJSONStorage(() => {
        try { return localStorage; } catch { return sessionStorage; }
      }),
    }
  )
);
