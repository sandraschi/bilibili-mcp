import { type SearchResponse, type SlimVideo, type UserHit, api } from "@/lib/api";
import { KeyRound, Play, Search as SearchIcon, UserRound } from "lucide-react";
import { useState } from "react";

function fmt(n: number): string {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}w`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

export default function Search() {
  const [mode, setMode] = useState<"video" | "user">("video");
  const [query, setQuery] = useState("");
  const [videos, setVideos] = useState<SlimVideo[]>([]);
  const [users, setUsers] = useState<UserHit[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const run = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setMessage("");
    setVideos([]);
    setUsers([]);
    try {
      const res = await api<SearchResponse>(
        `/api/search?keyword=${encodeURIComponent(query)}&operation=${mode}&limit=15`,
      );
      if (!res.success) {
        setError(res.error || "search failed");
        return;
      }
      setMessage(res.message || "");
      if (mode === "video") setVideos(res.data as SlimVideo[]);
      else setUsers(res.data as UserHit[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="search-page" className="mx-auto max-w-5xl">
      <h2 className="text-xl font-bold">Search Bilibili</h2>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <div className="flex overflow-hidden rounded-lg border border-zinc-700">
          {(["video", "user"] as const).map((m) => (
            <button
              type="button"
              key={m}
              data-testid={`mode-${m}`}
              onClick={() => {
                setMode(m);
                setError("");
                setVideos([]);
                setUsers([]);
              }}
              className={`px-4 py-1.5 text-sm ${
                mode === m ? "bg-red-500 font-semibold text-white" : "bg-zinc-800 text-zinc-300"
              }`}
            >
              {m}
            </button>
          ))}
        </div>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void run()}
          data-testid="search-input"
          placeholder={mode === "video" ? "video title keyword..." : "creator name..."}
          className="w-72 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500"
        />
        <button
          type="button"
          onClick={() => void run()}
          data-testid="search-submit"
          className="flex items-center gap-1.5 rounded-lg bg-red-500 px-4 py-1.5 text-sm font-semibold text-white hover:bg-red-400"
        >
          <SearchIcon className="h-4 w-4" /> Search
        </button>
      </div>

      <div className="mt-3 flex items-start gap-2 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 text-xs text-zinc-400">
        <KeyRound className="mt-0.5 h-3.5 w-3.5 shrink-0 text-red-400" />
        <span>
          Anonymous search can hit Bilibili risk control. If you get an error, retry after a delay
          or set a login cookie (BILIBILI_COOKIE) for the account tier.
        </span>
      </div>

      {message && <p className="mt-3 text-xs text-zinc-400">{message}</p>}
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {loading && <p className="mt-3 text-sm text-zinc-400">Searching Bilibili...</p>}

      <div data-testid="search-results" className="mt-4 space-y-2">
        {videos.map((v) => (
          <a
            key={v.bvid}
            href={v.url}
            target="_blank"
            rel="noreferrer"
            data-testid="result-video"
            className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 hover:border-red-500/50"
          >
            <div className="flex items-center gap-2 text-sm">
              <span className="font-semibold text-red-400">{v.title || "(untitled)"}</span>
              <span className="ml-auto flex items-center gap-1 text-xs text-zinc-400">
                <Play className="h-3 w-3" /> {fmt(v.play)}
              </span>
            </div>
            <p className="mt-1 truncate text-xs text-zinc-400">
              {v.author} · {v.bvid}
            </p>
          </a>
        ))}
        {users.map((u) => (
          <a
            key={u.mid}
            href={u.url}
            target="_blank"
            rel="noreferrer"
            data-testid="result-user"
            className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 hover:border-red-500/50"
          >
            <div className="flex items-center gap-2 text-sm">
              <UserRound className="h-4 w-4 text-red-400" />
              <span className="font-semibold text-red-400">{u.name}</span>
              <span className="ml-auto flex items-center gap-3 text-xs text-zinc-400">
                <span>{fmt(u.fans)} fans</span>
                <span>{u.videos} videos</span>
              </span>
            </div>
            {u.sign && <p className="mt-1 truncate text-xs text-zinc-400">{u.sign}</p>}
          </a>
        ))}
        {!loading && !error && videos.length === 0 && users.length === 0 && (
          <p className="text-sm text-zinc-400">No results yet - search above.</p>
        )}
      </div>
    </div>
  );
}
