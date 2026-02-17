"""
Prompt templates (v0.1 placeholder -> v0.2-ready)

Status: v0.1 (research-first)

This project may optionally use LLMs in v0.2+ to:
- extract structured, observable signals from README text
- generate short scoring rationales grounded in visible evidence

Design goals:
- stay evidence-based (no hallucination)
- keep outputs compact and comparable across repos
"""

# ---- README -> signals ----
PROMPT_README_TO_SIGNALS = """
You are reading a GitHub README. Extract OBSERVABLE signals only.
Do NOT guess unknown information. Do NOT infer unmentioned features.

Return JSON with exactly these keys:
- problem_clarity
- novelty_trend_fit
- distribution_potential
- execution_quality

For each key:
- output 2–5 bullets
- each bullet MUST include:
  - cue: a short description of the signal
  - quote: a direct quote from the README (6–20 words)
  - where: where it appears (e.g., "top section", "install", "usage", "example", "demo", "faq")
Rules:
- If evidence is missing, output an empty list for that key.
- Quotes must be copied verbatim from the README text provided.
"""

# ---- signals -> scores ----
PROMPT_SIGNALS_TO_SCORES = """
Given extracted signals for the four dimensions, assign a 0–10 score for each.

Important:
- Be conservative when evidence is weak.
- Do not invent evidence. Reasons must be backed by the given signals (and their quotes).

Rubric anchors (quick):
problem_clarity:
- 0: unclear what it is / who it's for
- 5: somewhat clear but boundaries are fuzzy
- 10: instantly clear what/for whom/why

novelty_trend_fit:
- 0: generic clone / no distinct angle
- 5: some angle but weak differentiation
- 10: clear hook + timely + demonstrably different

distribution_potential:
- 0: nothing shareable (no payoff/hook)
- 5: somewhat shareable but payoff unclear
- 10: strong hook + visible payoff + low sharing friction

execution_quality (README-first onboarding):
- 0: cannot tell how to try it
- 5: basic steps exist but incomplete/ambiguous
- 10: clear steps + expected outcome + low-friction first success

Output JSON in this exact shape:
{
  "problem_clarity": {"score": <0-10 number>, "reason": "<1 sentence>"},
  "novelty_trend_fit": {"score": <0-10 number>, "reason": "<1 sentence>"},
  "distribution_potential": {"score": <0-10 number>, "reason": "<1 sentence>"},
  "execution_quality": {"score": <0-10 number>, "reason": "<1 sentence>"}
}

Constraints:
- reason must be <= 22 words
- reason must reference at least one concrete cue from the signals
"""
