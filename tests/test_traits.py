import numpy as np
import pytest

from rootscope.traits import lateral_count, primary_length


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
# np.ndarray[tuple[Any, ...], np.dtype[Any]
def test_primary_length(pts: np.ndarray, expected: float) -> None:
    result = primary_length(pts)

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
        (np.empty((0, 3, 2)), 0),  # empty frame: YOUR choice (sleap-roots reports 1)
    ],
)
def test_lateral_count(pts: np.ndarray, expected: int) -> None:
    result = lateral_count(pts)

    assert result == expected
