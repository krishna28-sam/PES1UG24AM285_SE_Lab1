"""Lab 7 - Hypothesis fuzz tests for photo_print_order.py.

Contract being tested
---------------------
Every function must survive ANY input without raising an exception:
  * valid input   -> a correct result
  * invalid input -> None

Run:
    pytest test_photo_print_order.py
"""
import math

import pytest
from hypothesis import given, strategies as st

from photo_print_order import parse_order, file_size_average, payable_amount

# Anything a caller could possibly hand to these functions.
ANYTHING = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(),
    st.binary(),
    st.text(),
    st.lists(st.integers()),
    st.dictionaries(st.text(), st.integers()),
)

PRINT_SIZE = st.from_regex(r"[0-9]{1,2}x[0-9]{1,2}", fullmatch=True)


# =====================================================================
# 1. Basic fuzz tests: the function must never crash on text or None
# =====================================================================
@given(st.text() | st.none())
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(st.text() | st.none())
def test_file_size_average_no_crash(s):
    try:
        file_size_average(s)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(st.text() | st.none())
def test_payable_amount_no_crash(s):
    try:
        payable_amount(s)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


# =====================================================================
# 2. Wrong types: ints, floats, bytes, lists, dicts, ...
# =====================================================================
@given(ANYTHING)
def test_parse_order_any_type_no_crash(x):
    try:
        parse_order(x)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(ANYTHING)
def test_file_size_average_any_type_no_crash(x):
    try:
        file_size_average(x)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(ANYTHING)
def test_payable_amount_any_type_no_crash(x):
    try:
        payable_amount(x)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


@pytest.mark.parametrize("func", [parse_order, file_size_average, payable_amount])
@pytest.mark.parametrize("bad", [None, 5, 4.5, b"4x6:25", ["4x6:25"], {"a": 1}])
def test_non_string_input_returns_none(func, bad):
    assert func(bad) is None


# =====================================================================
# 3. parse_order: "size:copies" -> (SIZE, copies)
# =====================================================================
@given(PRINT_SIZE, st.integers(min_value=0, max_value=10**9))
def test_parse_order_valid_round_trip(size, copies):
    assert parse_order(f"{size}:{copies}") == (size.upper(), copies)


@given(PRINT_SIZE, st.integers(min_value=0, max_value=10**6))
def test_parse_order_ignores_surrounding_whitespace(size, copies):
    assert parse_order(f"  {size} :  {copies}  ") == (size.upper(), copies)


@given(st.text().filter(lambda s: ":" not in s))
def test_parse_order_without_colon_is_invalid(s):
    assert parse_order(s) is None


@given(st.text(alphabet="abc 12x", max_size=6), st.text(alphabet="abc 12x", max_size=6),
       st.text(alphabet="abc 12x", max_size=6))
def test_parse_order_too_many_colons_is_invalid(a, b, c):
    assert parse_order(f"{a}:{b}:{c}") is None


@given(PRINT_SIZE, st.integers(max_value=-1))
def test_parse_order_negative_copies_is_invalid(size, copies):
    assert parse_order(f"{size}:{copies}") is None


@pytest.mark.parametrize("text", [":5", "  :5", "4x6:", "4x6:abc", "4x6:2.5", "4x6:-1", ""])
def test_parse_order_known_bad_inputs(text):
    assert parse_order(text) is None


# =====================================================================
# 4. file_size_average: "4,8,12" -> 8
# =====================================================================
@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1, max_size=50))
def test_file_size_average_valid_lists(values):
    result = file_size_average(",".join(str(v) for v in values))
    assert result == sum(values) // len(values)
    assert min(values) <= result <= max(values)


@given(st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=10))
def test_file_size_average_ignores_spaces(values):
    result = file_size_average(" , ".join(str(v) for v in values))
    assert result == sum(values) // len(values)


@given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=10)
       .filter(lambda vs: any(v < 0 for v in vs)))
def test_file_size_average_negative_size_is_invalid(values):
    assert file_size_average(",".join(str(v) for v in values)) is None


@pytest.mark.parametrize("text", ["", ",", "4,,8", "4,8,", ",4", "a,b", "4;8", "1.5,2", "   "])
def test_file_size_average_known_bad_inputs(text):
    assert file_size_average(text) is None


def test_file_size_average_example_from_prompt():
    assert file_size_average("4,8,12") == 8


# =====================================================================
# 5. payable_amount: "450|50" -> 450 * 1.18 - 50
# =====================================================================
MONEY = st.floats(min_value=0, max_value=1e9, allow_nan=False, allow_infinity=False)


@given(MONEY, MONEY)
def test_payable_amount_valid_values(amount, discount):
    result = payable_amount(f"{amount!r}|{discount!r}")
    assert result is not None
    assert math.isfinite(result)
    assert result >= 0
    assert result == max(amount * 1.18 - discount, 0)


def test_payable_amount_example_from_prompt():
    assert payable_amount("450|50") == pytest.approx(481.0)


def test_payable_amount_discount_larger_than_total_is_free():
    assert payable_amount("10|1000") == 0


@pytest.mark.parametrize(
    "text",
    [
        "", "450", "450|", "|50", "|", "a|b", "1|2|3",
        "nan|1", "1|nan", "inf|1", "1|inf", "-inf|1", "1e999|0",
        "-5|1", "5|-1",          # negative money makes no sense
        "1.7e308|0",             # finite input, but the result overflows to inf
    ],
)
def test_payable_amount_known_bad_inputs(text):
    assert payable_amount(text) is None


@given(st.text().filter(lambda s: s.count("|") != 1))
def test_payable_amount_needs_exactly_one_pipe(s):
    assert payable_amount(s) is None
