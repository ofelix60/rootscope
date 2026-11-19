import numpy as np
import pytest

from rootscope.traits import (
    lateral_count,
    primary_angle_distal,
    primary_angle_proximal,
    primary_length,
    primary_tip_pt_y,
)


@pytest.mark.parametrize(
    "pts, expected",
    [
        ([[0, 0], [0, 10], [0, 20]], 20),
        ([[0, 0], [0, 10], [np.nan, np.nan], [0, 30]], 10),
        ([[0, 0], [np.nan, np.nan], [0, 20]], np.nan),
        ([[np.nan, np.nan], [0, 10], [0, 20]], 10),
        (np.empty((0, 2)), np.nan),
        ([[0, 0], [3, 4]], 5),
    ],
)
def test_primary_length(pts: np.ndarray, expected: float) -> None:
    result = primary_length(pts)

    assert result == pytest.approx(expected, nan_ok=True)


@pytest.mark.parametrize(
    "pts, expected",
    [
        ([[0, 0], [0, 10], [0, 20], [0, 30], [0, 40], [0, 50]], 0.0),  # straight down
        ([[0, 0], [10, 0], [20, 0], [30, 0], [40, 0], [50, 0]], 90.0),  # sideways right
        (
            [[0, 0], [-10, 0], [-20, 0], [0, 30], [0, 40], [0, 50]],
            90.0,
        ),  # sideways left: still 90
        (
            [[0, 0], [10, 10], [0, 20], [0, 30], [0, 40], [0, 50]],
            45.0,
        ),  # node 1 at a diagonal
        (
            [[0, 0], [np.nan, np.nan], [20, 0], [0, 30], [0, 40], [0, 50]],
            90.0,
        ),  # node 1 missing → node 2 used
        (
            [[0, 0], [np.nan, np.nan], [np.nan, np.nan], [0, 30], [0, 40], [0, 50]],
            np.nan,
        ),  # nodes 1 and 2 missing → NaN
        (
            [[np.nan, np.nan], [0, 10], [0, 20], [0, 30], [0, 40], [0, 50]],
            np.nan,
        ),  # base missing → NaN
        (
            [[0, 10], [0, 0], [0, 20], [0, 30], [0, 40], [0, 50]],
            180.0,
        ),  # node 1 above the base: pointing up
        (
            [[0, 0], [0, 0], [0, 20], [0, 30], [0, 40], [0, 50]],
            np.nan,
        ),  # node 1 on top of the base: no direction (sleap-roots says 90)
        (
            [[0, 0], [np.nan, np.nan], [20, 0], [0, 30], [0, 40]],
            90.0,
        ),  # 5 nodes: (5 + 1) // 2 = 3, so node 2 is still in the proximal half
    ],
)
def test_primary_angle_proximal(pts: np.ndarray, expected: float) -> None:
    result = primary_angle_proximal(pts)

    assert result == pytest.approx(expected, nan_ok=True)


@pytest.mark.parametrize(
    "pts, expected",
    [
        ([[0, 0], [0, 10], [0, 20], [0, 30], [0, 40], [0, 50]], 0.0),  # straight down
        (
            [[0, 0], [0, 10], [0, 20], [0, 30], [0, 40], [50, 50]],
            45.0,
        ),  # tip swings out
        (
            [[0, 0], [0, 10], [0, 20], [0, 30], [40, 0], [np.nan, np.nan]],
            90.0,
        ),  # tip missing → node 4 used
        (
            [
                [0, 0],
                [0, 10],
                [0, 20],
                [np.nan, np.nan],
                [np.nan, np.nan],
                [np.nan, np.nan],
            ],
            np.nan,
        ),  # 3, 4, 5 missing → NaN
        (
            [[np.nan, np.nan], [0, 10], [0, 20], [0, 30], [0, 40], [0, 50]],
            np.nan,
        ),  # base missing → NaN
        (
            [[0, 50], [0, 40], [0, 30], [0, 20], [0, 10], [0, 0]],
            180.0,
        ),  # tip above the base: pointing up
        (
            [[0, 0], [0, 10], [0, 20], [0, 30], [0, 40], [0, 0]],
            np.nan,
        ),  # tip on top of the base: no direction (sleap-roots says 90)
        (
            [[0, 0], [0, 10], [20, 0], [np.nan, np.nan], [np.nan, np.nan]],
            np.nan,
        ),  # 5 nodes: the distal half is nodes 3-4 only, so node 2 is NOT used
    ],
)
def test_primary_angle_distal(pts: np.ndarray, expected: float) -> None:
    result = primary_angle_distal(pts)

    assert result == pytest.approx(expected, nan_ok=True)


@pytest.mark.parametrize(
    "pts, expected",
    [
        (np.zeros((4, 3, 2)), 4),  # 4 laterals, 3 nodes each
        (np.zeros((1, 3, 2)), 1),
        (
            np.full((2, 3, 2), np.nan),
            2,
        ),  # all-NaN roots still count (same as sleap-roots)
        (np.empty((0, 3, 2)), 0),  # empty frame: deliberate, sleap-roots reports 1
    ],
)
def test_lateral_count(pts: np.ndarray, expected: int) -> None:
    result = lateral_count(pts)

    assert result == expected


@pytest.mark.parametrize(
    "pts, expected",
    [
        ([[0, 0], [0, 10], [3, 25]], 25.0),  # the tip's y; x doesn't matter
        ([[0, 0], [0, 30], [10, 20]], 20.0),  # the LAST dot, not the lowest one
        (
            [[0, 0], [0, 10], [np.nan, np.nan]],
            np.nan,
        ),  # tip missing: NaN, NOT 10
        ([[0, 0], [0, 10], [5, 40]], 40.0),
    ],
)
def test_primary_tip_pt_y(pts: np.ndarray, expected: float) -> None:
    result = primary_tip_pt_y(pts)

    assert result == pytest.approx(expected, nan_ok=True)
