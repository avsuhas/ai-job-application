"""Tests for shared utilities: ids, files, text, config."""

import json

import pytest

from job_platform.shared.config import Settings, load_settings
from job_platform.shared.errors import ConfigurationError
from job_platform.shared.files import atomic_write_json, atomic_write_text, read_json
from job_platform.shared.ids import new_id, stable_hash
from job_platform.shared.text import normalize_whitespace, slugify, truncate


class TestIds:
    def test_new_id_has_prefix_and_is_unique(self):
        first = new_id("search")
        second = new_id("search")
        assert first.startswith("search_")
        assert first != second

    def test_stable_hash_is_deterministic_and_normalized(self):
        assert stable_hash("Google", "SWE") == stable_hash("  google ", "swe")
        assert stable_hash("Google", "SWE") != stable_hash("Google", "SRE")


class TestFiles:
    def test_atomic_write_and_read_json(self, tmp_path):
        target = tmp_path / "nested" / "data.json"
        atomic_write_json(target, {"a": 1})
        assert read_json(target) == {"a": 1}

    def test_atomic_write_replaces_existing(self, tmp_path):
        target = tmp_path / "file.txt"
        atomic_write_text(target, "one")
        atomic_write_text(target, "two")
        assert target.read_text() == "two"
        # No temp files left behind
        assert [p.name for p in tmp_path.iterdir()] == ["file.txt"]


class TestText:
    def test_normalize_whitespace(self):
        assert normalize_whitespace("  a\n\t b  c ") == "a b c"

    def test_slugify(self):
        assert slugify("Senior Backend Engineer (L5)") == "senior-backend-engineer-l5"

    def test_truncate(self):
        assert truncate("abcdef", 4) == "abc…"
        assert truncate("abc", 10) == "abc"


class TestConfig:
    def test_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        settings = load_settings()
        assert settings.reasoning.provider == "claude"
        assert settings.applications.automation_mode == "review"
        assert settings.paths.tracker_path.name == "tracker.csv"

    def test_settings_file_is_loaded(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / "config"
        cfg.mkdir()
        (cfg / "settings.json").write_text(
            json.dumps({"job_search": {"minimum_match_score": 75}})
        )
        settings = load_settings()
        assert settings.job_search.minimum_match_score == 75

    def test_env_overrides_settings_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = tmp_path / "config"
        cfg.mkdir()
        (cfg / "settings.json").write_text(json.dumps({"reasoning": {"model": "from-file"}}))
        monkeypatch.setenv("REASONING__MODEL", "from-env")
        settings = load_settings()
        assert settings.reasoning.model == "from-env"

    def test_invalid_settings_json_raises_actionable_error(self, tmp_path):
        bad = tmp_path / "settings.json"
        bad.write_text("{not json")
        with pytest.raises(ConfigurationError) as excinfo:
            load_settings(bad)
        assert "invalid JSON" in str(excinfo.value)

    def test_runtime_directories_cover_required_layout(self):
        settings = Settings()
        names = {str(p) for p in settings.paths.runtime_directories()}
        assert "user_data/candidate/resume" in names
        assert "user_data/applications/packages" in names
        assert "user_data/logs" in names
