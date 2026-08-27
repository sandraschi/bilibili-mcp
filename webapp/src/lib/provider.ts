/** Local LLM provider probing (Ollama / LM Studio) per SOTA webapp standard. */

export interface Provider {
  name: string;
  base: string;
  port: number | null;
  status: "probing" | "detected" | "not_found";
}

const TARGETS: { name: string; base: string; port: number | null }[] = [
  { name: "ollama", base: "http://127.0.0.1:11434/v1", port: 11434 },
  { name: "lmstudio", base: "http://127.0.0.1:1234/v1", port: 1234 },
];

async function probeTarget(base: string): Promise<boolean> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 1500);
  try {
    const r = await fetch(`${base}/models`, { signal: controller.signal });
    return r.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

export async function discoverProviders(): Promise<Provider[]> {
  const providers: Provider[] = [];
  for (const t of TARGETS) {
    const ok = await probeTarget(t.base);
    providers.push({
      name: t.name,
      base: t.base,
      port: t.port,
      status: ok ? "detected" : "not_found",
    });
  }
  return providers;
}
