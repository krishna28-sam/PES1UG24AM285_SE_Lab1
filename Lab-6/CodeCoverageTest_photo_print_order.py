"""Lab 6 - line (code) coverage tests for photo_print_order.py.

Run:
    coverage run --source=. -m pytest CodeCoverageTest_photo_print_order.py
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


def test_member_bonus_and_matte_rate():
    # member 4x6 -> 20 + 5 = 25 included, 30 copies -> 5 extra at 4 each
    assert extra_print_charge("4x6", 30, "matte", True) == 20


def test_standard_rate_for_non_matte_finish():
    # 4x6 non-member -> 20 included, 40 copies -> 20 extra at 7 each
    assert extra_print_charge("4x6", 40, "glossy", False) == 140


def test_bulk_surcharge_with_canvas_finish():
    # 4x6 -> 20 included, 100 copies -> 80 extra at 7 + 2 + 5 = 14 each
    assert extra_print_charge("4x6", 100, "canvas", False) == 1120


# ---------------------------------------------------------------- order_valid
def test_order_valid():
    assert order_valid(10, 100, False) is True


def test_rush_order_over_limit_rejected():
    assert order_valid(10, 51, True) is False


def test_oversized_file_rejected():
    assert order_valid(30, 10, False) is False


# ---------------------------------------------------------------- dispatch_status
def test_framed_international_on_time():
    # cutoff 24 + 24 = 48
    assert dispatch_status(48, True, True) == "on_time"


def test_unframed_domestic_tight():
    # cutoff 12, tight window is [6, 12)
    assert dispatch_status(8, False, False) == "tight"


def test_unframed_domestic_missed():
    assert dispatch_status(2, False, False) == "missed"
