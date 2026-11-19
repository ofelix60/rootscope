"""Tests for rootscope.pipeline.

Expected canola numbers were measured from the canola fixture files.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import sleap_io as sio

from rootscope.pipeline import compute_traits, longest_root

EXPECTED_COLUMNS = [
    "frame_idx",
    "primary_length",
    "primary_angle_proximal",
    "primary_angle_distal",
    "lateral_count",
    "primary_tip_pt_y",
]


@pytest.mark.parametrize(
    "stack, expected",
    [
        (
            np.array([[[0, 0], [0, 5], [0, 10]], [[0, 0], [0, 20], [0, 40]]], float),
            np.array([[0, 0], [0, 20], [0, 40]], float),
        ),
        (
            np.array([[[0, 0], [0, 20], [0, 40]], [[0, 0], [0, 5], [0, 10]]], float),
            np.array([[0, 0], [0, 20], [0, 40]], float),
        ),
        (
            np.array(
                [[[0, 0], [0, 30], [0, 40]], [[0, 0], [0, 10], [np.nan, np.nan]]],
                float,
            ),
            np.array([[0, 0], [0, 30], [0, 40]], float),
        ),
        # tie: equal-length roots -> the first one wins (matches nanargmax)
        (
            np.array([[[0, 0], [0, 10]], [[5, 5], [5, 15]]], float),
            np.array([[0, 0], [0, 10]], float),
        ),
        (np.full((2, 3, 2), np.nan), np.full((3, 2), np.nan)),
        (np.empty((0, 3, 2)), np.full((3, 2), np.nan)),
    ],
)
def test_longest_root(stack: np.ndarray, expected: np.ndarray) -> None:
    result = longest_root(stack)
    assert result.shape == expected.shape
    assert np.array_equal(result, expected, equal_nan=True)


@pytest.fixture
def traits(canola_primary_slp: Path, canola_lateral_slp: Path) -> pd.DataFrame:
    return compute_traits(canola_primary_slp, canola_lateral_slp)


def test_shape(traits: pd.DataFrame) -> None:
    assert traits.shape == (72, 6)


def test_columns(traits: pd.DataFrame) -> None:
    assert list(traits.columns) == EXPECTED_COLUMNS


def test_angle_nan_counts(traits: pd.DataFrame) -> None:
    # Both angle columns are NaN on the same 18 frames: the 12 base-missing
    # single-instance frames (33-45 except 38), plus the 6 split frames
    # (66-71). In the split frames the longer piece is the bottom one, which
    # has no base, so BOTH angles are NaN there -- not just distal.
    assert traits["primary_angle_proximal"].isna().sum() == 18
    assert traits["primary_angle_distal"].isna().sum() == 18


def test_empty_lateral_frame_counts_zero(
    canola_primary_slp: Path, canola_lateral_slp: Path, tmp_path: Path
) -> None:
    # A lateral file with a genuinely empty frame -> lateral_count 0 there.
    lateral = sio.load_slp(canola_lateral_slp)
    video = lateral.videos[0]
    empty_lateral = sio.Labels(
        videos=[video],
        skeletons=lateral.skeletons,
        labeled_frames=[sio.LabeledFrame(video=video, frame_idx=0, instances=[])],
    )
    lateral_path = tmp_path / "empty_lateral.slp"
    sio.save_slp(empty_lateral, lateral_path)

    result = compute_traits(canola_primary_slp, lateral_path)
    assert int(result.loc[result["frame_idx"] == 0, "lateral_count"].iloc[0]) == 0


def test_frame_in_one_file_only(canola_primary_slp: Path, tmp_path: Path) -> None:
    # Primary has frame 0; lateral has only frame 1. The union keeps both
    # rows: frame 0 gets lateral_count 0, frame 1 gets all-NaN primary traits.
    lateral = sio.load_slp(canola_primary_slp)  # reuse as a stand-in lateral
    video = lateral.videos[0]
    only_frame_1 = sio.Labels(
        videos=[video],
        skeletons=lateral.skeletons,
        labeled_frames=[
            sio.LabeledFrame(
                video=video,
                frame_idx=1,
                instances=lateral.labeled_frames[0].instances,
            )
        ],
    )
    lateral_path = tmp_path / "only_frame_1.slp"
    sio.save_slp(only_frame_1, lateral_path)

    # Primary stand-in: only frame 0.
    primary = sio.load_slp(canola_primary_slp)
    only_frame_0 = sio.Labels(
        videos=[primary.videos[0]],
        skeletons=primary.skeletons,
        labeled_frames=[
            sio.LabeledFrame(
                video=primary.videos[0],
                frame_idx=0,
                instances=primary.labeled_frames[0].instances,
            )
        ],
    )
    primary_path = tmp_path / "only_frame_0.slp"
    sio.save_slp(only_frame_0, primary_path)

    result = compute_traits(primary_path, lateral_path)
    assert sorted(result["frame_idx"]) == [0, 1]
    # frame 0: lateral absent -> count 0; frame 1: primary absent -> length NaN
    assert int(result.loc[result["frame_idx"] == 0, "lateral_count"].iloc[0]) == 0
    assert np.isnan(result.loc[result["frame_idx"] == 1, "primary_length"].iloc[0])
