"""
Evaluator (placeholder)

Status: v0.1 (research-first)

In v0.2, this module will turn the framework into something executable:
- input: a repo README (text) + optional metadata
- output: 0–10 overall score + per-dimension scores + short reasons

Why a separate module?
- Keep scoring logic testable and independent from fetching/CLI glue.
"""

from typing import Dict


def evaluate_repo(readme_text: str) -> Dict[str, float]:
    """
    Evaluate a repo based on README text and return dimension scores.

    v0.1: not implemented.
    v0.2 plan (rough):
    - extract signals (problem clarity, narrative, onboarding friction, etc.)
    - map signals -> 4 dimension scores
    - return {dimension: score}
    """
    raise NotImplementedError(
        "v0.2 will implement README-based evaluation. See README.md for the framework."
    )
