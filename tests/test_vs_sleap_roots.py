"""Step 6: validate rootscope.compute_traits against sleap-roots.

For each plant, run sleap-roots' DicotPipeline and rootscope's compute_traits
on the same two .slp files, line the results up by frame_idx, and check that
all five shared columns agree within the lab's own tolerance (atol=1e-7).

This is the only file in the repo that imports sleap-roots. It is skipped
cleanly if sleap-roots isn't installed (it's a dev-group dependency).
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rootscope.pipeline import compute_traits

sleap_roots = pytest.importorskip("sleap_roots")
from sleap_roots import DicotPipeline, Series  # noqa: E402

SHARED_COLUMNS = [
    "primary_length",
    "primary_angle_proximal",
    "primary_angle_distal",
    "lateral_count",
    "primary_tip_pt_y",
]


def test_sleap_roots_version() -> None:
    # Re-validate before bumping: a sleap-roots update can silently change the
    # reference these comparisons are made against.
    assert sleap_roots.__version__ == "0.1.4", (
        f"validated against sleap-roots 0.1.4, found {sleap_roots.__version__}; "
        "re-validate before bumping"
    )


@pytest.fixture(scope="module")
def aligned(plant_paths: tuple[str, Path, Path]) -> pd.DataFrame:
    """Run both pipelines on one plant, merged one-to-one on frame_idx.

    Module-scoped so sleap-roots runs once per plant, not once per column.
    Columns are suffixed _mine and _theirs after the merge.
    """
    series_name, primary_path, lateral_path = plant_paths

    series = Series.load(
        series_name=series_name,
        primary_path=str(primary_path),
        lateral_path=str(lateral_path),
    )
    theirs = DicotPipeline().compute_plant_traits(series)
    mine = compute_traits(primary_path, lateral_path)

    # Same set of frames on both sides, or every comparison below is meaningless.
    assert set(mine["frame_idx"]) == set(theirs["frame_idx"]), (
        "frame_idx sets differ between rootscope and sleap-roots"
    )

    merged = mine.merge(
        theirs[["frame_idx", *SHARED_COLUMNS]],
        on="frame_idx",
        suffixes=("_mine", "_theirs"),
        validate="one_to_one",  # also catches duplicate frames on either side
    )
    assert len(merged) > 0, "no frames to compare"
    return merged


@pytest.mark.parametrize("column", SHARED_COLUMNS)
def test_matches(aligned: pd.DataFrame, column: str) -> None:
    mine = aligned[f"{column}_mine"].to_numpy(float)
    theirs = aligned[f"{column}_theirs"].to_numpy(float)
    np.testing.assert_allclose(mine, theirs, atol=1e-7, equal_nan=True)
