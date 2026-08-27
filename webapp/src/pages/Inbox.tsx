import { Inbox as InboxIcon } from "lucide-react";

export default function Inbox() {
  return (
    <div data-testid="inbox-page" className="mx-auto max-w-3xl">
      <h2 className="flex items-center gap-2 text-xl font-bold">
        <InboxIcon className="h-5 w-5 text-red-400" /> Inbox
      </h2>
      <div className="mt-4 rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
        <p className="text-sm text-zinc-400" data-testid="inbox-empty">
          Nothing here yet. This server has no webhook inbox - discovery, search and transcripts are
          pull-based. Notifications will appear here if a feed source is added later.
        </p>
      </div>
    </div>
  );
}
