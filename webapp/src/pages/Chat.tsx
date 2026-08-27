import { API_BASE, type SummaryResult } from "@/lib/api";
import { useLlmStore } from "@/store/llm";
import { FileText, Send } from "lucide-react";
import { useEffect, useState } from "react";

export default function Chat() {
  const [bvid, setBvid] = useState("");
  const [summary, setSummary] = useState("");
  const [transcriptWords, setTranscriptWords] = useState<number | null>(null);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState("");
  const probe = useLlmStore((s) => s.probe);
  const providers = useLlmStore((s) => s.providers);

  useEffect(() => {
    void probe();
  }, [probe]);

  const summarize = async () => {
    const id = bvid.trim();
    if (!id || thinking) return;
    setThinking(true);
    setError("");
    setSummary("");
    setTranscriptWords(null);
    try {
      const r = await fetch(`${API_BASE}/api/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bvid: id }),
      });
      const body = (await r.json()) as SummaryResult;
      if (!body.success) throw new Error(body.error || "summarize failed");
      setSummary(body.summary);
      setTranscriptWords(body.transcript_word_count);
    } catch (e) {
      setError(e instanceof Error ? e.message : "summarize failed");
    } finally {
      setThinking(false);
    }
  };

  const llmUp = providers.some((p) => p.status === "detected");

  return (
    <div data-testid="chat-page" className="mx-auto max-w-4xl">
      <h2 className="text-xl font-bold">Summarize a video</h2>
      <p className="mt-1 text-xs text-zinc-500">
        Give a BV id or URL and the server fetches its AI transcript and summarises it with a local
        LLM.
      </p>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <input
          value={bvid}
          onChange={(e) => setBvid(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void summarize()}
          data-testid="chat-bvid"
          placeholder="BV... or full bilibili URL"
          className="w-96 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 placeholder-zinc-500"
        />
        <button
          type="button"
          onClick={() => void summarize()}
          data-testid="chat-summarize"
          disabled={!bvid.trim() || thinking}
          className="flex items-center gap-1.5 rounded-lg bg-red-500 px-4 py-1.5 text-sm font-semibold text-white hover:bg-red-400 disabled:opacity-40"
        >
          <Send className="h-4 w-4" /> Summarize
        </button>
        <span
          data-testid="llm-status"
          className={`flex items-center gap-1.5 text-xs ${llmUp ? "text-green-400" : "text-red-400"}`}
        >
          <span className="h-2 w-2 rounded-full bg-current" />{" "}
          {llmUp
            ? "Local LLM detected"
            : "No local LLM detected - backend summariser may still work"}
        </span>
      </div>

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {thinking && (
        <p className="mt-3 text-sm text-zinc-500">Fetching transcript and summarising...</p>
      )}

      {summary && (
        <div
          data-testid="chat-result"
          className="mt-4 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4"
        >
          <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
            <FileText className="h-4 w-4" /> Summary
            {transcriptWords !== null && (
              <span className="text-xs font-normal text-zinc-500">
                ({transcriptWords} transcript words)
              </span>
            )}
          </h3>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-zinc-200">
            {summary}
          </p>
        </div>
      )}
    </div>
  );
}
