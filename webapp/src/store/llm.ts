import { type Provider, discoverProviders } from "@/lib/provider";
import { create } from "zustand";

interface LlmState {
  providers: Provider[];
  status: Record<string, "probing" | "detected" | "not_found">;
  selectedProvider: string;
  selectedModel: string;
  availableModels: string[];
  probing: boolean;
  probe: () => Promise<void>;
  setProvider: (name: string) => Promise<void>;
  setModel: (model: string) => void;
}

const KEY_PROVIDER = "bilibili_llm_provider";
const KEY_MODEL = "bilibili_llm_model";

export const useLlmStore = create<LlmState>((set, get) => ({
  providers: [],
  status: {},
  selectedProvider: localStorage.getItem(KEY_PROVIDER) || "",
  selectedModel: localStorage.getItem(KEY_MODEL) || "",
  availableModels: [],
  probing: false,
  probe: async () => {
    set({ probing: true, status: { ollama: "probing", lmstudio: "probing" } });
    const providers = await discoverProviders();
    const status: Record<string, "probing" | "detected" | "not_found"> = {};
    for (const p of providers) status[p.name] = p.status;
    const saved = localStorage.getItem(KEY_PROVIDER);
    const selected =
      saved && providers.some((p) => p.name === saved) ? saved : providers[0]?.name || "";
    set({ providers, status, selectedProvider: selected, probing: false });
    if (selected) await get().setProvider(selected);
  },
  setProvider: async (name) => {
    localStorage.setItem(KEY_PROVIDER, name);
    set({ selectedProvider: name });
    const provider = get().providers.find((p) => p.name === name);
    if (!provider) return;
    try {
      const r = await fetch(`${provider.base}/models`);
      if (r.ok) {
        const body = await r.json();
        const ids = (body.data || body.models || []).map(
          (m: { id?: string; name?: string }) => m.id || m.name || "",
        );
        const saved = localStorage.getItem(KEY_MODEL);
        const model = ids.includes(saved || "") ? saved : ids[0] || "";
        set({ availableModels: ids, selectedModel: model || "" });
        if (model) localStorage.setItem(KEY_MODEL, model);
      }
    } catch {
      set({ availableModels: [], selectedModel: "" });
    }
  },
  setModel: (model) => {
    localStorage.setItem(KEY_MODEL, model);
    set({ selectedModel: model });
  },
}));
