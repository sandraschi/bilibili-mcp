import { HelpCircle } from "lucide-react";

export default function Help() {
  return (
    <div data-testid="help-page" className="mx-auto max-w-3xl space-y-6">
      <h2 className="flex items-center gap-2 text-xl font-bold" data-testid="help-title">
        <HelpCircle className="h-5 w-5 text-red-400" /> Help
      </h2>
      <section
        data-testid="help-what"
        className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5"
      >
        <h3 className="text-sm font-semibold text-red-400">What does this server do?</h3>
        <p className="mt-2 text-sm leading-relaxed text-zinc-300">
          bilibili-mcp surfaces the Chinese video platform Bilibili as an MCP tool: trending and
          ranking discovery, hot search keywords, video metadata and comments, and AI subtitle
          transcripts that an LLM can summarise or translate.
        </p>
      </section>
      <section
        data-testid="help-pages"
        className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5"
      >
        <h3 className="text-sm font-semibold text-red-400">Pages</h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-zinc-300">
          <li>
            <span className="font-semibold text-zinc-100">Explore</span> - popular feed, daily
            ranking and hot keywords.
          </li>
          <li>
            <span className="font-semibold text-zinc-100">Search</span> - search videos or creators.
          </li>
          <li>
            <span className="font-semibold text-zinc-100">Video</span> - paste a BV id to inspect
            metadata, comments and transcript.
          </li>
          <li>
            <span className="font-semibold text-zinc-100">Chat</span> - summarise a video from its
            transcript.
          </li>
        </ul>
      </section>
      <section
        data-testid="help-setup"
        className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-5"
      >
        <h3 className="text-sm font-semibold text-red-400">Setup</h3>
        <p className="mt-2 text-sm leading-relaxed text-zinc-300">
          Anonymous mode works out of the box. To unlock account tools and pass search risk control,
          set a Bilibili login cookie in <code className="rounded bg-zinc-800 px-1">.env</code> -
          see the Settings page.
        </p>
      </section>
    </div>
  );
}
