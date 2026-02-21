"""Tests for main CLI (offline, synthetic inputs via monkeypatch)."""
from __future__ import annotations

import json
import io
import sys
import unittest
from unittest.mock import patch

from github_fetcher import ReadmeFetchResult


# A minimal synthetic README so we never hit the network.
_FAKE_README = ReadmeFetchResult(
    repo="test/repo",
    ref="main",
    filename="README.md",
    text="# TestRepo\nA tool.\n",
    source_url="https://raw.githubusercontent.com/test/repo/main/README.md",
)


class TestJsonOutputSchema(unittest.TestCase):
    """JSON output must contain required keys in stable order."""

    def _run_score_json(self) -> dict:
        with patch("github_fetcher.fetch_readme", return_value=_FAKE_README):
            captured = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                from main import main
                main(["score", "--repo", "test/repo", "--format", "json"])
            finally:
                sys.stdout = old_stdout
            return json.loads(captured.getvalue())

    def test_required_top_level_keys(self):
        data = self._run_score_json()
        required = [
            "version", "repo", "readme", "source", "overall",
            "scores", "signals",
            "docs_followed_url", "docs_fetch_ok", "docs_signals_used",
        ]
        for key in required:
            self.assertIn(key, data, f"missing top-level key: {key}")

    def test_version_present(self):
        data = self._run_score_json()
        self.assertEqual(data["version"], "0.3.0")

    def test_dimension_order_stable(self):
        data = self._run_score_json()
        dims = list(data["scores"].keys())
        expected = [
            "problem_clarity",
            "novelty_trend_fit",
            "distribution_potential",
            "execution_quality",
        ]
        self.assertEqual(dims, expected)

    def test_signals_sorted(self):
        data = self._run_score_json()
        keys = list(data["signals"].keys())
        self.assertEqual(keys, sorted(keys))

    def test_each_score_has_score_and_why(self):
        data = self._run_score_json()
        for dim, val in data["scores"].items():
            self.assertIn("score", val, f"{dim} missing 'score'")
            self.assertIn("why", val, f"{dim} missing 'why'")
            self.assertIsInstance(val["score"], (int, float))
            self.assertIsInstance(val["why"], str)


if __name__ == "__main__":
    unittest.main()
