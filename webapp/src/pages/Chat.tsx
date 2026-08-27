import { API_BASE, api } from "@/lib/api";
import { useLlmStore } from "@/store/llm";
import { Bot, Download, Eraser, Send, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

const STORAGE_KEY = "bilibili_chat_history";
const HISTORY_CAP = 100;

const PERSONALITIES = [
  {
    id: "researcher",
    label: "Researcher",
    system:
      "You are a concise Bilibili content researcher. Summarise transcripts and rank videos with evidence.",
  },
  {
    id: "translator",
    label: "Translator",
    system:
      "You are a careful Chinese-to-English translator. Output faithful, fluent translations only.",
  },
  {
    id: "curator",
    label: "Curator",
    system: "You are a Bilibili curator. Recommend videos and trends with reasons.",
  },
  { id: "custom", label: "Custom", system: "" },
];

const EXAMPLE_PROMPTS = [
  "Summarise what is trending on Bilibili right now",
  "Explain the appeal of danmaku to someone new",
  "Help me find educational videos about calculus",
  "Translate this title: 微积分入门到精通",
  "Compare Bilibili to YouTube for Chinese content",
  "What makes a good UP主 (creator) channel?",
];

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? (JSON.parse(raw) as Message[]) : [];
    return Array.isArray(parsed) ? parsed.slice(-HISTORY_CAP) : [];
  } catch {
    return [];
  }
}

function nextId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `m-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(loadHistory);
  const [input, setInput] = useState("");
  const [personality, setPersonality] = useState("researcher");
  const [skill, setSkill] = useState("");
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const probe = useLlmStore((s) => s.probe);
  const providers = useLlmStore((s) => s.providers);

  useEffect(() => {
    void probe();
    void api<{ skills: { name: string; description: string }[] }>("/api/skills")
      .then((r) => setSkill(r.skills?.[0]?.description ?? ""))
      .catch(() => setSkill(""));
  }, [probe]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-HISTORY_CAP)));
  }, [messages]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: intentional - scroll to latest message when history grows
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const llmUp = providers.some((p) => p.status === "detected");

  const send = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || thinking) return;
    const personalitySystem = PERSONALITIES.find((p) => p.id === personality)?.system ?? "";
    const system = [personalitySystem, skill && `Skill context: ${skill}`]
      .filter(Boolean)
      .join("\n\n");
    const next = [...messages, { id: nextId(), role: "user" as const, content }];
    setMessages(next);
    setInput("");
    setThinking(true);
    setError("");
    try {
      const r = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "",
          messages: [
            ...(system ? [{ role: "system", content: system }] : []),
            ...next.map((m) => ({ role: m.role, content: m.content })),
          ],
        }),
      });
      const body = await r.json();
      if (!r.ok || !body.success) {
        throw new Error(body.error || `chat failed (HTTP ${r.status})`);
      }
      setMessages((prev) => [...prev, { id: nextId(), role: "assistant", content: body.reply }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "chat failed");
    } finally {
      setThinking(false);
    }
  };

  const clear = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
    setError("");
  };

  const exportTxt = () => {
    const blob = new Blob(
      [messages.map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n\n")],
      {
        type: "text/plain;charset=utf-8",
      },
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "bilibili-chat.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div data-testid="chat-page" className="mx-auto flex max-w-4xl flex-col">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-xl font-bold">
          <Bot className="h-5 w-5 text-red-400" /> Chat
        </h2>
        <div data-testid="chat-controls" className="flex flex-wrap items-center gap-2">
          <select
            data-testid="personality-select"
            aria-label="Personality"
            value={personality}
            onChange={(e) => setPersonality(e.target.value)}
            className="rounded-lg border border-zinc-700 bg-zinc-800 px-2 py-1 text-sm text-zinc-100"
          >
            {PERSONALITIES.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={exportTxt}
            disabled={messages.length === 0}
            data-testid="chat-export"
            className="flex items-center gap-1 rounded-lg border border-zinc-700 px-3 py-1 text-sm text-zinc-300 hover:text-red-400 disabled:opacity-40"
          >
            <Download className="h-4 w-4" /> Export
          </button>
          <button
            type="button"
            onClick={clear}
            disabled={messages.length === 0}
            data-testid="chat-clear"
            className="flex items-center gap-1 rounded-lg border border-zinc-700 px-3 py-1 text-sm text-zinc-300 hover:text-red-400 disabled:opacity-40"
          >
            <Eraser className="h-4 w-4" /> Clear
          </button>
        </div>
      </div>

      {error && (
        <p
          data-testid="chat-error"
          className="mt-2 rounded border border-red-500/40 bg-red-500/10 p-2 text-sm text-red-300"
        >
          {error}
        </p>
      )}

      <div
        data-testid="chat-messages"
        className="mt-4 h-[52vh] space-y-3 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900/50 p-4"
      >
        {messages.length === 0 && !thinking && (
          <div
            data-testid="chat-empty"
            className="flex h-full flex-col items-center justify-center text-center"
          >
            <Sparkles className="h-8 w-8 text-red-400" />
            <p className="mt-3 text-sm text-zinc-200">
              Ask about Bilibili trends, translate titles, or summarise a video.
            </p>
            <p className="mt-1 text-sm text-zinc-400">
              Local LLM {llmUp ? "detected" : "not detected"}. Without one, chat is unavailable.
            </p>
            <div data-testid="example-prompts" className="mt-4 grid gap-2 sm:grid-cols-2">
              {EXAMPLE_PROMPTS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => void send(p)}
                  className="rounded-lg border border-zinc-700 px-3 py-2 text-left text-sm text-zinc-200 hover:border-red-500/50"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={m.role === "user" ? "text-right" : ""}>
            <div
              className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-left text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-red-500/15 text-zinc-100"
                  : "border border-zinc-800 bg-zinc-900 text-zinc-100"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {thinking && <p className="text-sm text-zinc-400">Thinking...</p>}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex items-center gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && void send()}
          data-testid="chat-input"
          placeholder="Ask about Bilibili, or paste a BV id to summarise its transcript..."
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500"
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={!input.trim() || thinking}
          data-testid="chat-send"
          className="flex items-center gap-1.5 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white hover:bg-red-400 disabled:opacity-40"
        >
          <Send className="h-4 w-4" /> Send
        </button>
      </div>
    </div>
  );
}
