"""Tests for the portmanteau tools (explore, search, video, transcript, account)."""

from __future__ import annotations

import httpx
import respx

from bilibili_mcp.tools import account, explore, search, transcript, video

API = "https://api.bilibili.com"


@respx.mock
def test_explore_trending():
    respx.get(f"{API}/x/web-interface/popular").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "list": [
                        {"bvid": "BV1", "title": "t", "owner": {"name": "u"}, "stat": {"view": 5}}
                    ]
                },
            },
        )
    )
    result = __import__("asyncio").run(explore.bilibili_explore(operation="trending", limit=5))
    assert result["success"] is True
    assert result["data"][0]["bvid"] == "BV1"
    assert result["data"][0]["play"] == 5


@respx.mock
def test_explore_hot_search():
    respx.get(f"{API}/x/web-interface/search/square").mock(
        return_value=httpx.Response(
            200,
            json={"code": 0, "data": {"trending": {"list": [{"keyword": "k", "show_name": "k"}]}}},
        )
    )
    result = __import__("asyncio").run(explore.bilibili_explore(operation="hot_search", limit=5))
    assert result["success"] is True
    assert result["data"][0]["keyword"] == "k"


@respx.mock
def test_search_video():
    respx.get(f"{API}/x/web-interface/search/type").mock(
        return_value=httpx.Response(
            200,
            json={"code": 0, "data": {"result": [{"bvid": "BV1", "title": "t"}], "numResults": 1}},
        )
    )
    result = __import__("asyncio").run(search.bilibili_search(operation="video", keyword="测试"))
    assert result["success"] is True
    assert result["data"][0]["bvid"] == "BV1"


@respx.mock
def test_video_info_tool():
    respx.get(f"{API}/x/web-interface/view").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "data": {"bvid": "BV1", "aid": 1, "title": "t"}}
        )
    )
    result = __import__("asyncio").run(video.bilibili_video(operation="info", bvid="BV1"))
    assert result["success"] is True
    assert result["data"]["title"] == "t"


@respx.mock
def test_transcript_happy_path():
    respx.get(f"{API}/x/web-interface/view").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": 0,
                "data": {"bvid": "BV1", "pages": [{"cid": 9001, "page": 1, "part": "P1"}]},
            },
        )
    )
    respx.get(f"{API}/x/player/v2").mock(
        return_value=httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "subtitle": {
                        "subtitles": [
                            {
                                "lan": "ai-zh",
                                "ai_status": 2,
                                "subtitle_url": "//s.hdslb.com/sub.json",
                            }
                        ]
                    }
                },
            },
        )
    )
    respx.get("https://s.hdslb.com/sub.json").mock(
        return_value=httpx.Response(
            200, json={"body": [{"from": 0, "content": "hello"}, {"from": 1, "content": "world"}]}
        )
    )
    result = __import__("asyncio").run(transcript.bilibili_transcript(bvid="BV1"))
    assert result["success"] is True
    assert result["data"]["text"] == "hello\nworld"
    assert result["data"]["word_count"] == 2


@respx.mock
def test_transcript_no_subtitles_honest_error():
    respx.get(f"{API}/x/web-interface/view").mock(
        return_value=httpx.Response(
            200,
            json={"code": 0, "data": {"bvid": "BV1", "pages": [{"cid": 9001}]}},
        )
    )
    respx.get(f"{API}/x/player/v2").mock(
        return_value=httpx.Response(200, json={"code": 0, "data": {"subtitle": {"subtitles": []}}})
    )
    result = __import__("asyncio").run(transcript.bilibili_transcript(bvid="BV1"))
    assert result["success"] is False
    assert result["error_type"] == "not_found"


def test_account_status_anonymous():
    result = __import__("asyncio").run(account.bilibili_account(operation="status"))
    assert result["success"] is True
    assert result["data"]["tier"] in ("anonymous", "account")


def test_account_following_requires_login():
    result = __import__("asyncio").run(account.bilibili_account(operation="following"))
    assert result["success"] is False
    assert result["error_type"] == "auth_required"
