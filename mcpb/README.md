# bilibili-mcp (MCPB Bundle)

Bilibili (Chinese video platform) bridge - search, trending, video intel and transcript summarization

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "bilibili-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos\bilibili-mcp", "python", "-m", "bilibili_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos\bilibili-mcp/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **capabilities**: capabilities
- **tools_list**: tools_list
- **skills_list**: skills_list
- **skill_content**: skill_content
- **dashboard**: dashboard
- **explore_trending**: explore_trending
- **explore_rank**: explore_rank
- **explore_hot_search**: explore_hot_search
- **search_surface**: search_surface
- **video_info**: video_info
- **video_comments**: video_comments
- **video_transcript**: video_transcript
- **llm_discover**: llm_discover
- **llm_providers**: llm_providers
- **account_status**: account_status
- **logs**: logs
- **bilibili_account**: bilibili_account
- **bilibili_account_status**: bilibili_account(status)
- **bilibili_account_following**: bilibili_account(following)
- **bilibili_account_favorites**: bilibili_account(favorites)
- **bilibili_explore**: bilibili_explore
- **bilibili_explore_trending**: bilibili_explore(trending)
- **bilibili_explore_rank**: bilibili_explore(rank)
- **bilibili_explore_hot_search**: bilibili_explore(hot_search)
- **bilibili_help**: bilibili_help
- **show_bilibili_trending_card**: show_bilibili_trending_card
- **show_bilibili_status_card**: show_bilibili_status_card
- **show_bilibili_cache_card**: show_bilibili_cache_card
- **bilibili_search**: bilibili_search
- **bilibili_search_video**: bilibili_search(video)
- **bilibili_search_user**: bilibili_search(user)
- **bilibili_shutdown**: bilibili_shutdown
- **bilibili_transcript**: bilibili_transcript
- **bilibili_video**: bilibili_video
- **bilibili_video_info**: bilibili_video(info)
- **bilibili_video_comments**: bilibili_video(comments)
- **bilibili_video_pages**: bilibili_video(pages)

## Requirements

- Python 3.12+
- uv
