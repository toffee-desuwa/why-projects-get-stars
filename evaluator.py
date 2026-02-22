from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class DimensionScore:
    score: float
    why: str  # one sentence, reader-facing


@dataclass(frozen=True)
class EvalResult:
    scores: Dict[str, DimensionScore]
    signals: Dict[str, int]  # debug: observed cues / counts
    docs_signals_applied: list  # docs signals that actually changed scoring (not just detected)


def _count(pattern: str, text: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text, flags))


def _has(pattern: str, text: str, flags: int = 0) -> bool:
    return re.search(pattern, text, flags) is not None


def _count_fenced_code_blocks(text: str) -> int:
    """
    Rough count of fenced code blocks.

    Why this exists:
    - many READMEs use ``` fences, some use ~~~ fences
    - we don't need perfect parsing; we just want a "does it show runnable stuff?" signal
    """
    ticks = _count(r"```", text)
    tildes = _count(r"~~~", text)
    return (ticks // 2) + (tildes // 2)


def evaluate_readme(readme_text: str, *, docs_text: str | None = None) -> EvalResult:
    """
    Heuristic v0.3 evaluator (README-first, optional docs supplement).

    What we're trying to measure:
    - "star-worthiness signals" as they appear to a reader skimming the README
    - not code quality, not algorithmic difficulty

    This is intentionally conservative:
    - if a README doesn't *show* evidence, we don't give it credit

    docs_text: when --follow-docs is used, the fetched docs page text.
    Signals from docs are tracked separately (docs_* prefix) for traceability.
    Only execution_quality uses docs evidence — the other dimensions stay
    README-only, since they measure first-screen impression.
    """
    t = readme_text

    # --- Observable signals (debug-friendly) ---
    has_title = _has(r"(?m)^\s*#\s+\S+", t)

    # TL;DR / one-line / summary-ish cues
    has_tldr = _has(r"(?i)\b(tl;dr|tldr|one[- ]line|summary|in short)\b", t)

    # "Install/Usage" headers are common, but plenty of repos don't use those exact words.
    # We try to catch onboarding sections that still function as install/usage.
    has_install = _has(
        r"(?i)\b(install|installation|get(ting)? started|setup|set up|requirements|prerequisite|dependencies)\b",
        t,
    )
    has_usage = _has(
        r"(?i)\b(usage|quick\s*start|quickstart|examples?|how to|run|try it|getting\s+started|cli|commands?)\b",
        t,
    )

    # Demo-ish cues: explicit words OR any markdown image
    has_demo = (
        _has(r"(?i)\b(demo|screenshot|gif|video|preview)\b", t)
        or _has(r"!\[.*?\]\(.*?\)", t)
    )
    
    has_badges = _has(r"!\[.*?\]\(https?://img\.shields\.io/.*?\)", t)

    code_blocks = _count_fenced_code_blocks(t)

    # Steps: "1." / "1)" / "Step 1:" / "- Step:"
    step_lines = _count(r"(?im)^\s*(\d+\.\s+|\d+\)\s+|step\s*\d+\s*:)", t)

    # Bullets: -, *, or unicode bullet
    bullets = _count(r"(?m)^\s*([-*]|•)\s+", t)

    has_docs_link = _has(r"(?i)\b(docs|documentation)\b", t) and _has(r"https?://\S+", t)
    
    docs_is_primary_onboarding = bool(has_docs_link and (not has_install) and 
    (not has_usage) and code_blocks == 0 and step_lines == 0)


    # Also detect "one-command" onboarding (npx, curl | bash, pip install, etc.)
    has_one_command = _has(
        r"(?i)\b(npx\s+\S+|pip\s+install\s+\S+|curl\s+.+\|\s*(sh|bash)|docker\s+run\s+\S+)\b",
        t,
    )

    signals = {
        "has_title": int(has_title),
        "has_tldr": int(has_tldr),
        "has_install": int(has_install),
        "has_usage": int(has_usage),
        "has_demo": int(has_demo),
        "has_badges": int(has_badges),
        "code_blocks": int(code_blocks),
        "step_lines": int(step_lines),
        "bullets": int(bullets),
        "has_one_command": int(has_one_command),
        "has_docs_link": int(has_docs_link),
        "docs_is_primary_onboarding": int(docs_is_primary_onboarding),
    }

    # --- Supplemental docs signals (only when --follow-docs provides text) ---
    # Tracked separately so score changes are traceable to their source.
    docs_has_install = False
    docs_has_usage = False
    docs_code_blocks = 0
    docs_step_lines = 0
    docs_has_one_command = False

    if docs_text:
        docs_has_install = _has(
            r"(?i)\b(install|installation|get(ting)? started|setup|set up|requirements|prerequisite|dependencies)\b",
            docs_text,
        )
        docs_has_usage = _has(
            r"(?i)\b(usage|quick\s*start|quickstart|examples?|how to|run|try it|getting\s+started|cli|commands?)\b",
            docs_text,
        )
        docs_code_blocks = _count_fenced_code_blocks(docs_text)
        docs_step_lines = _count(
            r"(?im)^\s*(\d+\.\s+|\d+\)\s+|step\s*\d+\s*:)", docs_text
        )
        docs_has_one_command = _has(
            r"(?i)\b(npx\s+\S+|pip\s+install\s+\S+|curl\s+.+\|\s*(sh|bash)|docker\s+run\s+\S+)\b",
            docs_text,
        )

    signals["docs_has_install"] = int(docs_has_install)
    signals["docs_has_usage"] = int(docs_has_usage)
    signals["docs_code_blocks"] = int(docs_code_blocks)
    signals["docs_step_lines"] = int(docs_step_lines)
    signals["docs_has_one_command"] = int(docs_has_one_command)

    # --- Dimension 1: problem_clarity ---
    pc = 3.0
    if has_title:
        pc += 1.0
    if has_tldr:
        pc += 1.5
    if _has(r"(?i)\b(what\s+it\s+is|what\s+this\s+is|why)\b", t):
        pc += 1.0
    if bullets >= 6:
        pc += 0.5
    pc = min(10.0, pc)

    # ceiling is 7.0 (3 base + 1 title + 1.5 tldr + 1 what/why + 0.5 bullets)
    if pc >= 7:
        pc_why = "It quickly answers what it is and who it’s for with low ambiguity."
    elif pc <= 5:
        pc_why = "It’s not obvious who it’s for or what problem it solves from the first screen."
    else:
        pc_why = "It states what it is early, but the target user / problem framing could be sharper."

    # --- Dimension 2: novelty_trend_fit ---
    nt = 4.0
    if _has(r"(?i)\b(new|novel|first|unique|different|opinionated)\b", t):
        nt += 1.0
    if _has(r"(?i)\b(agent|workflow|automation|benchmark|copy[- ]paste)\b", t):
        nt += 1.0
    if has_demo:
        nt += 0.5
    nt = min(10.0, nt)

    # ceiling is 6.5 (4 base + 1 novelty words + 1 trend words + 0.5 demo)
    if nt >= 6.5:
        nt_why = "It has a distinct angle that matches current developer attention and trends."
    elif nt <= 5:
        nt_why = "It reads like a standard library without a strong ‘why now / why different’ hook."
    else:
        nt_why = "It has a recognizable angle, but the differentiation claim isn’t strongly demonstrated yet."

    # --- Dimension 3: distribution_potential ---
    dp = 3.5
    if has_demo:
        dp += 2.0
    if has_badges:
        dp += 0.5
    if (has_usage or has_one_command) and (step_lines >= 2 or code_blocks >= 1):
        dp += 1.5
    if _has(r"(?i)\b(copy[- ]paste|3\s*minutes|one\s+command|zero\s+config)\b", t):
        dp += 1.0
    dp = min(10.0, dp)

    if dp >= 8:
        dp_why = "It lowers sharing friction with clear payoff, visuals, and fast first success."
    elif dp <= 5:
        dp_why = "There’s little reason to share it: no visible payoff, demo, or quick success path."
    else:
        dp_why = "It’s shareable if people can ‘see the payoff’ quickly."

    # --- Dimension 4: execution_quality (README-first onboarding quality) ---
    eq = 3.0
    if has_install or has_one_command:
        eq += 2.0
    if has_usage:
        eq += 2.0
    if has_docs_link:
        eq += 1.0
    if docs_is_primary_onboarding:
        eq += 0.5  # acknowledge docs-first projects (still README-first scorer)

    if step_lines >= 3:
        eq += 1.0
    if code_blocks >= 2:
        eq += 0.5
    if _has(r"(?i)\b(requirements|dependencies|python\s+>=|node\s+>=)\b", t):
        eq += 0.5

    # Docs supplement: only count cues the README itself didn't already provide.
    # Each docs signal is capped so it can't dominate the score.
    # We track which signals actually changed eq (not just detected) for traceability.
    _applied = []
    if docs_text:
        if docs_has_install and not (has_install or has_one_command):
            eq += 1.0
            _applied.append("docs_has_install")
        if docs_has_usage and not has_usage:
            eq += 1.0
            _applied.append("docs_has_usage")
        if docs_step_lines >= 3 and step_lines < 3:
            eq += 0.5
            _applied.append("docs_step_lines")
        # Code blocks are an independent onboarding signal (runnable examples),
        # so they can add a small bump even when the README already has
        # install/usage sections — those sections might lack concrete snippets.
        if docs_code_blocks >= 2 and code_blocks < 2:
            eq += 0.5
            _applied.append("docs_code_blocks")

    eq = min(10.0, eq)

    if eq >= 8:
        eq_why = "It gives a low-friction path to first success (install → run → see output)."
    elif eq <= 5:
        eq_why = "Even if the code works, the onboarding path feels under-specified."
    else:
        eq_why = "It’s runnable with some effort, but the first-success path could be more explicit."

    scores = {
        "problem_clarity": DimensionScore(pc, pc_why),
        "novelty_trend_fit": DimensionScore(nt, nt_why),
        "distribution_potential": DimensionScore(dp, dp_why),
        "execution_quality": DimensionScore(eq, eq_why),
    }
    return EvalResult(scores=scores, signals=signals, docs_signals_applied=_applied)
