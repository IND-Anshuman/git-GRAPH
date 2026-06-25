/**
 * UI Store — transient UI state (sidebar, selections, active tab)
 * Uses persist middleware for sidebar + theme preferences.
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { DetailTabId } from "@/lib/constants";

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  // Selected capability
  selectedCapabilityId: string | null;
  setSelectedCapabilityId: (id: string | null) => void;

  // Active detail tab
  activeDetailTab: DetailTabId;
  setActiveDetailTab: (tab: DetailTabId) => void;

  // Active repository
  activeRepositoryId: string | null;
  setActiveRepositoryId: (id: string | null) => void;

  // Expanded categories in navigator
  expandedCategories: Set<string>;
  toggleCategory: (category: string) => void;
  expandCategory: (category: string) => void;

  // Reduced motion (accessibility)
  reducedMotion: boolean;
  setReducedMotion: (val: boolean) => void;

  // Filter panel open state
  filterPanelOpen: boolean;
  setFilterPanelOpen: (open: boolean) => void;
  toggleFilterPanel: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

      selectedCapabilityId: null,
      setSelectedCapabilityId: (id) => set({ selectedCapabilityId: id }),

      activeDetailTab: "overview",
      setActiveDetailTab: (tab) => set({ activeDetailTab: tab }),

      activeRepositoryId: null,
      setActiveRepositoryId: (id) => set({ activeRepositoryId: id }),

      expandedCategories: new Set<string>(),
      toggleCategory: (category) =>
        set((s) => {
          const next = new Set(s.expandedCategories);
          if (next.has(category)) next.delete(category);
          else next.add(category);
          return { expandedCategories: next };
        }),
      expandCategory: (category) =>
        set((s) => ({
          expandedCategories: new Set([...s.expandedCategories, category]),
        })),

      reducedMotion: false,
      setReducedMotion: (val) => set({ reducedMotion: val }),

      filterPanelOpen: false,
      setFilterPanelOpen: (open) => set({ filterPanelOpen: open }),
      toggleFilterPanel: () => set((s) => ({ filterPanelOpen: !s.filterPanelOpen })),
    }),
    {
      name: "sip-ui-store",
      storage: createJSONStorage(() => {
        // Graceful localStorage degradation (Requirement 14.6)
        if (typeof window !== "undefined") {
          try {
            return localStorage;
          } catch {
            console.warn("[UIStore] localStorage unavailable — session state not persisted");
            return sessionStorage;
          }
        }
        return {
          getItem: () => null,
          setItem: () => {},
          removeItem: () => {},
        };
      }),
      // Only persist these fields — the rest are session-only
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        activeDetailTab: state.activeDetailTab,
        reducedMotion: state.reducedMotion,
        activeRepositoryId: state.activeRepositoryId,
      }),
    }
  )
);
