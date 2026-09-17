import { API_BASE, type Health } from "@/lib/api";
import { useZoom } from "@/lib/useZoom";
import {
  Activity,
  ChevronLeft,
  ChevronRight,
  Clapperboard,
  HelpCircle,
  Inbox,
  LayoutDashboard,
  Logs as LogsIcon,
  MessageSquare,
  Search,
  Settings,
  Sparkles,
  TrendingUp,
  Wrench,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/explore", label: "Explore", icon: TrendingUp },
  { to: "/search", label: "Search", icon: Search },
  { to: "/video", label: "Video", icon: Clapperboard },
  { to: "/tools", label: "Tools", icon: Wrench },
  { to: "/skills", label: "Skills", icon: Sparkles },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/inbox", label: "Inbox", icon: Inbox },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/logs", label: "Logs", icon: LogsIcon },
  { to: "/help", label: "Help", icon: HelpCircle },
];

async function checkHealth(): Promise<Health | null> {
  try {
    const r = await fetch(`${API_BASE}/api/health`);
    if (!r.ok) return null;
    return (await r.json()) as Health;
  } catch {
    return null;
  }
}

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const [backend, setBackend] = useState<Health | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [tier, setTier] = useState("anonymous");
  const location = useLocation();
  const { zoomPercent } = useZoom();

  const refresh = useCallback(async () => {
    const h = await checkHealth();
    setBackend(h);
    setBackendOk(!!h);
    if (h) setTier(h.tier);
  }, []);

  useEffect(() => {
    void refresh();
    const interval = setInterval(refresh, 15000);

    // Tauri desktop shell emits "backend-status" when the embedded backend
    // process changes state; fall back to HTTP polling above when not
    // running inside Tauri (e.g. plain browser dev mode).
    let unlisten: (() => void) | undefined;
    void (async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event");
        unlisten = await listen("backend-status", () => void refresh());
      } catch {
        // Not running inside the Tauri webview - HTTP polling covers it.
      }
    })();

    return () => {
      clearInterval(interval);
      unlisten?.();
    };
  }, [refresh]);

  const pageTitle =
    NAV.find((n) => (n.to === "/" ? location.pathname === "/" : location.pathname.startsWith(n.to)))
      ?.label ?? "Bilibili MCP";

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <aside
        data-testid="sidebar"
        className={`flex flex-col border-r border-zinc-800 bg-zinc-900/60 backdrop-blur transition-all ${
          collapsed ? "w-16" : "w-56"
        }`}
      >
        <div className="flex items-center gap-2 px-4 py-4">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded bg-red-600 font-bold text-white">
            B
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold">Bilibili MCP</div>
              <div className="text-[10px] text-zinc-500">v0.1.0</div>
            </div>
          )}
        </div>
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          data-testid="sidebar-toggle"
          className="mx-2 mb-2 flex items-center justify-center gap-1 rounded border border-zinc-800 py-1.5 text-zinc-400 hover:text-white"
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
        <nav className="flex-1 space-y-1 px-2">
          {NAV.map((item) => {
            const active =
              item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to);
            return (
              <NavLink
                key={item.to}
                to={item.to}
                aria-label={item.label}
                data-testid={`nav-${item.label.toLowerCase().replace(" ", "-")}`}
                className={`flex items-center gap-2 rounded px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-red-500/15 text-red-400"
                    : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
                }`}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>
        <div className="border-t border-zinc-800 p-3">
          <div className="flex items-center gap-2">
            <span
              data-testid="backend-dot"
              className={`h-2.5 w-2.5 rounded-full ${
                backendOk === null ? "bg-zinc-500" : backendOk ? "bg-green-500" : "bg-red-500"
              } animate-pulse`}
            />
            <span className="text-sm text-zinc-300">
              {backendOk === null ? "Connecting..." : backendOk ? "Connected" : "Offline"}
            </span>
          </div>
          <div className="mt-1 text-xs uppercase tracking-wide text-zinc-500">
            tier: <span className="text-red-400">{tier}</span>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/40 px-5 py-3">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-red-400" />
            <h1 className="text-sm font-semibold">{pageTitle}</h1>
          </div>
          <div className="flex items-center gap-3 text-sm text-zinc-300">
            {backend && (
              <>
                <span>{backend.version}</span>
                <span>{backend.tool_count} tools</span>
                <span className="rounded bg-zinc-800 px-2 py-0.5">{backend.tier}</span>
              </>
            )}
            <span
              data-testid="zoom-indicator"
              title="Ctrl+Scroll to zoom, Ctrl+0 to reset"
              className="rounded bg-zinc-800 px-2 py-0.5 text-zinc-500"
            >
              {zoomPercent}%
            </span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-5">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
