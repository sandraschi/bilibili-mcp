/** API base for the bilibili-mcp backend (REST on 11185). */
export const API_BASE = "http://127.0.0.1:11185";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) {
    throw new Error(`HTTP ${r.status} on ${path}`);
  }
  return (await r.json()) as T;
}

export interface Health {
  status: string;
  server: string;
  version: string;
  uptime_seconds: number;
  tool_count: number;
  configured: boolean;
  tier: string;
  providers: {
    bilibili: { tier: string; configured: boolean };
  };
}

export interface Dashboard {
  server: string;
  version: string;
  uptime_seconds: number;
  tool_count: number;
  configured: boolean;
  tier: string;
  rate_limited: boolean;
  llm_configured: boolean;
}

export interface SlimVideo {
  bvid: string;
  aid: number;
  title: string;
  desc: string;
  duration: number;
  pic: string;
  play: number;
  danmaku: number;
  author: string;
  mid: number;
  pubdate: number;
  url: string;
}

export interface VideoInfo {
  bvid: string;
  aid: number;
  title: string;
  desc: string;
  duration: number;
  pic: string;
  pubdate: number;
  tname: string;
  url: string;
  owner: { mid: number; name: string };
  stats: {
    view: number;
    danmaku: number;
    reply: number;
    favorite: number;
    coin: number;
    share: number;
    like: number;
  };
  pages: number;
}

export interface Comment {
  rpid: number;
  author: string;
  likes: number;
  time: number;
  text: string;
}

export interface Transcript {
  bvid: string;
  cid: number;
  lang: string;
  text: string;
  word_count: number;
}

export interface UserHit {
  mid: number;
  name: string;
  fans: number;
  videos: number;
  sign: string;
  url: string;
}

export interface ToolResult<T> {
  success: boolean;
  operation?: string;
  message?: string;
  count?: number;
  error?: string;
  error_type?: string;
  suggestions?: string[];
  cached?: boolean;
  data: T;
}

export interface ExploreResponse {
  success: boolean;
  operation: string;
  data: SlimVideo[];
  count: number;
  message?: string;
  error?: string;
}

export interface HotSearchItem {
  keyword: string;
  heat: number | string;
}

export interface HotSearchResponse {
  success: boolean;
  operation: string;
  data: HotSearchItem[];
  count: number;
  message?: string;
  error?: string;
}

export interface VideoInfoResponse {
  success: boolean;
  operation: string;
  data: VideoInfo;
  message?: string;
  error?: string;
}

export interface CommentsResponse {
  success: boolean;
  operation: string;
  data: { aid: number; comments: Comment[]; count: number };
  message?: string;
  error?: string;
}

export interface TranscriptResponse {
  success: boolean;
  data: Transcript;
  message?: string;
  error?: string;
  error_type?: string;
}

export interface SearchResponse {
  success: boolean;
  operation: string;
  data: SlimVideo[] | UserHit[];
  count: number;
  message?: string;
  error?: string;
  error_type?: string;
  suggestions?: string[];
}

export interface SummaryResult {
  success: boolean;
  summary: string;
  transcript_word_count: number;
  error?: string;
}

export interface LogEntry {
  ts: string;
  level: string;
  source: string;
  message: string;
}
