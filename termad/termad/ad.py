"""Ad schema, loading, and validation for termad."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
import json
from pathlib import Path
from typing import Any

REQUIRED_METADATA_FIELDS = ("advertiser", "url")


@dataclass(frozen=True)
class Ad:
    """A validated ad definition."""

    frames: list[str]
    frame_rate: float
    duration: float
    metadata: dict[str, str]


def load_ad_from_dict(data: dict[str, Any]) -> Ad:
    """Validate and load an ad from a Python dictionary."""
    if not isinstance(data, dict):
        raise ValueError("Ad data must be a dictionary.")

    frames_raw = data.get("frames")
    if not isinstance(frames_raw, list) or not frames_raw:
        raise ValueError("Ad field 'frames' must be a non-empty list of strings.")

    frames: list[str] = []
    for index, frame in enumerate(frames_raw):
        if not isinstance(frame, str):
            raise ValueError(f"Ad frame at index {index} must be a string.")
        normalized = frame.rstrip("\n")
        if not normalized:
            raise ValueError(f"Ad frame at index {index} cannot be empty.")
        frames.append(normalized)

    frame_rate = _parse_positive_number(data.get("frame_rate"), field_name="frame_rate")
    duration = _parse_positive_number(data.get("duration"), field_name="duration")

    metadata_raw = data.get("metadata")
    if not isinstance(metadata_raw, dict):
        raise ValueError("Ad field 'metadata' must be a dictionary.")

    metadata: dict[str, str] = {}
    for key in REQUIRED_METADATA_FIELDS:
        value = metadata_raw.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Ad metadata must include non-empty string field '{key}'.")
        metadata[key] = value.strip()

    for key, value in metadata_raw.items():
        if key not in metadata and isinstance(value, str):
            metadata[key] = value

    return Ad(frames=frames, frame_rate=frame_rate, duration=duration, metadata=metadata)


def load_ad_from_json(path: str | Path) -> Ad:
    """Validate and load an ad from a JSON file path."""
    file_path = Path(path)
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Ad JSON file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in ad file {file_path}: {exc.msg}") from exc

    return load_ad_from_dict(payload)


def load_builtin_ad() -> Ad:
    """Load the bundled bouncing-logo ad."""
    resource = resources.files("termad").joinpath("assets/dvd_ad.json")
    with resources.as_file(resource) as path:
        return load_ad_from_json(path)


def _parse_positive_number(value: Any, field_name: str) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"Ad field '{field_name}' must be a number greater than 0.")

    parsed = float(value)
    if parsed <= 0:
        raise ValueError(f"Ad field '{field_name}' must be greater than 0.")
    return parsed
