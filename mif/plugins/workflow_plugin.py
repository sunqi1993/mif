"""WorkflowPlugin — wraps workflows.json as a first-class plugin.

This bridges the Workflow (JSON-configured) and Plugin (Python-coded) worlds:
  • Every WorkflowItem becomes a PluginResult with a unified interface.
  • Fuzzy name/description matching (via thefuzz) replaces naive substring search.
  • Per-workflow `keywords` enable prefix triggers (e.g. "g python" → Google search).
  • {query} substitution is passed through to WorkflowItem.run().
  • All workflows are browsable via @wf in the search box.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from mif.plugins.base import BasePlugin, PluginMeta, PluginResult
from mif.workflow import WorkflowItem

logger = logging.getLogger("AlfredPy.WorkflowPlugin")

# Minimum fuzzy score (0–1) to include a workflow in results
_FUZZY_THRESHOLD = 0.42


class WorkflowPlugin(BasePlugin):
    """Wraps config/workflows.json as a searchable plugin."""

    def __init__(self):
        super().__init__()
        self._workflows: List[WorkflowItem] = []
        self._load()

    # ── Metadata ──────────────────────────────────────────────────────────────

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="workflows",
            name="Workflows",
            description="JSON 配置的自动化快捷指令 (@wf 浏览全部)",
            version="1.0.0",
            author="mif",
            icon="🚀",
            keywords=[],          # override match_keyword to always participate
            at_keyword="wf",      # @wf → browse/filter all workflows
            priority=50,          # behind calc (5) but ahead of defaults (100)
        )

    # ── Keyword matching ──────────────────────────────────────────────────────

    def match_keyword(self, query: str) -> bool:
        """Always participate — filtering (score threshold) happens in search()."""
        return True

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> List[PluginResult]:
        q = query.strip()
        results: List[PluginResult] = []

        for wf in self._workflows:
            score, subst = self._score(wf, q)
            if score <= 0:
                continue

            # Build subtitle: show substitution hint when {query} is used
            subtitle = wf.description or ""
            if "{query}" in str(wf.args.values()) and not subst:
                # 与插件一致：展示实际触发关键词（如 触发词: g, google）
                kw_hint = " / ".join(wf.keywords) if wf.keywords else "关键词"
                subtitle = f"{'  ' + subtitle if subtitle else ''}  ← 输入 {kw_hint} 后触发".strip()

            results.append(PluginResult(
                title=wf.name,
                subtitle=subtitle,
                icon=wf.icon,
                action=wf.run,
                action_args=(subst,),          # substituted query text
                plugin_id=self.meta.id,
                score=score,
                extra={
                    "action_type": wf.action,  # e.g. "open_url" for window-close hint
                    "wf_id": wf.id,
                },
            ))

        # Sort by score desc, then by workflow priority asc
        results.sort(key=lambda r: (-r.score, self._priority(r)))
        return results

    # ── Scoring ───────────────────────────────────────────────────────────────

    def _score(self, wf: WorkflowItem, query: str) -> Tuple[float, str]:
        """Return (score, substitution_text). score=0 → exclude from results."""
        if not query:
            # Empty query: show all, ordered by priority
            return 1.0 - wf.priority / 10_000, ""

        # ── Per-workflow keyword match (highest priority) ───────────────────
        if wf.keywords:
            for kw in wf.keywords:
                kw_l = kw.lower()
                if query.lower() == kw_l:
                    return 2.0, ""
                if query.lower().startswith(kw_l + " "):
                    subst = query[len(kw):].strip()
                    return 2.0, subst

        # ── Fuzzy name / description match ─────────────────────────────────
        fuzzy = self._fuzzy_score(wf, query)
        return (fuzzy, query) if fuzzy >= _FUZZY_THRESHOLD else (0.0, "")

    @staticmethod
    def _fuzzy_score(wf: WorkflowItem, query: str) -> float:
        try:
            from thefuzz import fuzz
            ql = query.lower()
            name_s = fuzz.token_set_ratio(ql, wf.name.lower()) / 100
            desc_s = (
                fuzz.token_set_ratio(ql, wf.description.lower()) / 100
                if wf.description else 0.0
            )
            return max(name_s, desc_s * 0.8)
        except ImportError:
            q = query.lower()
            if q in wf.name.lower():
                return 1.0
            if wf.description and q in wf.description.lower():
                return 0.8
            return 0.0

    def _priority(self, result: PluginResult) -> int:
        wf_id = result.extra.get("wf_id", "")
        for wf in self._workflows:
            if wf.id == wf_id:
                return wf.priority
        return 100

    # ── Config loading ────────────────────────────────────────────────────────

    def _load(self) -> None:
        from mif.config import load_config
        self._workflows = []
        try:
            config = load_config()
            raw = config if isinstance(config, list) else config.get("workflows", [])
            self._workflows = [
                WorkflowItem.from_dict(item)
                for item in raw
                if isinstance(item, dict)
            ]
            logger.debug(f"WorkflowPlugin: loaded {len(self._workflows)} workflows")
        except Exception as e:
            logger.warning(f"WorkflowPlugin: failed to load workflows: {e}")

    def reload(self) -> None:
        """Reload workflows from disk (call after editing workflows.json)."""
        self._load()
