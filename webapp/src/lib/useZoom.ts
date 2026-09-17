import { useCallback, useEffect, useState } from "react";

// Fleet standard zoom hook: Tauri windows have no native browser zoom, so
// without this the app is unusable at high-DPI or for anyone wanting larger
// text. Ctrl+Scroll cycles levels, Ctrl+0 resets, persisted to localStorage.
const ZOOM_LEVELS = [0.5, 0.6, 0.7, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0];
const DEFAULT_ZOOM = 1.0;
const STORAGE_KEY = "tauri-zoom";

function readStoredZoom(): number {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? Number.parseFloat(raw) : DEFAULT_ZOOM;
    return ZOOM_LEVELS.includes(parsed) ? parsed : DEFAULT_ZOOM;
  } catch {
    return DEFAULT_ZOOM;
  }
}

function applyZoom(level: number) {
  // In a real Tauri webview, window.zoomLevel-style APIs aren't available;
  // CSS zoom on the root element is the reliable cross-context fallback and
  // also works when the app is opened in a plain dev browser.
  document.documentElement.style.zoom = String(level);
}

export function useZoom() {
  const [zoom, setZoom] = useState<number>(() => readStoredZoom());

  useEffect(() => {
    applyZoom(zoom);
    try {
      window.localStorage.setItem(STORAGE_KEY, String(zoom));
    } catch {
      // localStorage unavailable (private mode, etc.) - zoom still applies for this session.
    }
  }, [zoom]);

  const cycleZoom = useCallback((direction: 1 | -1) => {
    setZoom((current) => {
      const idx = ZOOM_LEVELS.indexOf(current);
      const nextIdx = Math.min(Math.max(idx + direction, 0), ZOOM_LEVELS.length - 1);
      return ZOOM_LEVELS[nextIdx];
    });
  }, []);

  const resetZoom = useCallback(() => setZoom(DEFAULT_ZOOM), []);

  useEffect(() => {
    function onWheel(e: WheelEvent) {
      if (!e.ctrlKey) return;
      e.preventDefault();
      cycleZoom(e.deltaY < 0 ? 1 : -1);
    }
    function onKeyDown(e: KeyboardEvent) {
      if (!e.ctrlKey) return;
      if (e.key === "0") {
        e.preventDefault();
        resetZoom();
      } else if (e.key === "=" || e.key === "+") {
        e.preventDefault();
        cycleZoom(1);
      } else if (e.key === "-") {
        e.preventDefault();
        cycleZoom(-1);
      }
    }
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [cycleZoom, resetZoom]);

  return { zoom, zoomPercent: Math.round(zoom * 100) };
}
