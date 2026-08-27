import { type Dashboard as DashboardInfo, api } from "@/lib/api";
import { BookOpen, Cpu, Gauge, Server, Sparkles, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface MockTrending {
  bvid: string;
  title: string;
  author: string;
  play: number;
}

const MOCK_TRENDING: MockTrending[] = [
  {
    bvid: "BV1Mock0001",
    title: "How to Set Your Bilibili Cookie (sample)",
    author: "Joe Mocky",
    play: 12345,
  },
  {
    bvid: "BV1Mock0002",
    title: "Top 10 Science Videos (sample data)",
    author: "Sandra Mockinger",
    play: 9876,
  },
  { bvid: "BV1Mock0003", title: "MCP Fleet Tour (demo)", author: "Mock Bot", play: 4321 },
];

export default function Dashboard() {
  const [dashboard, setDashboard] = useState<DashboardInfo | null>(null);
  const [retry, setRetry] = useState(0);

  // biome-ignore lint/correctness/useExhaustiveDependencies: retry dep intentionally re-triggers the poll
  useEffect(() => {
    let cancelled = false;
    const delays = [1000, 2000, 4000, 8000, 16000];
    let timer: ReturnType<typeof setTimeout>;
    const attempt = async (i: number) => {
      try {
        const d = await api<DashboardInfo>("/api/dashboard");
        if (!cancelled) setDashboard(d);
      } catch {
        if (!cancelled) {
          timer = setTimeout(
            () => void attempt(Math.min(i + 1, delays.length - 1)),
            delays[Math.min(i, delays.length - 1)],
          );
        }
      }
    };
    void attempt(0);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [retry]);

  const configured = !!dashboard?.configured;

  return (
    <div data-testid="dashboard" className="mx-auto max-w-5xl">
      <section className="rounded-xl border border-zinc-800 bg-gradient-to-br from-zinc-900 to-zinc-950 p-8">
        <h2 className="text-3xl font-bold">
          What is <span className="text-red-400">trending</span> on Bilibili?
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-zinc-400">
          Chinese video intelligence: popular feed, rankings, hot search keywords, single-video
          metadata, comments and AI subtitles - turned into summarizable transcript text.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            to="/explore"
            data-testid="cta-explore"
            className="flex items-center gap-2 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white hover:bg-red-400"
          >
            <TrendingUp className="h-4 w-4" /> Open the feed
          </Link>
          {!configured && (
            <Link
              to="/settings"
              data-testid="onboarding-cue"
              className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
            >
              Complete onboarding - set your Bilibili cookie
            </Link>
          )}
        </div>
      </section>

      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Kpi
          testid="kpi-server"
          icon={<Server className="h-4 w-4" />}
          label="Server"
          value={dashboard?.version ?? "-"}
        />
        <Kpi
          testid="kpi-tools"
          icon={<Sparkles className="h-4 w-4" />}
          label="Tools"
          value={String(dashboard?.tool_count ?? "-")}
        />
        <Kpi
          testid="kpi-tier"
          icon={<Gauge className="h-4 w-4" />}
          label="Tier"
          value={dashboard?.tier ?? "anonymous"}
          accent={dashboard?.tier === "account"}
        />
        <Kpi
          testid="kpi-configured"
          icon={<Cpu className="h-4 w-4" />}
          label="Configured"
          value={configured ? "Yes" : "No"}
          accent={configured}
        />
      </div>

      {!configured && (
        <section
          data-testid="mock-data-banner"
          className="mt-6 rounded-lg border border-amber-500/50 bg-amber-500/10 p-4"
        >
          <div className="flex flex-wrap items-center gap-2 text-sm text-amber-300">
            <span className="rounded bg-amber-500 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-zinc-950">
              MOCK
            </span>
            <span data-testid="mock-sample">
              Sample data shown below. These clear after you set your Bilibili cookie in Settings.
            </span>
          </div>
          <div data-testid="trending-sample" className="mt-3 space-y-2">
            {MOCK_TRENDING.map((v) => (
              <div
                key={v.bvid}
                className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3"
              >
                <span
                  data-testid="mock-badge"
                  className="rounded bg-amber-500/15 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-amber-400"
                >
                  sample
                </span>
                <span className="text-sm text-zinc-200">{v.title}</span>
                <span className="ml-auto text-sm text-zinc-400">{v.author}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-red-400">
            <BookOpen className="h-4 w-4" /> Content intelligence
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-zinc-300">
            Bilibili subtitles are fetched and returned as plain text, so an LLM can summarise or
            translate a video without watching it.
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h3 className="text-sm font-semibold text-red-400">Anonymous first</h3>
          <p className="mt-2 text-sm leading-relaxed text-zinc-300">
            Trending, rankings, search, video intel and transcripts all work without an account.
            Responses are TTL-cached to stay polite to Bilibili.
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h3 className="text-sm font-semibold text-red-400">Tiers</h3>
          <p className="mt-2 text-sm leading-relaxed text-zinc-300">
            Anonymous works now. A logged-in Bilibili cookie unlocks the account tier and passes
            search risk control.
          </p>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setRetry((r) => r + 1)}
        className="mt-4 text-sm text-zinc-400 hover:text-red-400"
        data-testid="health-retry"
      >
        Retry dashboard
      </button>
    </div>
  );
}

function Kpi({
  testid,
  icon,
  label,
  value,
  accent = false,
}: { testid: string; icon: React.ReactNode; label: string; value: string; accent?: boolean }) {
  return (
    <div data-testid={testid} className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
      <div
        className={`flex items-center gap-1.5 text-sm ${accent ? "text-green-400" : "text-zinc-400"}`}
      >
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-1 text-xl font-bold">{value}</div>
    </div>
  );
}
