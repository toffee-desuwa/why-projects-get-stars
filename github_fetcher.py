from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class ReadmeFetchResult:
    repo: str
    ref: str
    filename: str
    text: str
    source_url: str


README_CANDIDATES = ("README.md", "README.MD", "README.rst", "README.txt", "README")


def _http_get_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "why-projects-get-stars/0.2 (README fetcher)",
            "Accept": "text/plain, text/markdown, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def fetch_readme(repo: str, ref: str = "main") -> ReadmeFetchResult:
    """
    Fetch README from GitHub via raw.githubusercontent.com.

    Why raw?
    - no extra dependency (requests)
    - no token required
    - simple and predictable

    Raises ValueError if README not found.
    """
    if "/" not in repo:
        raise ValueError(f'repo must be "owner/name", got: {repo!r}')

    owner, name = repo.split("/", 1)

    last_err: Exception | None = None
    for filename in README_CANDIDATES:
        url = f"https://raw.githubusercontent.com/{owner}/{name}/{ref}/{filename}"
        try:
            text = _http_get_text(url)
            # raw.githubusercontent returns a 404 html page sometimes; guard it.
            if "404: Not Found" in text[:200]:
                raise urllib.error.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)
            return ReadmeFetchResult(repo=repo, ref=ref, filename=filename, text=text, source_url=url)
        except Exception as e:
            last_err = e
            continue

    raise ValueError(f"README not found for {repo}@{ref}. Last error: {last_err}")


def extract_docs_url(readme_text: str) -> str | None:
    """
    Find the first docs/documentation URL in a README.

    Strategy (in order):
    1. Markdown link whose text mentions docs/documentation/getting started
    2. Any URL whose path contains /docs or /documentation
    3. Bare URL on the same line as "docs"/"documentation" (either order)

    Returns the first match or None. Intentionally conservative —
    we'd rather miss a link than follow the wrong one.
    """
    # 1) Markdown links with docs-related anchor text
    md_link = re.search(
        r"\[(?:[^\]]*(?:docs|documentation|getting\s+started)[^\]]*)\]\((https?://[^\s)]+)\)",
        readme_text,
        re.IGNORECASE,
    )
    if md_link:
        return md_link.group(1)

    # 2) Any URL whose path contains /docs or /documentation
    path_match = re.search(
        r"(https?://\S+/(?:docs|documentation)\b\S*)",
        readme_text,
        re.IGNORECASE,
    )
    if path_match:
        return path_match.group(1)

    # 3) Bare URL on a line that also mentions docs/documentation
    for line in readme_text.splitlines():
        if re.search(r"(?i)\b(?:docs|documentation)\b", line):
            url_match = re.search(r"(https?://\S+)", line)
            if url_match:
                return url_match.group(1)

    return None


def fetch_docs_page(url: str, timeout: int = 10) -> str | None:
    """
    Fetch a single docs page. Returns text or None on any failure.

    This is not a crawler. One URL, one attempt, short timeout.
    """
    try:
        return _http_get_text(url, timeout=timeout)
    except Exception:
        return None
