import { api } from "@/lib/api";
import { Wrench } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

export default function Tools() {
  const [tools, setTools] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api<{ tools: string[] }>("/api/tools");
      setTools(res.tools);
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to load tools");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div data-testid="tools-page" className="mx-auto max-w-4xl">
      <div className="flex items-center gap-2">
        <h2 className="flex items-center gap-2 text-xl font-bold">
          <Wrench className="h-5 w-5 text-red-400" /> MCP tools
        </h2>
        <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
          {tools.length} registered
        </span>
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      {loading && <p className="mt-4 text-sm text-zinc-500">Loading tools...</p>}
      <div data-testid="tools-list" className="mt-4 grid gap-2 md:grid-cols-2">
        {tools.map((t) => (
          <div
            key={t}
            data-testid="tool-entry"
            className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 font-mono text-sm text-zinc-200"
          >
            {t}
          </div>
        ))}
        {!loading && tools.length === 0 && (
          <p className="text-sm text-zinc-500">No tools reported.</p>
        )}
      </div>
    </div>
  );
}
