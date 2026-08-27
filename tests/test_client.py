"""Tests for bilibili_mcp.client - httpx transport and error mapping, mocked with respx."""

from __future__ import annotations

import httpx
import pytest
import respx

from bilibili_mcp.client import BilibiliClient, BilibiliError

API = "https://api.bilibili.com"


def _make() -> BilibiliClient:
    c = BilibiliClient()
    c._base = API
    c._cookie = ""
    return c


@respx.mock
def test_popular_ok():
    respx.get(f"{API}/x/web-interface/popular").mock(
        return_value=httpx.Response(200, json={"code": 0, "data": {"list": [{"bvid": "BV1"}]}})
    )
    items = _make().popular()
    assert items == [{"bvid": "BV1"}]


@respx.mock
def test_ranking_ok():
    respx.get(f"{API}/x/web-interface/ranking").mock(
        return_value=httpx.Response(200, json={"code": 0, "data": {"list": [{"bvid": "BV2"}]}})
    )
    items = _make().ranking(rid=3)
    assert items == [{"bvid": "BV2"}]


@respx.mock
def test_video_info_ok():
    respx.get(f"{API}/x/web-interface/view").mock(
        return_value=httpx.Response(200, json={"code": 0, "data": {"bvid": "BV1"}})
    )
    data = _make().video_info(bvid="BV1")
    assert data["bvid"] == "BV1"


def test_video_info_requires_identifier():
    with pytest.raises(BilibiliError):
        _make().video_info()


@respx.mock
def test_not_logged_in_maps_to_auth_required():
    respx.get(f"{API}/x/web-interface/view").mock(
        return_value=httpx.Response(200, json={"code": -101, "message": "账号未登录"})
    )
    with pytest.raises(BilibiliError) as ei:
        _make().video_info(bvid="BV1")
    assert ei.value.error_type == "auth_required"


@respx.mock
def test_http_412_maps_to_rate_limited():
    respx.get(f"{API}/x/web-interface/popular").mock(return_value=httpx.Response(412))
    with pytest.raises(BilibiliError) as ei:
        _make().popular()
    assert ei.value.error_type == "rate_limited"


@respx.mock
def test_comments_ok():
    respx.get(f"{API}/x/v2/reply").mock(
        return_value=httpx.Response(
            200, json={"code": 0, "data": {"replies": [{"rpid": 1, "member": {"uname": "u"}}]}}
        )
    )
    replies = _make().comments(170001)
    assert replies[0]["rpid"] == 1
