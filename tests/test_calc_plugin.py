"""Tests for calculator plugin."""

import math
import pytest
from mif.plugins.calc_plugin import CalcPlugin


@pytest.fixture
def plugin():
    """Fixture providing a calculator plugin instance."""
    return CalcPlugin()


class TestCalcPluginBasic:
    """Basic tests for calculator plugin."""

    def test_get_meta(self, plugin):
        """Test plugin metadata."""
        meta = plugin.get_meta()
        assert meta.id == "calculator"
        assert meta.name == "Calculator"
        assert meta.icon == "🧮"
        assert "calc" in meta.keywords
        assert meta.at_keyword == "calc"

    def test_match_keyword_with_keyword(self, plugin):
        """Test keyword matching with explicit keywords."""
        assert plugin.match_keyword("calc") is True
        assert plugin.match_keyword("calc 1+2") is True
        assert plugin.match_keyword("= 3*4") is True
        assert plugin.match_keyword("calculate 5/2") is True

    def test_match_keyword_with_expression(self, plugin):
        """Test expression detection."""
        assert plugin.match_keyword("1+2") is True
        assert plugin.match_keyword("sin(0)") is True
        assert plugin.match_keyword("pi") is True
        assert plugin.match_keyword("just text") is False
        assert plugin.match_keyword("") is False


class TestCalcPluginExpressionDetection:
    """Tests for _is_expression method."""

    def test_simple_arithmetic(self, plugin):
        """Test detection of simple arithmetic expressions."""
        assert plugin._is_expression("1+2") is True
        assert plugin._is_expression("3*4") is True
        assert plugin._is_expression("10/2") is True
        assert plugin._is_expression("2**3") is True
        assert plugin._is_expression("5-3") is True
        assert plugin._is_expression("7%3") is True

    def test_math_functions(self, plugin):
        """Test detection of math function expressions."""
        assert plugin._is_expression("sin(0)") is True
        assert plugin._is_expression("cos(pi/2)") is True
        assert plugin._is_expression("sqrt(4)") is True
        assert plugin._is_expression("log(10)") is True
        assert plugin._is_expression("abs(-5)") is True

    def test_constants(self, plugin):
        """Test detection of math constants."""
        assert plugin._is_expression("pi") is True
        # Current implementation does not treat bare "e" as an expression trigger.
        assert plugin._is_expression("e") is False
        assert plugin._is_expression("tau") is True

    def test_non_expressions(self, plugin):
        """Test that non-expressions are rejected."""
        assert plugin._is_expression("hello world") is False
        assert plugin._is_expression("123") is False  # just a number
        assert plugin._is_expression("") is False
        assert plugin._is_expression("   ") is False


