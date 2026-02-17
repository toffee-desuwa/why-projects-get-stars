from __future__ import annotations

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
        raise ValueError('repo must be "owner/name", got: {repo!r}')

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
