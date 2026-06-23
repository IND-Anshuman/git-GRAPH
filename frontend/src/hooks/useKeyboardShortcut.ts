import { useEffect, useRef } from "react";

type KeyCombo = {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
};

/**
 * Listen for keyboard shortcuts globally.
 * Handles Ctrl+K, Cmd+K etc.
 */
export function useKeyboardShortcut(
  combo: KeyCombo,
  handler: (e: KeyboardEvent) => void,
  enabled = true
): void {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    if (!enabled) return;

    const listener = (e: KeyboardEvent) => {
      const matchKey = e.key.toLowerCase() === combo.key.toLowerCase();
      const matchCtrl = combo.ctrlKey ? e.ctrlKey || e.metaKey : true;
      const matchMeta = combo.metaKey ? e.metaKey || e.ctrlKey : true;
      const matchShift = combo.shiftKey ? e.shiftKey : !e.shiftKey;
      const matchAlt = combo.altKey ? e.altKey : !e.altKey;

      if (
        matchKey &&
        (combo.ctrlKey || combo.metaKey ? matchCtrl : true) &&
        matchShift &&
        matchAlt
      ) {
        e.preventDefault();
        handlerRef.current(e);
      }
    };

    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [combo.key, combo.ctrlKey, combo.metaKey, combo.shiftKey, combo.altKey, enabled]);
}
