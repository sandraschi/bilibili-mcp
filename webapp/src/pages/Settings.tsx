import { type Dashboard, api } from "@/lib/api";
import { useLlmStore } from "@/store/llm";
import { CheckCircle2, KeyRound, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

export default function Settings() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const { providers, probe, probing } = useLlmStore();

  useEffect(() => {
    void api<Dashboard>("/api/dashboard")
      .then(setDashboard)
      .catch(() => setDashboard(null));
  }, []);

  const configured = !!dashboard?.configured;

  return (
    <div data-testid="settings-page" className="mx-auto max-w-3xl space-y-6">
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="text-sm font-semibold text-red-400">Backend health</h2>
        <div className="mt-3 grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
          <div>
            <div className="text-xs text-zinc-500">Server</div>
            <div data-testid="settings-server">{dashboard?.server ?? "-"}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-500">Version</div>
            <div>{dashboard?.version ?? "-"}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-500">Tools</div>
            <div data-testid="settings-tools">{dashboard?.tool_count ?? "-"}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-500">Tier</div>
            <div>{dashboard?.tier ?? "-"}</div>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-red-400">
          <KeyRound className="h-4 w-4" /> Bilibili account (onboarding)
        </h2>
        <div className="mt-3 flex items-center gap-2 text-sm">
          {configured ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span data-testid="token-state">Cookie configured - account tier active</span>
            </>
          ) : (
            <>
              <XCircle className="h-4 w-4 text-red-500" />
              <span data-testid="token-state">
                Anonymous tier - set BILIBILI_COOKIE to unlock account tools
              </span>
            </>
          )}
        </div>
        <p className="mt-2 text-xs text-zinc-500">
          Set <code className="rounded bg-zinc-800 px-1">BILIBILI_COOKIE</code> in the repo{" "}
          <code className="rounded bg-zinc-800 px-1">.env</code> with a logged-in{" "}
          <code className="rounded bg-zinc-800 px-1">SESSDATA=...;bili_jct=...</code> cookie. This
          passes search risk control and unlocks the account tier.
        </p>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5">
        <h2 className="text-sm font-semibold text-red-400">Local intelligence</h2>
        <div className="mt-3 flex items-center gap-2 text-sm">
          {dashboard?.llm_configured ? (
            <>
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span data-testid="llm-state">LLM configured - summarise transcripts to English</span>
            </>
          ) : (
            <>
              <XCircle className="h-4 w-4 text-zinc-600" />
              <span data-testid="llm-state">LLM not configured - summarise may be unavailable</span>
            </>
          )}
        </div>
        <div className="mt-3 space-y-2">
          {probing && providers.length === 0 && (
            <p className="text-xs text-zinc-500">Probing providers...</p>
          )}
          {providers.map((p) => (
            <div
              key={p.name}
              className="flex items-center gap-2 text-sm"
              data-testid={`provider-${p.name}`}
            >
              {p.status === "detected" ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-zinc-600" />
              )}
              <span className="w-28 capitalize">{p.name}</span>
              <span className="text-xs text-zinc-500">:{p.port ?? "custom"}</span>
              <span className={p.status === "detected" ? "text-green-400" : "text-zinc-500"}>
                {p.status === "detected" ? "Detected" : "Not found"}
              </span>
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={() => void probe()}
          className="mt-4 rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-300 hover:text-red-400"
        >
          Re-probe providers
        </button>
      </section>
    </div>
  );
}
