"""
why-projects-get-stars — entry point

Status: v0.1 (research-first)

This repo is currently centered on:
- a scoring schema (`scoring_schema.py`)
- public case-study notes (`docs/`)
- a README that explains the working hypothesis and framework

The CLI/tooling will land in v0.2.
This file exists as a clear, honest placeholder for that next step.
"""

from __future__ import annotations

import argparse
import json

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="why-projects-get-stars",
        description="Score a GitHub repo's star-worthiness signals (v0.2 WIP).",
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


    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "score":
        from github_fetcher import fetch_readme
        from evaluator import evaluate_readme
        from scoring_schema import calculate_overall_score

        res = fetch_readme(args.repo, args.ref)
        ev = evaluate_readme(res.text)

        numeric_scores = {k: v.score for k, v in ev.scores.items()}
        overall = calculate_overall_score(numeric_scores)

        payload = {
            "repo": f"{args.repo}@{args.ref}",
            "readme": res.filename,
            "source": res.source_url,
            "overall": overall,
            "scores": {
                dim: {"score": ds.score, "why": ds.why}
                for dim, ds in ev.scores.items()
            },
            "signals": ev.signals,
        }

        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        # text output (default)
        print(f"Repo: {args.repo}@{args.ref}")
        print(f"README: {res.filename}")
        print(f"Source: {res.source_url}")
        print()
        print(f"Overall (0–10): {overall}")
        print()

        for dim, ds in ev.scores.items():
            print(f"- {dim}: {ds.score}/10")
            print(f"  why: {ds.why}")

        print()
        print("Debug signals:", ev.signals)
        return



if __name__ == "__main__":
    main()
