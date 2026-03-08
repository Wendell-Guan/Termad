from __future__ import annotations

import json

import pytest

from termad.ad import Ad, load_ad_from_dict, load_ad_from_json, load_builtin_ad


def valid_payload() -> dict:
    return {
        "frames": ["frame one\nline two"],
        "frame_rate": 2,
        "duration": 4,
        "metadata": {
            "advertiser": "ACME",
            "url": "https://example.com",
            "tagline": "Sample",
        },
    }


def test_load_ad_from_dict_valid() -> None:
    ad = load_ad_from_dict(valid_payload())
    assert isinstance(ad, Ad)
    assert ad.frame_rate == 2.0
    assert ad.duration == 4.0
    assert ad.metadata["advertiser"] == "ACME"


def test_load_ad_from_dict_requires_frames() -> None:
    payload = valid_payload()
    payload["frames"] = []
    with pytest.raises(ValueError, match="frames"):
        load_ad_from_dict(payload)


def test_load_ad_from_dict_requires_positive_numbers() -> None:
    payload = valid_payload()
    payload["frame_rate"] = 0
    with pytest.raises(ValueError, match="frame_rate"):
        load_ad_from_dict(payload)


def test_load_ad_from_dict_requires_metadata_fields() -> None:
    payload = valid_payload()
    payload["metadata"] = {"advertiser": "ACME"}
    with pytest.raises(ValueError, match="url"):
        load_ad_from_dict(payload)


def test_load_ad_from_json_round_trip(tmp_path) -> None:
    path = tmp_path / "ad.json"
    path.write_text(json.dumps(valid_payload()), encoding="utf-8")
    ad = load_ad_from_json(path)
    assert ad.frames[0].startswith("frame one")


def test_load_ad_from_json_invalid_json(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_ad_from_json(path)


def test_load_builtin_ad() -> None:
    ad = load_builtin_ad()
    assert ad.frames
    assert ad.metadata["advertiser"]
    assert ad.metadata["url"]
