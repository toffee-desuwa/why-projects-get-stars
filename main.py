"""
why-projects-get-stars — entry point

Status: v0.3 (README-first heuristic scorer + optional docs-follow mode)

CLI: python main.py score --repo owner/name [--ref main] [--format text|json]
"""

from __future__ import annotations

import argparse
import json

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="why-projects-get-stars",
        description="Score a GitHub repo's star-worthiness signals (v0.3).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser(
        "score",
        help="Score a GitHub repo (README-first).",
    )
    score.add_argument(
        "--repo",
        required=True,
        help='GitHub repo in the form "owner/name", e.g. "shadcn-ui/ui".',
    )
    score.add_argument(
        "--ref",
        default="main",
        help='Branch/tag/sha to read from (default: "main").',
    )
    score.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help='Output format (default: "text").',
    )
    score.add_argument(
        "--follow-docs",
        action="store_true",
        default=False,
        help="Follow the first docs link in the README and use it as supplemental evidence.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "score":
        from github_fetcher import fetch_readme, extract_docs_url, fetch_docs_page
        from evaluator import evaluate_readme
        from scoring_schema import calculate_overall_score

        res = fetch_readme(args.repo, args.ref)

        # --follow-docs: one-hop fetch of the first docs URL found in README.
        docs_followed_url = None
        docs_fetch_ok = 0
        docs_text = None

        if args.follow_docs:
            docs_followed_url = extract_docs_url(res.text)
            if docs_followed_url:
                docs_text = fetch_docs_page(docs_followed_url)
                docs_fetch_ok = 1 if docs_text else 0

        ev = evaluate_readme(res.text, docs_text=docs_text)

        numeric_scores = {k: v.score for k, v in ev.scores.items()}
        overall = calculate_overall_score(numeric_scores)

        # Fixed dimension order — must stay stable across versions.
        _DIM_ORDER = [
            "problem_clarity",
            "novelty_trend_fit",
            "distribution_potential",
            "execution_quality",
        ]

        scores_ordered = {
            dim: {"score": ev.scores[dim].score, "why": ev.scores[dim].why}
            for dim in _DIM_ORDER
        }

        # Which docs signals actually contributed to scoring?
        _DOCS_SIGNAL_KEYS = [
            "docs_has_install", "docs_has_usage",
            "docs_code_blocks", "docs_step_lines", "docs_has_one_command",
        ]
        docs_signals_used = [
            k for k in _DOCS_SIGNAL_KEYS if ev.signals.get(k, 0)
        ]

        # Top-level key order: version, repo, readme, source, overall, scores, signals,
        # then docs debug fields.
        payload = {
            "version": "0.3.0",
            "repo": f"{args.repo}@{args.ref}",
            "readme": res.filename,
            "source": res.source_url,
            "overall": overall,
            "scores": scores_ordered,
            "signals": dict(sorted(ev.signals.items())),
            "docs_followed_url": docs_followed_url,
            "docs_fetch_ok": docs_fetch_ok,
            "docs_signals_used": docs_signals_used,
        }

        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        # text output (default)
        print(f"Repo: {args.repo}@{args.ref}")
        print(f"README: {res.filename}")
        print(f"Source: {res.source_url}")
        print()
        print(f"Overall (0-10): {overall}")
        print()

        for dim in _DIM_ORDER:
            ds = ev.scores[dim]
            print(f"- {dim}: {ds.score}/10")
            print(f"  why: {ds.why}")

        print()
        print("Debug signals:", dict(sorted(ev.signals.items())))
        return



if __name__ == "__main__":
    main()
