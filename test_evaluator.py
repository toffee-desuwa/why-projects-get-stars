"""Tests for evaluator (offline, synthetic READMEs)."""
from __future__ import annotations

import unittest

from evaluator import evaluate_readme


class TestDocsLinkCredit(unittest.TestCase):
    """
    When a README lacks install/usage but has a docs link,
    execution_quality should still get partial credit.
    """

    def test_docs_link_only(self):
        readme = (
            "# MyLib\n"
            "A tool for X.\n"
            "## Documentation\n"
            "Visit https://mylib.dev/docs\n"
        )
        ev = evaluate_readme(readme)
        eq = ev.scores["execution_quality"].score
        # has_docs_link (+1.0) and docs_is_primary_onboarding (+0.5) on top of base 3.0
        self.assertGreaterEqual(eq, 4.5)

    def test_no_docs_link(self):
        readme = "# MyLib\nA tool for X.\n"
        ev = evaluate_readme(readme)
        eq = ev.scores["execution_quality"].score
        # base 3.0, no install/usage/docs
        self.assertLessEqual(eq, 4.0)


class TestDocsSupplementScoring(unittest.TestCase):
    """
    docs_text should only boost execution_quality for cues the README lacks,
    and docs_signals_applied should list only the signals that changed scoring.
    """

    THIN_README = (
        "# MyLib\n"
        "A tool.\n"
        "## Documentation\n"
        "Visit https://mylib.dev/docs\n"
    )

    RICH_DOCS = (
        "## Installation\n"
        "pip install mylib\n"
        "## Usage\n"
        "1. Import mylib\n"
        "2. Call mylib.run()\n"
        "3. Check output\n"
        "```python\nimport mylib\n```\n"
        "```bash\nmylib --help\n```\n"
    )

    def test_thin_readme_with_rich_docs(self):
        ev_without = evaluate_readme(self.THIN_README)
        ev_with = evaluate_readme(self.THIN_README, docs_text=self.RICH_DOCS)

        eq_before = ev_without.scores["execution_quality"].score
        eq_after = ev_with.scores["execution_quality"].score

        # Docs provide install + usage + steps + code blocks the README lacks.
        self.assertGreater(eq_after, eq_before)
        self.assertIn("docs_has_install", ev_with.docs_signals_applied)
        self.assertIn("docs_has_usage", ev_with.docs_signals_applied)

    def test_readme_already_has_install_usage(self):
        readme = (
            "# MyLib\n"
            "## Installation\n"
            "pip install mylib\n"
            "## Usage\n"
            "```python\nimport mylib\n```\n"
            "1. step\n2. step\n3. step\n"
        )
        ev = evaluate_readme(readme, docs_text=self.RICH_DOCS)

        # README already covers install + usage + steps; those docs signals
        # should NOT appear in applied list.
        self.assertNotIn("docs_has_install", ev.docs_signals_applied)
        self.assertNotIn("docs_has_usage", ev.docs_signals_applied)
        self.assertNotIn("docs_step_lines", ev.docs_signals_applied)

    def test_html_docs_no_false_positives(self):
        html_docs = (
            "<html><head><title>MyLib</title></head><body>\n"
            "<nav>Home | About | Contact</nav>\n"
            "<p>Welcome to MyLib. Learn more about our team.</p>\n"
            "</body></html>\n"
        )
        ev_without = evaluate_readme(self.THIN_README)
        ev_with = evaluate_readme(self.THIN_README, docs_text=html_docs)

        eq_before = ev_without.scores["execution_quality"].score
        eq_after = ev_with.scores["execution_quality"].score

        # Generic HTML has no install/usage/code cues; no score change.
        self.assertEqual(eq_before, eq_after)
        self.assertEqual(ev_with.docs_signals_applied, [])

    def test_no_docs_text_means_empty_applied(self):
        ev = evaluate_readme(self.THIN_README)
        self.assertEqual(ev.docs_signals_applied, [])


class TestScoringCeilings(unittest.TestCase):
    """High-band why messages must be reachable."""

    def test_problem_clarity_high_band(self):
        readme = (
            "# MyLib\n"
            "TL;DR: a fast tool.\n"
            "What it is: a thing. Why it matters.\n"
            + "\n".join(f"- bullet {i}" for i in range(7))
        )
        ev = evaluate_readme(readme)
        pc = ev.scores["problem_clarity"]
        self.assertGreaterEqual(pc.score, 7.0)
        self.assertIn("quickly answers", pc.why)

    def test_novelty_high_band(self):
        readme = (
            "# MyLib\n"
            "A new, unique, opinionated agent workflow tool.\n"
            "![demo](https://example.com/demo.png)\n"
        )
        ev = evaluate_readme(readme)
        nt = ev.scores["novelty_trend_fit"]
        self.assertGreaterEqual(nt.score, 6.5)
        self.assertIn("distinct angle", nt.why)


if __name__ == "__main__":
    unittest.main()
