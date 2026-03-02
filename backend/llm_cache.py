"""Lightweight persistent cache for LLM responses."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Optional


_CACHE_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "llm_cache.json")
)
_LOCK = Lock()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _load_cache_unlocked() -> dict:
    if not os.path.exists(_CACHE_FILE):
        return {}
    try:
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_cache_unlocked(cache: dict) -> None:
    os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def make_key(text: str, provider: str, model: str, prompt_version: str = "v1") -> str:
    payload = {
        "text": text.strip(),
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def get(key: str, ttl_days: int = 30) -> Optional[Any]:
    with _LOCK:
        cache = _load_cache_unlocked()
        entry = cache.get(key)
        if not entry:
            return None

        cached_at_raw = entry.get("cached_at")
        if not cached_at_raw:
            return None

        try:
            cached_at = datetime.fromisoformat(cached_at_raw)
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)
        except Exception:
            return None

        if ttl_days > 0 and _utcnow() - cached_at > timedelta(days=ttl_days):
            cache.pop(key, None)
            _save_cache_unlocked(cache)
            return None

        return entry.get("payload")


def set(key: str, payload: Any) -> None:
    with _LOCK:
        cache = _load_cache_unlocked()
        cache[key] = {
            "cached_at": _utcnow().isoformat(),
            "payload": payload,
        }
        _save_cache_unlocked(cache)


def get_stats(ttl_days: int = 30) -> dict:
    with _LOCK:
        cache = _load_cache_unlocked()
        total_entries = len(cache)
        active_entries = 0
        expired_entries = 0

        now = _utcnow()
        for entry in cache.values():
            cached_at_raw = entry.get("cached_at")
            if not cached_at_raw:
                expired_entries += 1
                continue

            try:
                cached_at = datetime.fromisoformat(cached_at_raw)
                if cached_at.tzinfo is None:
                    cached_at = cached_at.replace(tzinfo=timezone.utc)
            except Exception:
                expired_entries += 1
                continue

            if ttl_days > 0 and now - cached_at > timedelta(days=ttl_days):
                expired_entries += 1
            else:
                active_entries += 1

        file_size_bytes = os.path.getsize(_CACHE_FILE) if os.path.exists(_CACHE_FILE) else 0
        return {
            "cache_file": _CACHE_FILE,
            "ttl_days": ttl_days,
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "file_size_bytes": file_size_bytes,
        }


def clear() -> dict:
    with _LOCK:
        cache = _load_cache_unlocked()
        removed_entries = len(cache)
        _save_cache_unlocked({})
        return {
            "removed_entries": removed_entries,
            "cache_file": _CACHE_FILE,
        }
