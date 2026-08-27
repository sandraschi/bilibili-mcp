import {
  type Comment,
  type CommentsResponse,
  type TranscriptResponse,
  type VideoInfo,
  type VideoInfoResponse,
  api,
} from "@/lib/api";
import { Clapperboard, MessageSquare, Play, Subtitles } from "lucide-react";
import { useState } from "react";

function fmt(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

function fmtTime(ts: number): string {
  if (!ts) return "-";
  return new Date(ts * 1000).toLocaleDateString();
}

export default function Video() {
  const [bvid, setBvid] = useState("");
  const [info, setInfo] = useState<VideoInfo | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    const id = bvid.trim();
    if (!id) return;
    setLoading(true);
    setError("");
    setInfo(null);
    setComments([]);
    setTranscript("");
    try {
      const [i, c, t] = await Promise.all([
        api<VideoInfoResponse>(`/api/video/info?bvid=${encodeURIComponent(id)}`),
        api<CommentsResponse>(`/api/video/comments?bvid=${encodeURIComponent(id)}&limit=10`),
        api<TranscriptResponse>(`/api/video/transcript?bvid=${encodeURIComponent(id)}`),
      ]);
      if (i.success) setInfo(i.data);
      else if (i.error) setError(i.error);
      if (c.success) setComments(c.data.comments);
      if (t.success) setTranscript(t.data.text);
      else if (t.error) setError((e) => `${e ? `${e} | ` : ""}${t.error}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "failed to load video");
    } finally {
      setLoading(false);
    }
  };

  const infoStats = info?.stats;

  return (
    <div data-testid="video-page" className="mx-auto max-w-5xl">
      <h2 className="text-xl font-bold">Video intel</h2>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <input
          value={bvid}
          onChange={(e) => setBvid(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void load()}
          data-testid="video-input"
          placeholder="BV... or https://www.bilibili.com/video/BV..."
          className="w-96 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500"
        />
        <button
          type="button"
          onClick={() => void load()}
          data-testid="video-submit"
          className="flex items-center gap-1.5 rounded-lg bg-red-500 px-4 py-1.5 text-sm font-semibold text-white hover:bg-red-400"
        >
          <Clapperboard className="h-4 w-4" /> Inspect
        </button>
      </div>

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {loading && <p className="mt-3 text-sm text-zinc-500">Fetching video data...</p>}

      {info && (
        <section
          data-testid="video-info"
          className="mt-5 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4"
        >
          <div className="flex flex-wrap items-start gap-3">
            {info.pic && (
              <img src={info.pic} alt={info.title} className="h-24 w-40 rounded object-cover" />
            )}
            <div className="min-w-0 flex-1">
              <a
                href={info.url}
                target="_blank"
                rel="noreferrer"
                className="text-base font-semibold text-red-400 hover:underline"
              >
                {info.title}
              </a>
              <p className="mt-1 text-xs text-zinc-400">
                {info.owner.name} · {info.tname} · {info.bvid} · published {fmtTime(info.pubdate)}
              </p>
              {infoStats && (
                <div className="mt-2 flex flex-wrap gap-3 text-xs text-zinc-400">
                  <span className="flex items-center gap-1">
                    <Play className="h-3 w-3" /> {fmt(infoStats.view)} views
                  </span>
                  <span>❤ {fmt(infoStats.like)}</span>
                  <span>💬 {fmt(infoStats.reply)}</span>
                  <span>★ {fmt(infoStats.favorite)}</span>
                  <span>◎ {fmt(infoStats.coin)}</span>
                  <span>↗ {fmt(infoStats.share)}</span>
                </div>
              )}
            </div>
          </div>
          {info.desc && <p className="mt-3 text-sm text-zinc-300">{info.desc}</p>}
        </section>
      )}

      <section data-testid="video-transcript" className="mt-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
          <Subtitles className="h-4 w-4" /> Transcript
        </h3>
        {transcript ? (
          <div className="mt-2 max-h-80 overflow-y-auto whitespace-pre-wrap rounded-lg border border-zinc-800 bg-black/50 p-3 text-sm leading-relaxed text-zinc-200">
            {transcript}
          </div>
        ) : (
          <p className="mt-2 text-sm text-zinc-500">
            {loading
              ? "Loading transcript..."
              : "No transcript loaded. Some videos gate subtitles behind login."}
          </p>
        )}
      </section>

      <section data-testid="video-comments" className="mt-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
          <MessageSquare className="h-4 w-4" /> Hot comments
        </h3>
        <div className="mt-2 space-y-2">
          {comments.map((c) => (
            <div
              key={c.rpid}
              data-testid="comment"
              className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3"
            >
              <div className="flex items-center gap-2 text-xs text-zinc-500">
                <span className="font-semibold text-zinc-300">{c.author}</span>
                <span className="ml-auto">{fmtTime(c.time)}</span>
                <span>❤ {fmt(c.likes)}</span>
              </div>
              <p className="mt-1 text-sm text-zinc-300">{c.text}</p>
            </div>
          ))}
          {!loading && comments.length === 0 && (
            <p className="text-sm text-zinc-500">No comments loaded.</p>
          )}
        </div>
      </section>
    </div>
  );
}
