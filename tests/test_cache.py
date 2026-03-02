"""Tests for backend.llm_cache — persistent JSON caching."""

import pytest
from backend import llm_cache


def test_make_key_deterministic():
    k1 = llm_cache.make_key("hello", "openrouter", "model-x")
    k2 = llm_cache.make_key("hello", "openrouter", "model-x")
    assert k1 == k2


def test_make_key_varies_by_input():
    k1 = llm_cache.make_key("hello", "openrouter", "model-x")
    k2 = llm_cache.make_key("world", "openrouter", "model-x")
    assert k1 != k2


def test_set_and_get(tmp_cache):
    key = llm_cache.make_key("test", "provider", "model")
    llm_cache.set(key, {"result": 42})
    assert llm_cache.get(key) == {"result": 42}


def test_get_miss(tmp_cache):
    assert llm_cache.get("nonexistent_key") is None


def test_stats_empty(tmp_cache):
    stats = llm_cache.get_stats()
    assert stats["total_entries"] == 0
    assert stats["active_entries"] == 0


def test_stats_after_set(tmp_cache):
    key = llm_cache.make_key("x", "p", "m")
    llm_cache.set(key, [1, 2, 3])
    stats = llm_cache.get_stats()
    assert stats["total_entries"] == 1
    assert stats["active_entries"] == 1


def test_clear(tmp_cache):
    key = llm_cache.make_key("x", "p", "m")
    llm_cache.set(key, [1])
    result = llm_cache.clear()
    assert result["removed_entries"] == 1
    assert llm_cache.get_stats()["total_entries"] == 0
