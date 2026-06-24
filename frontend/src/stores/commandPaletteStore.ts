import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { COMMAND_PALETTE_RECENT_MAX } from "@/lib/constants";

export interface CommandRecord {
  id: string;
  label: string;
  executionCount: number;
  lastExecuted: number; // timestamp
}

interface CommandPaletteState {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;

  isSearchOpen: boolean;
  openSearch: () => void;
  closeSearch: () => void;
  toggleSearch: () => void;

  recentCommands: CommandRecord[];
  recordCommandExecution: (id: string, label: string) => void;
  clearHistory: () => void;
}

export const useCommandPaletteStore = create<CommandPaletteState>()(
  persist(
    (set) => ({
      isOpen: false,
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      toggle: () => set((s) => ({ isOpen: !s.isOpen })),

      isSearchOpen: false,
      openSearch: () => set({ isSearchOpen: true, isOpen: false }), // close palette when search opens
      closeSearch: () => set({ isSearchOpen: false }),
      toggleSearch: () => set((s) => ({ isSearchOpen: !s.isSearchOpen, isOpen: false })),

      recentCommands: [],

      recordCommandExecution: (id, label) =>
        set((s) => {
          const existing = s.recentCommands.find((c) => c.id === id);
          let next: CommandRecord[];

          if (existing) {
            next = s.recentCommands.map((c) =>
              c.id === id
                ? { ...c, executionCount: c.executionCount + 1, lastExecuted: Date.now() }
                : c
            );
          } else {
            next = [
              { id, label, executionCount: 1, lastExecuted: Date.now() },
              ...s.recentCommands,
            ].slice(0, COMMAND_PALETTE_RECENT_MAX);
          }

          return { recentCommands: next };
        }),

      clearHistory: () => set({ recentCommands: [] }),
    }),
    {
      name: "sip-command-palette-store",
      storage: createJSONStorage(() => {
        try { return localStorage; } catch { return sessionStorage; }
      }),
      // Only persist recentCommands
      partialize: (s) => ({ recentCommands: s.recentCommands }),
    }
  )
);

