import { type ExploreResponse, type HotSearchResponse, type SlimVideo, api } from "@/lib/api";
import { Flame, Play, RefreshCw, Trophy } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

interface HotItem {
  keyword: string;
  heat: number | string;
}

function fmt(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

export default function Explore() {
  const [trending, setTrending] = useState<SlimVideo[]>([]);
  const [rank, setRank] = useState<SlimVideo[]>([]);
  const [hot, setHot] = useState<HotItem[]>([]);
  const [limit, setLimit] = useState(12);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [t, r, h] = await Promise.all([
        api<ExploreResponse>(`/api/explore/trending?limit=${limit}`),
        api<ExploreResponse>(`/api/explore/rank?rid=0&limit=${limit}`),
        api<HotSearchResponse>("/api/explore/hot_search?limit=10"),
      ]);
      setTrending(t.success ? t.data : []);
      setRank(r.success ? r.data : []);
      setHot(h.success ? (h.data as HotItem[]) : []);
      if (!t.success) setError(t.error || "trending failed");
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to load explore data");
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div data-testid="explore-page" className="mx-auto max-w-6xl">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-xl font-bold">Explore Bilibili</h2>
        <select
          data-testid="limit-select"
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="rounded border border-zinc-700 bg-zinc-800 px-2 py-1 text-sm text-zinc-100"
        >
          {[6, 12, 20].map((n) => (
            <option key={n} value={n}>
              {n} per list
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => void load()}
          data-testid="explore-refresh"
          className="ml-auto flex items-center gap-1.5 rounded border border-zinc-700 px-3 py-1 text-sm text-zinc-300 hover:border-red-500 hover:text-red-400"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
      </div>

      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      {loading && <p className="mt-4 text-sm text-zinc-400">Fetching live Bilibili data...</p>}

      <section data-testid="trending-section" className="mt-6">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
          <Flame className="h-4 w-4" /> Popular feed
        </h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {trending.map((v) => (
            <VideoCard key={v.bvid} v={v} />
          ))}
        </div>
        {!loading && trending.length === 0 && (
          <p className="text-sm text-zinc-400">No trending videos returned.</p>
        )}
      </section>

      <section data-testid="rank-section" className="mt-8">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
          <Trophy className="h-4 w-4" /> All-region daily ranking
        </h3>
        <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {rank.map((v) => (
            <VideoCard key={v.bvid} v={v} />
          ))}
        </div>
        {!loading && rank.length === 0 && (
          <p className="text-sm text-zinc-400">No ranking entries returned.</p>
        )}
      </section>

      <section data-testid="hot-search-section" className="mt-8">
        <h3 className="text-sm font-semibold text-red-400">Hot search keywords</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {hot.map((h, i) => (
            <span
              key={`${h.keyword}-${i}`}
              data-testid="hot-search-chip"
              className="rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1 text-sm text-zinc-300"
            >
              <span className="mr-1.5 text-red-400">#{i + 1}</span>
              {h.keyword}
              <span className="ml-1.5 text-xs text-zinc-400">{String(h.heat)}</span>
            </span>
          ))}
        </div>
        {!loading && hot.length === 0 && (
          <p className="text-sm text-zinc-400">No hot keywords returned.</p>
        )}
      </section>
    </div>
  );
}

function VideoCard({ v }: { v: SlimVideo }) {
  return (
    <a
      href={v.url}
      target="_blank"
      rel="noreferrer"
      data-testid="video-card"
      className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-red-500/50"
    >
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold text-red-400">{v.title || "(untitled)"}</span>
      </div>
      <p className="mt-1 line-clamp-2 text-xs text-zinc-400">{v.desc || "(no description)"}</p>
      <div className="mt-2 flex items-center gap-3 text-xs text-zinc-400">
        <span className="flex items-center gap-1">
          <Play className="h-3 w-3 text-red-500" /> {fmt(v.play)}
        </span>
        <span>{v.author}</span>
        <span className="ml-auto rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400">
          {v.bvid}
        </span>
      </div>
    </a>
  );
}
