"""Filesystem locations and public URLs for the course website."""
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def public_path(url):
    """Keep existing page and notebook URLs working after moving the website."""
    parts = unquote(urlsplit(url).path).replace("\\", "/").split("/")
    parts = [part for part in parts if part]
    if parts and parts[0] == "site":
        parts = parts[1:]
    if any(part.startswith(".") or ":" in part or "\x00" in part for part in parts):
        return None
    base = ROOT if parts and parts[0] == "code" else SITE
    target = base.joinpath(*parts).resolve()
    if not target.is_relative_to(base.resolve()):
        return None
    return target
