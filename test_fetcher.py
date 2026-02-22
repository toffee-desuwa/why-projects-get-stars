"""Tests for github_fetcher (offline, no network)."""
from __future__ import annotations

import unittest

from github_fetcher import extract_docs_url


class TestInvalidRepoError(unittest.TestCase):
    """fetch_readme must raise ValueError with the actual repo string."""

    def test_missing_slash(self):
        from github_fetcher import fetch_readme

        with self.assertRaises(ValueError) as ctx:
            fetch_readme("badrepo")
        self.assertIn("badrepo", str(ctx.exception))

    def test_empty_string(self):
        from github_fetcher import fetch_readme

        with self.assertRaises(ValueError) as ctx:
            fetch_readme("")
        # repr('') gives "''" (single quotes in f-string)
        self.assertIn("''", str(ctx.exception))


class TestExtractDocsUrl(unittest.TestCase):
    """extract_docs_url should find docs links using 3 strategies."""

    def test_markdown_link(self):
        text = "[Docs](https://example.com/docs) | [Contributing](CONTRIBUTING.md)"
        self.assertEqual(extract_docs_url(text), "https://example.com/docs")

    def test_url_path_contains_docs(self):
        text = "Visit https://ui.shadcn.com/docs to view the documentation."
        self.assertEqual(extract_docs_url(text), "https://ui.shadcn.com/docs")

    def test_bare_url_same_line_as_keyword(self):
        text = "Check our docs at https://example.com/guide"
        self.assertEqual(extract_docs_url(text), "https://example.com/guide")

    def test_no_docs_link(self):
        text = "# MyLib\nA simple library.\n"
        self.assertIsNone(extract_docs_url(text))

    def test_heading_then_url_on_next_line(self):
        # "## Documentation" heading, URL on a separate line with "documentation" word
        text = "## Documentation\n\nVisit https://example.com/docs to learn more."
        url = extract_docs_url(text)
        self.assertEqual(url, "https://example.com/docs")


if __name__ == "__main__":
    unittest.main()
