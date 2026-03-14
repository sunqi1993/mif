"""Chrome bookmarks plugin — search Google Chrome bookmarks and open the selected URL.

Reads the Chrome Bookmarks JSON file (bookmark_bar, other, synced), flattens
all URLs, and filters by query on title and URL. Sorting combines fuzzy match
score with click-through rate (CTR) stored in the user config directory.

Config:
  bookmarks_path  — override path (default: auto-detect by OS)
  profile         — Chrome profile folder name (default: "Default")
  max_results     — max results to return (default: 15)
  click_weight    — weight for CTR in [0,1]; rest is fuzzy score (default: 0.3)

Click-through data is stored in:
  <config_dir>/chrome_bookmarks_clicks.json   (same priority as plugin_configs.json)
Format: {"url": count, ...}. Each time a bookmark is opened, its count is incremented.
"""

from __future__ import annotations

import json
import logging
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mif.plugins.base import BasePlugin, ConfigOption, PluginMeta, PluginResult

logger = logging.getLogger("AlfredPy.ChromeBookmarks")

# ── Click-through data (user config dir) ──────────────────────────────────────

CLICKS_FILENAME = "chrome_bookmarks_clicks.json"


def _clicks_path() -> Path:
    from mif.config import effective_config_dir
    return effective_config_dir() / CLICKS_FILENAME


def _load_clicks() -> Dict[str, int]:
    """Load url -> click_count from user/project config dir."""
    path = _clicks_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items() if isinstance(v, (int, float))}
    except Exception as e:
        logger.warning(f"Failed to load click stats from {path}: {e}")
        return {}


def _save_clicks(clicks: Dict[str, int]) -> None:
    path = _clicks_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clicks, f, indent=2, ensure_ascii=False)


def _record_click(url: str) -> None:
    clicks = _load_clicks()
    clicks[url] = clicks.get(url, 0) + 1
    _save_clicks(clicks)

# ── Default bookmarks path by OS ───────────────────────────────────────────────

def _default_bookmarks_dir() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library/Application Support/Google/Chrome"
    if sys.platform == "win32":
        local = Path.home() / "AppData/Local"
        return local / "Google/Chrome/User Data"
    return home / ".config/google-chrome"


