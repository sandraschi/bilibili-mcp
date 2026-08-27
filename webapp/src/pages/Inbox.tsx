import { Inbox as InboxIcon } from "lucide-react";

export default function Inbox() {
  return (
    <div data-testid="inbox-page" className="mx-auto max-w-3xl">
      <h2 className="flex items-center gap-2 text-xl font-bold" data-testid="inbox-title">
        <InboxIcon className="h-5 w-5 text-red-400" /> Inbox
      </h2>
      <div
        className="mt-4 rounded-lg border border-zinc-800 bg-zinc-900/50 p-6"
        data-testid="inbox-panel"
      >
        <p className="text-sm text-zinc-400" data-testid="inbox-empty">
          Nothing here yet. This server has no webhook inbox - discovery, search and transcripts are
          pull-based. Notifications will appear here if a feed source is added later.
        </p>
        <a
          href="/explore"
          data-testid="inbox-explore-link"
          className="mt-4 inline-block text-sm font-semibold text-red-400 hover:text-red-300"
        >
          Explore trending content instead
        </a>
      </div>
    </div>
  );
}
