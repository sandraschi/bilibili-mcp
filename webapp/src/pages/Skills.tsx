import { API_BASE, api } from "@/lib/api";
import { Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

interface Skill {
  name: string;
  uri: string;
  description: string;
}

export default function Skills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [content, setContent] = useState("");
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api<{ skills: Skill[] }>("/api/skills");
      setSkills(res.skills);
      if (res.skills[0]) setSelected(res.skills[0].name);
    } catch {
      setSkills([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!selected) {
      setContent("");
      return;
    }
    let cancelled = false;
    void fetch(`${API_BASE}/api/skills/${encodeURIComponent(selected)}`)
      .then((r) => r.text())
      .then((t) => {
        if (!cancelled) setContent(t);
      })
      .catch(() => {
        if (!cancelled) setContent("");
      });
    return () => {
      cancelled = true;
    };
  }, [selected]);

  return (
    <div data-testid="skills-page" className="mx-auto max-w-4xl">
      <h2 className="flex items-center gap-2 text-xl font-bold">
        <Sparkles className="h-5 w-5 text-red-400" /> Skills
      </h2>
      {loading && <p className="mt-4 text-sm text-zinc-500">Loading skills...</p>}
      <div data-testid="skills-list" className="mt-4 space-y-3">
        {skills.map((s) => (
          <div
            key={s.name}
            data-testid="skill-entry"
            className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4"
          >
            <div className="flex items-center gap-2">
              <button
                type="button"
                data-testid={`skill-select-${s.name}`}
                onClick={() => setSelected(s.name)}
                className={`text-sm font-semibold ${
                  selected === s.name ? "text-red-400" : "text-zinc-200 hover:text-red-400"
                }`}
              >
                {s.name}
              </button>
            </div>
            <p className="mt-1 text-xs text-zinc-400">{s.description}</p>
          </div>
        ))}
        {!loading && skills.length === 0 && (
          <p className="text-sm text-zinc-500">No skills reported.</p>
        )}
      </div>
      {content && (
        <div className="prose-dark mt-5 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h3 className="text-sm font-semibold text-red-400">{selected}</h3>
          <div className="mt-2 text-sm">{content}</div>
        </div>
      )}
    </div>
  );
}
