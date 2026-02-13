"""
GitHub fetcher (placeholder)

Status: v0.1 (research-first)

In v0.2, this module will fetch README content for a given GitHub repo,
so the scorer can run on real inputs without manual copy-paste.

Design notes:
- Keep this small and dependency-light.
- Prefer GitHub raw content endpoints or API, but allow offline mode too.

v0.1 intentionally does nothing to avoid implying functionality that isn't shipped yet.
"""

from typing import Optional


def fetch_readme(owner: str, repo: str, branch: str = "main") -> Optional[str]:
    """
    Fetch README.md as plain text.

    Returns:
        README content if available, otherwise None.

    v0.2 will implement:
    - URL construction and HTTP fetching
    - fallback branches (main/master)
    - minimal error handling
    """
    raise NotImplementedError("v0.2 will add fetching. For now, use local README text.")
