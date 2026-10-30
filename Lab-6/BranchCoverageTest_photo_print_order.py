"""Lab 6 - branch coverage tests for photo_print_order.py.

Every decision is exercised for both its True and False outcome.

Run:
    coverage run --branch --source=. -m pytest BranchCoverageTest_photo_print_order.py
    coverage report -m
"""
import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status


# ---------------------------------------------------------------- extra_print_charge
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0


def test_unknown_print_size_raises():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("11x14", 1, "matte", False)


def test_negative_copies_raises():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)


def test_zero_copies_is_free():
    assert extra_print_charge("4x6", 0, "matte", False) == 0


def test_exactly_at_included_limit_is_free():
    # extra == 0 hits the `extra <= 0` boundary
    assert extra_print_charge("4x6", 20, "matte", False) == 0


def test_one_over_included_limit_is_charged():
    assert extra_print_charge("4x6", 21, "matte", False) == 4


def test_member_gets_five_extra_included_prints():
    # member 4x6 -> 25 included; 25 copies free
    assert extra_print_charge("4x6", 25, "matte", True) == 0
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_member_bonus_applies_to_5x7():
    # 5x7 -> 15 + 5 = 20 included
    assert extra_print_charge("5x7", 20, "glossy", True) == 0
    assert extra_print_charge("5x7", 21, "glossy", True) == 7


def test_member_gets_no_bonus_on_8x10():
    # 8x10 stays at 10 included even for members
    assert extra_print_charge("8x10", 10, "matte", True) == 0
    assert extra_print_charge("8x10", 11, "matte", True) == 4


def test_non_member_gets_no_bonus():
    assert extra_print_charge("4x6", 25, "matte", False) == 20


def test_matte_rate():
    assert extra_print_charge("4x6", 30, "matte", False) == 40


def test_non_matte_finish_uses_standard_rate():
    assert extra_print_charge("4x6", 40, "glossy", False) == 140


def test_bulk_surcharge_boundary_exactly_fifty_extra_has_no_surcharge():
    # extra == 50 -> `extra > 50` is False
    assert extra_print_charge("4x6", 70, "matte", False) == 200


def test_bulk_surcharge_just_over_fifty_matte():
    # extra == 51 -> rate 4 + 2 = 6, finish is not canvas
    assert extra_print_charge("4x6", 71, "matte", False) == 51 * 6


def test_bulk_surcharge_non_canvas_non_matte():
    # extra == 80 -> rate 7 + 2 = 9, finish is not canvas
    assert extra_print_charge("4x6", 100, "glossy", False) == 80 * 9


def test_bulk_surcharge_with_canvas_finish():
    # extra == 80 -> rate 7 + 2 + 5 = 14
    assert extra_print_charge("4x6", 100, "canvas", False) == 1120


def test_canvas_finish_without_bulk_has_no_extra_surcharge():
    # canvas, extra == 10 (<= 50) -> plain standard rate of 7
    assert extra_print_charge("4x6", 30, "canvas", False) == 70


# ---------------------------------------------------------------- order_valid
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_order_within_limit_accepted():
    assert order_valid(10, 50, True) is True


def test_rush_order_over_limit_rejected():
    assert order_valid(10, 51, True) is False


def test_rush_order_ignores_file_size_limit():
    assert order_valid(100, 10, True) is True


def test_oversized_file_rejected():
    assert order_valid(26, 10, False) is False


def test_file_size_at_limit_accepted():
    assert order_valid(25, 10, False) is True


def test_normal_order_at_copy_limit_accepted():
    assert order_valid(10, 500, False) is True


def test_normal_order_over_copy_limit_rejected():
    assert order_valid(10, 501, False) is False


# ---------------------------------------------------------------- dispatch_status
@pytest.mark.parametrize(
    "hours, framed, international, expected",
    [
        # unframed domestic: cutoff 12, tight from 6
        (12, False, False, "on_time"),
        (11, False, False, "tight"),
        (6, False, False, "tight"),
        (5, False, False, "missed"),
        # framed domestic: cutoff 24, tight from 18
        (24, True, False, "on_time"),
        (23, True, False, "tight"),
        (18, True, False, "tight"),
        (17, True, False, "missed"),
        # unframed international: cutoff 36, tight from 30
        (36, False, True, "on_time"),
        (35, False, True, "tight"),
        (30, False, True, "tight"),
        (29, False, True, "missed"),
        # framed international: cutoff 48, tight from 42
        (48, True, True, "on_time"),
        (47, True, True, "tight"),
        (42, True, True, "tight"),
        (41, True, True, "missed"),
    ],
)
def test_dispatch_status(hours, framed, international, expected):
    assert dispatch_status(hours, framed, international) == expected