def _get_bookmarks_path(profile: str, custom_path: Optional[str]) -> Optional[Path]:
    """Resolve the Bookmarks file path. Returns None if not found."""
    if custom_path:
        p = Path(custom_path).expanduser().resolve()
        if p.is_file():
            return p
        if p.is_dir():
            p = p / "Bookmarks"
            if p.exists():
                return p
        return None

    base = _default_bookmarks_dir()
    candidates = [
        base / profile / "Bookmarks",
        base / "Default" / "Bookmarks",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


# ── Flatten Chrome JSON ───────────────────────────────────────────────────────

def _collect_urls(node: dict, out: List[Tuple[str, str]]) -> None:
    """Recursively collect (name, url) from Chrome bookmarks JSON."""
    if node.get("type") == "url":
        name = node.get("name") or ""
        url = node.get("url") or ""
        if name and url:
            out.append((name, url))
        return

    for child in node.get("children") or []:
        _collect_urls(child, out)


def _load_bookmarks(path: Path) -> List[Tuple[str, str]]:
    """Load and flatten bookmarks from a Chrome Bookmarks file."""
    out: List[Tuple[str, str]] = []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read bookmarks file {path}: {e}")
        return out

    roots = data.get("roots") or {}
    for key in ("bookmark_bar", "other", "synced"):
        if key in roots and isinstance(roots[key], dict):
            _collect_urls(roots[key], out)

    return out


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score(title: str, url: str, query: str) -> float:
    q = query.lower().strip()
    if not q:
        return 1.0
    t = title.lower()
    u = url.lower()
    if q in t:
        return 1.0
    if q in u:
        return 0.85
    try:
        from thefuzz import fuzz
        ts = fuzz.partial_ratio(q, t) / 100
        us = fuzz.partial_ratio(q, u) / 100
        return max(ts, us * 0.9)
    except ImportError:
        return 0.5 if q in t or q in u else 0.0


# ── Plugin ────────────────────────────────────────────────────────────────────

class ChromeBookmarksPlugin(BasePlugin):
    """Search Chrome bookmarks and open the selected link."""

    def __init__(self):
        super().__init__()
        self._cache: List[Tuple[str, str]] = []
        self._cache_path: Optional[Path] = None

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="chrome_bookmarks",
            name="Chrome 书签",
            description="搜索 Chrome 书签，选中后在浏览器中打开",
            version="1.0.0",
            author="mif",
            icon="📑",
            keywords=["bm", "bookmark", "书签", "chrome"],
            at_keyword="bm",
            priority=30,
            config_options=[
                ConfigOption(
                    key="bookmarks_path",
                    name="书签文件路径",
                    description="留空则自动检测；可填完整路径或 Chrome 配置目录",
                    type="str",
                    default="",
                ),
                ConfigOption(
                    key="profile",
                    name="Chrome 配置名",
                    description="Chrome 配置文件夹名，如 Default、Profile 1",
                    type="str",
                    default="Default",
                ),
                ConfigOption(
                    key="max_results",
                    name="最大结果数",
                    description="最多返回多少条书签",
                    type="int",
                    default=15,
                ),
                ConfigOption(
                    key="click_weight",
                    name="点击率权重",
                    description="排序时点击率所占权重 0~1，其余为模糊匹配分；0 表示仅按匹配度",
                    type="float",
                    default=0.3,
                ),
            ],
        )

    def _open_and_record(self, url: str) -> None:
        """Open URL in browser and record one click for CTR sorting."""
        _record_click(url)
        import webbrowser
        webbrowser.open(url)

    def _ensure_loaded(self) -> List[Tuple[str, str]]:
        """Load bookmarks once; reuse cache if path unchanged."""
        profile = self.get_config("profile") or "Default"
        custom = self.get_config("bookmarks_path") or ""
        path = _get_bookmarks_path(profile, custom if custom.strip() else None)

        if path is None:
            logger.debug("Chrome bookmarks file not found")
            return []

        if path == self._cache_path and self._cache:
            return self._cache

        self._cache_path = path
        self._cache = _load_bookmarks(path)
        logger.debug(f"Loaded {len(self._cache)} bookmarks from {path}")
        return self._cache

    def match_keyword(self, query: str) -> bool:
        if not query.strip():
            return False
        return any(query.strip().lower().startswith(kw.lower()) for kw in self.meta.keywords)

    def strip_keyword(self, query: str) -> str:
        q = query.strip()
        for kw in sorted(self.meta.keywords, key=len, reverse=True):
            kw_l = kw.lower()
            if q.lower().startswith(kw_l + " "):
                return q[len(kw) + 1:].strip()
            if q.lower().startswith(kw_l):
                return q[len(kw):].strip()
        return q

    def search(self, query: str) -> List[PluginResult]:
        bookmarks = self._ensure_loaded()
        if not bookmarks:
            return []

        q = query.strip()
        max_n = max(1, min(50, self.get_config("max_results") or 15))
        click_weight = max(0.0, min(1.0, self.get_config("click_weight") or 0.3))
        fuzzy_weight = 1.0 - click_weight

        clicks = _load_clicks()
        max_clicks = max(clicks.values()) if clicks else 0

        def ctr_score(url: str) -> float:
            if not clicks:
                return 0.0
            c = clicks.get(url, 0)
            if max_clicks <= 0:
                return 0.0
            # log scale so 1 vs 10 matters more than 100 vs 110
            return math.log(1 + c) / math.log(1 + max_clicks)

        if not q:
            # No query: sort by CTR only, then take top max_n
            with_ctr = [(ctr_score(url), name, url) for name, url in bookmarks]
            with_ctr.sort(key=lambda x: (-x[0], x[1]))
            scored = [(fuzzy_weight + click_weight * s, name, url) for s, name, url in with_ctr[:max_n]]
        else:
            scored = []
            for name, url in bookmarks:
                fuzzy = _score(name, url, q)
                if fuzzy <= 0:
                    continue
                ctr = ctr_score(url)
                combined = fuzzy_weight * fuzzy + click_weight * ctr
                scored.append((combined, name, url))
            scored.sort(key=lambda x: (-x[0], x[1]))
            scored = scored[:max_n]

        results: List[PluginResult] = []
        for score, name, url in scored:
            subtitle = url if len(url) <= 60 else url[:57] + "..."
            results.append(PluginResult(
                title=name,
                subtitle=subtitle,
                icon="📑",
                action=self._open_and_record,
                action_args=(url,),
                plugin_id=self.meta.id,
                score=score,
                extra={"action_type": "open_url"},
            ))

        return results
