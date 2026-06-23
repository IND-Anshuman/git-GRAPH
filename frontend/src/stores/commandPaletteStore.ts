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
      partialize: (s) => ({ recentCommands: s.recentCommands }),
    }
  )
);
