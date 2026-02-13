"""
Prompt templates (placeholder)

Status: v0.1 (research-first)

This project may optionally use LLMs in v0.2+ to:
- extract structured signals from README text
- generate short scoring rationales that remain grounded in visible evidence

Important:
- The prompts should push the model to *justify with quotes or concrete cues*,
  not to 'hallucinate' why a repo is good.
"""

PROMPT_README_TO_SIGNALS = """
You are reading a GitHub README. Extract observable signals only.
Do NOT guess unknown information.

Return JSON with:
- problem_clarity: short notes
- novelty_trend_fit: short notes
- distribution_potential: short notes
- execution_quality: short notes

For each field:
- include 2–5 bullet signals
- each signal must reference a specific phrase/section that exists in the README
"""

PROMPT_SIGNALS_TO_SCORES = """
Given extracted signals for the four dimensions, assign a 0–10 score for each.
Rules:
- be conservative if evidence is weak
- keep reasons short (1–2 sentences per dimension)
- do not invent evidence
Return JSON: {dimension: {score: float, reason: str}}
"""