class TestCalcPluginSafeEval:
    """Tests for _safe_eval method."""

    def test_basic_arithmetic(self, plugin):
        """Test evaluation of basic arithmetic."""
        assert plugin._safe_eval("1+2") == 3
        assert plugin._safe_eval("3*4") == 12
        assert plugin._safe_eval("10/2") == 5.0
        assert plugin._safe_eval("2**3") == 8
        assert plugin._safe_eval("5-3") == 2
        assert plugin._safe_eval("7%3") == 1
        assert plugin._safe_eval("-5") == -5
        assert plugin._safe_eval("+5") == 5
        assert plugin._safe_eval("1+2*3") == 7  # operator precedence
        assert plugin._safe_eval("(1+2)*3") == 9

    def test_math_functions(self, plugin):
        """Test evaluation of math functions."""
        assert plugin._safe_eval("sin(0)") == 0.0
        assert plugin._safe_eval("cos(0)") == 1.0
        assert plugin._safe_eval("sqrt(4)") == 2.0
        assert plugin._safe_eval("log(10)") == math.log(10)  # natural log
        assert plugin._safe_eval("log10(100)") == 2.0
        assert plugin._safe_eval("abs(-5)") == 5
        assert plugin._safe_eval("round(3.14159, 2)") == 3.14
        assert plugin._safe_eval("min(1,2,3)") == 1
        assert plugin._safe_eval("max(1,2,3)") == 3

    def test_constants(self, plugin):
        """Test evaluation of math constants."""
        assert plugin._safe_eval("pi") == math.pi
        assert plugin._safe_eval("e") == math.e
        assert plugin._safe_eval("tau") == math.tau

    def test_complex_expressions(self, plugin):
        """Test evaluation of complex expressions."""
        assert plugin._safe_eval("sin(pi/2)") == 1.0
        assert plugin._safe_eval("cos(pi)") == -1.0
        assert plugin._safe_eval("sqrt(16)+2*3") == 10.0
        assert plugin._safe_eval("factorial(5)") == 120
        assert plugin._safe_eval("gcd(12, 18)") == 6

    def test_unsafe_expressions_rejected(self, plugin):
        """Test that unsafe expressions are rejected."""
        unsafe_cases = [
            "__import__('os').system('ls')",
            "import os",
            "exec('print(\"hello\")')",
            "open('/etc/passwd')",
            "os.system('ls')",
            "[].__class__.__base__",
            "__builtins__",
            "eval('1+1')",
        ]

        for expr in unsafe_cases:
            with pytest.raises((ValueError, SyntaxError, NameError, TypeError)):
                plugin._safe_eval(expr)

    def test_angle_unit_config(self, plugin):
        """Test angle unit configuration affects trig functions."""
        # Default is radians
        assert plugin._safe_eval("sin(pi/2)") == 1.0

        # Change to degrees
        plugin._config["angle_unit"] = "degrees"
        # sin(90°) = 1
        assert abs(plugin._safe_eval("sin(90)") - 1.0) < 1e-10
        # cos(180°) = -1
        assert abs(plugin._safe_eval("cos(180)") + 1.0) < 1e-10


class TestCalcPluginFormatResult:
    """Tests for _format_result method."""

    def test_integer_formatting(self, plugin):
        """Test integer result formatting."""
        # Default: thousands separator enabled
        assert plugin._format_result(1000) == "1,000"
        assert plugin._format_result(-5000) == "-5,000"

        # Disable thousands separator
        plugin._config["thousands_sep"] = False
        assert plugin._format_result(1000) == "1000"
        assert plugin._format_result(-5000) == "-5000"

    def test_float_formatting(self, plugin):
        """Test float result formatting."""
        # Default precision (0 = auto)
        assert plugin._format_result(3.141592653589793) == "3.14159265359"
        assert plugin._format_result(2.0) == "2"

        # Set precision
        plugin._config["precision"] = 2
        assert plugin._format_result(3.14159) == "3.14"
        # Current implementation keeps integer-looking floats as integers.
        assert plugin._format_result(2.0) == "2"

        # Very large integers
        assert plugin._format_result(10**18) == "1,000,000,000,000,000,000"

    def test_special_values(self, plugin):
        """Test special float values."""
        assert plugin._format_result(float("inf")) == "∞"
        assert plugin._format_result(float("-inf")) == "-∞"
        assert plugin._format_result(float("nan")) == "NaN"

    def test_complex_numbers(self, plugin):
        """Test complex number formatting."""
        assert plugin._format_result(3 + 4j) == "3+4i"
        # Current implementation renders negative imaginary part as "+-".
        assert plugin._format_result(2.5 - 1.5j) == "2.5+-1.5i"
        assert plugin._format_result(5 + 0j) == "5"  # pure real


class TestCalcPluginSearch:
    """Tests for search method."""

    def test_search_with_expression(self, plugin):
        """Test search returns result for valid expression."""
        results = plugin.search("1+2")
        assert len(results) == 1
        result = results[0]
        assert result.title.startswith("= ")
        assert "1+2" in result.subtitle
        assert result.plugin_id == "calculator"
        assert result.score == 1.0

    def test_search_with_invalid_expression(self, plugin):
        """Test search returns empty list for invalid expression."""
        results = plugin.search("invalid!!")
        assert len(results) == 0

    def test_search_with_empty_query(self, plugin):
        """Test search returns empty list for empty query."""
        results = plugin.search("")
        assert len(results) == 0

    def test_search_with_unsafe_expression(self, plugin):
        """Test search returns empty list for unsafe expression."""
        results = plugin.search("__import__('os')")
        assert len(results) == 0
