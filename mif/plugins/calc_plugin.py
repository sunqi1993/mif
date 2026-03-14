"""Calculator plugin — evaluates arithmetic and math-function expressions.

Configuration options (persistent via ~/.mif/plugin_configs.json):
  angle_unit   : "radians" | "degrees"  — unit for trig functions (default: radians)
  precision    : int ≥ 0                — decimal places shown (0 = auto, default: 0)
  thousands_sep: bool                   — show thousands separator (default: True)
"""

import math
import re
from typing import List

from mif.plugins.base import BasePlugin, ConfigOption, PluginMeta, PluginResult


# ── Base safe namespace (angle-independent parts) ─────────────────────────────
_BASE_NS: dict = {
    "__builtins__": {},
    # Hyperbolic
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    # Roots / powers / exp
    "sqrt": math.sqrt,
    "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
    "pow": math.pow, "exp": math.exp,
    # Logarithms
    "log": math.log, "log2": math.log2, "log10": math.log10, "ln": math.log,
    # Rounding
    "abs": abs, "round": round, "floor": math.floor, "ceil": math.ceil,
    # Combinatorics
    "factorial": math.factorial, "gcd": math.gcd,
    # Angle conversion helpers (always available regardless of angle_unit setting)
    "degrees": math.degrees, "radians": math.radians,
    # Constants
    "pi": math.pi, "e": math.e, "tau": math.tau, "inf": math.inf,
    # Aggregates
    "min": min, "max": max, "sum": sum,
}

# ── Patterns ──────────────────────────────────────────────────────────────────
_SIMPLE_RE = re.compile(r"^[\d\+\-\*\/\.\(\)\s\%\^\_]+$")
_MATH_WORD_RE = re.compile(
    r"\b(?:sin|cos|tan|asin|acos|atan|sinh|cosh|tanh|sqrt|cbrt|"
    r"log2?|log10|ln|exp|abs|round|floor|ceil|pow|factorial|gcd|"
    r"degrees|radians|pi|tau|inf)\b",
    re.IGNORECASE,
)
_NORM = str.maketrans({"^": "**", "×": "*", "÷": "/", "，": ","})
_UNSAFE_RE = re.compile(r"(__|\bimport\b|\bexec\b|\beval\b|\bopen\b|\bos\b|\bsys\b)")


class CalcPlugin(BasePlugin):
    """Real-time math expression evaluator with configurable behaviour."""

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="calculator",
            name="Calculator",
            description="实时计算数学表达式，支持三角函数、对数等",
            version="2.1.0",
            author="mif",
            icon="🧮",
            keywords=["=", "calc", "calculate"],
            at_keyword="calc",        # triggered by @calc in the search box
            priority=5,
            config_options=[
                ConfigOption(
                    key="angle_unit",
                    name="角度单位",
                    description="三角函数（sin/cos/tan）使用的角度单位",
                    type="choice",
                    default="radians",
                    choices=["radians", "degrees"],
                ),
                ConfigOption(
                    key="precision",
                    name="小数位数",
                    description="结果显示的最大小数位数，0 表示自动",
                    type="int",
                    default=0,
                ),
                ConfigOption(
                    key="thousands_sep",
                    name="千位分隔符",
                    description="整数结果是否显示千位分隔符（如 1,024）",
                    type="bool",
                    default=True,
                ),
            ],
        )

    # ── Keyword matching ──────────────────────────────────────────────────────

    def match_keyword(self, query: str) -> bool:
        q = query.strip()
        if not q:
            return False
        if any(q.startswith(kw) for kw in self.meta.keywords):
            return True
        return self._is_expression(q)

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> List[PluginResult]:
        q = query.strip()
        if not q or not self._is_expression(q):
            return []
        try:
            value = self._safe_eval(q)
        except Exception:
            return []
        if value is None:
            return []

        result_str = self._format_result(value)
        angle_note = (
            "  [度数模式]" if self.get_config("angle_unit") == "degrees" else ""
        )
        return [
            PluginResult(
                title=f"= {result_str}",
                subtitle=f"{q}  =  {result_str}{angle_note}    ↩ 点击复制",
                action=self._copy_result,
                action_args=(result_str.replace(",", ""),),   # copy plain number
                plugin_id=self.meta.id,
                score=1.0,
            )
        ]

    # ── Expression detection ──────────────────────────────────────────────────

    def _is_expression(self, query: str) -> bool:
        q = query.strip()
        if not q:
            return False
        if _SIMPLE_RE.match(q):
            return any(c in q for c in "+-*/%^") and any(c.isdigit() for c in q)
        return bool(_MATH_WORD_RE.search(q))

    # ── Safe evaluation ───────────────────────────────────────────────────────

    def _build_namespace(self) -> dict:
        """Build the eval namespace, injecting angle-aware trig functions."""
        ns = dict(_BASE_NS)
        if self.get_config("angle_unit") == "degrees":
            ns.update({
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "asin": lambda x: math.degrees(math.asin(x)),
                "acos": lambda x: math.degrees(math.acos(x)),
                "atan": lambda x: math.degrees(math.atan(x)),
                "atan2": lambda y, x: math.degrees(math.atan2(y, x)),
            })
        else:
            ns.update({
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "asin": math.asin, "acos": math.acos,
                "atan": math.atan, "atan2": math.atan2,
            })
        return ns

    def _safe_eval(self, expr: str):
        normalized = expr.translate(_NORM).strip()
        if _UNSAFE_RE.search(normalized):
            raise ValueError("Unsafe expression")
        result = eval(normalized, self._build_namespace())  # noqa: S307
        if not isinstance(result, (int, float, complex)):
            raise TypeError("Non-numeric result")
        return result

    # ── Formatting ────────────────────────────────────────────────────────────

    def _format_result(self, value) -> str:
        precision: int = self.get_config("precision", 0)
        use_sep: bool = self.get_config("thousands_sep", True)

        if isinstance(value, complex):
            if value.imag == 0:
                return self._format_result(value.real)
            return f"{value.real:.6g}+{value.imag:.6g}i"

        if isinstance(value, float):
            if math.isinf(value):
                return "∞" if value > 0 else "-∞"
            if math.isnan(value):
                return "NaN"
            if value == int(value) and abs(value) < 1e15:
                value = int(value)
            else:
                if precision > 0:
                    return f"{value:.{precision}f}"
                return f"{value:.12g}"

        if isinstance(value, int):
            if use_sep:
                return f"{value:,}"
            return str(value)

        return str(value)

    # ── Clipboard ─────────────────────────────────────────────────────────────

    @staticmethod
    def _copy_result(result: str) -> None:
        try:
            import pyperclip
            pyperclip.copy(result)
        except ImportError:
            print(f"Result: {result}")
            print("Tip: pip install pyperclip to enable auto-copy")
