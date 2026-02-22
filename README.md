# why-projects-get-stars

A research-first framework for explaining (and scoring) why some GitHub repos earn stars — beyond pure code difficulty.
Status: **v0.3** (README-first heuristic scorer + optional docs-follow mode).
Tooling: `python main.py score --repo owner/name [--format text|json] [--follow-docs]`

---
## Quickstart (v0.3)

v0.3 is intentionally lightweight: **stdlib-only** (no third-party deps).

### Score a repo (text)

```bash
python main.py score --repo shadcn-ui/ui
```

### Score a repo (json)

```bash
python main.py score --repo shadcn-ui/ui --format json
```

### Score with docs follow (optional)

```bash
python main.py score --repo shadcn-ui/ui --follow-docs --format json
```

`--follow-docs` follows the first docs link found in the README (one hop, short timeout) and looks for onboarding cues — install steps, usage examples, code blocks. It will not override a strong README score; it only fills gaps the README left open.


## Why this project exists

This project started from a question I kept returning to:

Why do some GitHub repositories accumulate massive numbers of stars, while others — with equally serious technical effort behind them — remain relatively unseen?

My current conclusion is that stars are not simply a natural byproduct of technical difficulty.

In my view, they are more closely tied to whether a project forms a coherent logical loop, presents a clear narrative structure, and offers a distinct cognitive angle in an increasingly homogeneous landscape.

This is not a claim of superiority, nor an attempt to rank projects by taste. It is an effort to understand the underlying mechanism behind visibility and attention.

## Observations

While collecting examples for this project, one pattern kept showing up: a lot of the “star decision” seems to happen **before** anyone runs the code.

Across very different projects (UI components, a deep learning library, a JAX API), the first screen of the README often does the same three jobs:

1. **Identity positioning** — *Is this for me?*  
   In one breath: what it is, who it’s for, and what problem it solves.

2. **Feels runnable** — *Can I start without pain?*  
   A short install path, a CLI, a minimal snippet, or a “run it in Colab” option makes you feel: *ok, I can try this.*

3. **Show the destination** — *What will I get if it works?*  
   Screenshots, demos, or a tiny usage example act like a preview of the outcome.

This framing matters because stars are a public signal of attention. If stars were mainly about technical difficulty, the top of GitHub would look like an ICPC problemset leaderboard — but it doesn’t. Many highly-starred repos win early because they communicate a clear mental model fast, and earn the right to be tried.

Code quality still matters — just often **later** in the funnel.

---
> Scope note (v0.3): this tool is **README-first** by default. Docs-first repos (thin README, heavy external docs) may score lower unless you pass `--follow-docs`, which follows one docs link and extracts onboarding cues. Even then, it only supplements `execution_quality` — the other three dimensions stay README-only, since they measure first-screen impression.
## Framework

I’m treating a “star decision” as something that often happens in the *reading phase*.  
So the framework below focuses on what a repo communicates **before** you run any code.

### Scoring (0–10)

You score a repo on four dimensions (0–10 each), then compute a weighted overall score.

- 0 = basically absent
- 5 = present but weak / unclear
- 10 = extremely clear and convincing

> Important: this is not meant to judge “code quality”.  
> It’s meant to explain why a repo earns attention early.

---

### 1) Problem clarity (0–10)

**Question:** Do I understand what this is, who it’s for, and what problem it solves — in one breath?

**Signals:**
- A sharp one-liner that actually tells me something
- A clear target user (“for X who want Y”)
- The repo name + README headline match what it does

**Common failure modes:**
- Vague positioning (“A modern framework for everything”)
- Assumes I already know the context
- Says *what it is*, but not *why I should care*

---

### 2) Novelty / trend fit (0–10)

**Question:** Does this feel like a distinct angle *right now*, or another “same thing but rebranded”?

**Signals:**
- A non-obvious mental model (a new way to frame the problem)
- Clear differentiation from alternatives (“why this over X”)
- Timely relevance (fits what people are actively looking for)

**Common failure modes:**
- Pure clone / template with no twist
- Overclaims without concrete proof
- “Trend-chasing” with no real substance

---

### 3) Distribution potential (0–10)

