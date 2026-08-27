"""Tests for bilibili_mcp.helpers - id parsing and dict shaping."""

from __future__ import annotations

from bilibili_mcp.helpers import format_video, parse_aid, parse_bvid, slim_comment, slim_video


def test_parse_bvid_plain():
    assert parse_bvid("BV1xx411c7mD") == "BV1xx411c7mD"


def test_parse_bvid_from_url():
    url = "https://www.bilibili.com/video/BV1xx411c7mD?p=1"
    assert parse_bvid(url) == "BV1xx411c7mD"


def test_parse_aid_from_av():
    assert parse_aid("av170001") == 170001
    assert parse_aid("https://www.bilibili.com/video/av170001") == 170001


def test_parse_aid_plain_digits():
    assert parse_aid("170001") == 170001


def test_slim_video_shapes():
    v = slim_video(
        {"bvid": "BV1", "aid": 1, "title": "t", "owner": {"name": "u"}, "stat": {"view": 5}}
    )
    assert v["bvid"] == "BV1"
    assert v["play"] == 5
    assert v["url"] == "https://www.bilibili.com/video/BV1"


def test_format_video_stats():
    v = format_video(
        {
            "bvid": "BV1",
            "aid": 1,
            "title": "t",
            "owner": {"mid": 9, "name": "u"},
            "stat": {"view": 1, "like": 2},
            "pages": [{"cid": 1}],
        }
    )
    assert v["stats"]["view"] == 1
    assert v["stats"]["like"] == 2
    assert v["pages"] == 1


def test_slim_comment():
    c = slim_comment(
        {"rpid": 1, "like": 4, "ctime": 5, "member": {"uname": "x"}, "content": {"message": "hi"}}
    )
    assert c["author"] == "x"
    assert c["text"] == "hi"
