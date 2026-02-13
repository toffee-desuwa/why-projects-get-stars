from typing import Dict

# Weights for each evaluation dimension.
# They sum to 1.0 so we can treat them as direct weighting factors.
# The exact numbers are somewhat subjective for now — if we want to tune the schema later,
# this is the single place to do it.
WEIGHTS = {
    "problem_clarity": 0.30,
    "novelty_trend_fit": 0.25,
    "distribution_potential": 0.25,
    "execution_quality": 0.20,
}


def validate_scores(scores: Dict[str, float]) -> None:
    """
    Sanity checks before computing the weighted score:

    - All dimensions defined in the schema must be present.
    - Each individual score must be in the range [0, 10].

    We intentionally do not auto-correct or clamp values here.
    The goal is to make the scorer responsible for their inputs.
    Missing dimensions or out-of-range values fail fast.
    """
    for dimension in WEIGHTS.keys():
        if dimension not in scores:
            raise ValueError(f"Missing score for dimension: {dimension}")

        score = scores[dimension]
        if not (0 <= score <= 10):
            raise ValueError(
                f"Score for {dimension} must be between 0 and 10. Got: {score}"
            )


def calculate_overall_score(scores: Dict[str, float]) -> float:
    """
    Compute the weighted overall score for a repo.

    Validation is performed first; then each dimension score
    is multiplied by its corresponding weight.
    The final result is rounded to two decimal places.
    """
    validate_scores(scores)

    weighted_sum = 0.0
    for dimension, weight in WEIGHTS.items():
        weighted_sum += scores[dimension] * weight

    return round(weighted_sum, 2)
