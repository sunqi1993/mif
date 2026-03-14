"""Example calculator plugin for alfredpy."""

import re
import ast
import operator
from typing import List

from alfredpy.plugins.base import BasePlugin, PluginMeta, PluginResult


class CalcPlugin(BasePlugin):
    """Calculator plugin for quick math calculations."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def get_meta(self) -> PluginMeta:
        return PluginMeta(
            id="calculator",
            name="Calculator",
            description="Quick mathematical calculations",
            version="1.0.0",
            author="alfredpy",
            keywords=["=", "calc", "calculate"],
            priority=5,  # High priority
        )

    def search(self, query: str) -> List[PluginResult]:
        # Match mathematical expressions
        if not self._is_expression(query):
            return []

        try:
            result = self._safe_eval(query)
            return [
                PluginResult(
                    title=f"= {result}",
                    subtitle=f"Calculate: {query}",
                    action=self._copy_result,
                    action_args=(str(result),),
                    plugin_id=self.meta.id,
                )
            ]
        except Exception:
            return []

    def _is_expression(self, query: str) -> bool:
        """Check if query is a mathematical expression."""
        return bool(re.match(r"^[\d\+\-\*\/\.\(\)\s]+$", query))

    def _safe_eval(self, expr: str) -> float:
        """Safely evaluate mathematical expression."""
        node = ast.parse(expr, mode="eval")
        return self._eval_node(node.body)

    def _eval_node(self, node):
        if isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python >= 3.8
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            return self.OPERATORS[type(node.op)](operand)
        else:
            raise ValueError("Unsupported expression")

    def _copy_result(self, result: str):
        """Copy result to clipboard."""
        try:
            import pyperclip

            pyperclip.copy(result)
            print(f"Copied to clipboard: {result}")
        except ImportError:
            print(f"Result: {result}")
            print("Tip: Install pyperclip to auto-copy results")
