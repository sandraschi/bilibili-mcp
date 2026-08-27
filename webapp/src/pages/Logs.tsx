import { type LogEntry, api } from "@/lib/api";
import { Terminal } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

export default function Logs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [level, setLevel] = useState("");

  const load = useCallback(async () => {
    try {
      const res = await api<{ logs: LogEntry[] }>(
        `/api/logs?limit=200${level ? `&level=${level}` : ""}`,
      );
      setLogs(res.logs);
    } catch {
      setLogs([]);
    }
  }, [level]);

  useEffect(() => {
    void load();
    const interval = setInterval(() => void load(), 5000);
    return () => clearInterval(interval);
  }, [load]);

  const color = (lvl: string) =>
    lvl === "ERROR" ? "text-red-400" : lvl === "WARNING" ? "text-amber-400" : "text-zinc-400";

  return (
    <div data-testid="logs-page" className="mx-auto max-w-5xl">
      <div className="flex items-center gap-3">
        <h2 className="flex items-center gap-2 text-xl font-bold">
          <Terminal className="h-5 w-5 text-red-400" /> Logs
        </h2>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="ml-auto rounded border border-zinc-700 bg-zinc-800 px-2 py-1 text-xs text-zinc-100"
        >
          <option value="">all levels</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
        </select>
      </div>
      <div
        className="mt-3 rounded-lg border border-zinc-800 bg-black/60 p-3 font-mono text-xs"
        data-testid="logs-list"
      >
        {logs.length === 0 && (
          <p className="text-zinc-500" data-testid="logs-empty">
            No log entries.
          </p>
        )}
        {logs.map((l, i) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: log rows have no stable unique id
          <div key={i} data-testid="log-entry" className="flex gap-2 py-0.5">
            <span className="shrink-0 text-zinc-500">{l.ts}</span>
            <span className={`w-16 shrink-0 ${color(l.level)}`}>{l.level}</span>
            <span className="shrink-0 text-zinc-500">{l.source}</span>
            <span className="break-all text-zinc-300">{l.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