**Question:** Does it have strong “share triggers” — something that makes people want to send it to others?

**Signals:**
- A demo screenshot / GIF / before-after result
- A simple “wow moment” that is easy to show
- The README has a story arc (why → what → how → proof)

**Common failure modes:**
- No visuals, no examples, no payoff
- Only API docs / functions
- Too hard to explain in 1 sentence to a friend

---

### 4) Execution quality (0–10)

**Question:** Even if I haven’t read the whole codebase, does it *feel* trustworthy and runnable?

**Signals:**
- Low-friction onboarding (3-step install/run, or Colab)
- Clean structure, clear usage example
- Reasonable docs for the “happy path”

**Common failure modes:**
- “Works on my machine” vibes
- Missing quickstart
- Setup is painful with no guidance

---

### Weights

Right now I’m using these weights (they’re adjustable, not sacred):

- problem_clarity: 0.30  
- novelty_trend_fit: 0.25  
- distribution_potential: 0.25  
- execution_quality: 0.20  

The point isn’t the exact numbers — it’s making the trade-offs explicit.

### Example scoring (v1)

Below are two quick examples to show how the framework is used in practice.  
These are not “final truths” — they’re reproducible judgments based on what a repo communicates in the reading phase.

#### Example 1 — elegy (overall: 5.4 / 10)

- problem_clarity: **7**  
  Clear on what it is (“high-level API for deep learning in JAX”), but “who it’s for / why this matters” is not fully explicit.
- novelty_trend_fit: **6**  
  The value is “Keras-like ergonomics for the JAX ecosystem,” but it doesn’t redefine the problem.
- distribution_potential: **4**  
  Weak story arc and little/no demo payoff; low share-trigger density.
- execution_quality: **4**  
  JAX ecosystem setup is platform-specific and adds real friction (especially for beginners), even if the API itself is straightforward.

> Weighted overall: 7×0.30 + 6×0.25 + 4×0.25 + 4×0.20 = **5.4**

#### Example 2 — shadcn/ui (overall: 7.8 / 10)

- problem_clarity: **8**  
  Clear positioning for React developers: accessible, customizable components with a copy-paste workflow.
- novelty_trend_fit: **7**  
  The copy-paste distribution model is a strong differentiator, though the underlying stack fits an increasingly common “headless primitives + utility CSS” pattern.
- distribution_potential: **8**  
  High share-trigger density (visual demos + a simple mental model), but the audience is primarily within the React/Tailwind ecosystem rather than general users.
- execution_quality: **8**  
  The CLI path is streamlined, but it assumes a React + Tailwind setup, which is friction for projects outside that stack.

> Weighted overall: 8×0.30 + 7×0.25 + 8×0.25 + 8×0.20 = **7.8**

---

## Implications

If my observations hold (even roughly), then “getting stars” is less about writing the most impressive code
and more about reducing uncertainty for the reader.

A few practical implications:

- **A star is often a bet on future usefulness.**  
  People star when a repo feels *worth keeping in their mental bookmarks* — even before they use it.

- **Clarity beats complexity.**  
  A repo that answers “what is this / who is this for / how do I try it in 3 minutes” usually wins against one
  that only demonstrates technical depth.

- **Narrative is a UX layer.**  
  A good README is not marketing copy; it’s a guided onboarding path that makes the repo feel safe to adopt.

- **Distribution is part of the product.**  
  Demos, screenshots, copy-paste snippets, and “first success in 1–3 steps” are not decoration — they are the core funnel.

- **Treat the README like a contract.**  
  README quality has outsized leverage, but it’s easy to over-optimize the “first-screen” and under-deliver in the code.
  When the promise doesn’t match reality (reproducibility, clarity, or usefulness), the trust cost shows up later — in drop-offs,
  critical issues, or negative word-of-mouth.

What I’m doing next:

- Collect more case studies (high / mid / low star repos), and keep the notes public under `docs/`.
- Turn the framework into a small scoring tool (v0.2): given a repo README, output a 0–10 score + reasons.
- Add an optional docs-follow mode (follow 1-step “Docs / Getting Started” link) to better handle docs-first repos like shadcn/ui.