"""Compute per-frame root traits from a primary and a lateral SLEAP file.

compute_traits(primary_path, lateral_path) loads both files, reduces each
frame's primary instances to a single longest root, and builds one DataFrame
row per frame: frame_idx plus the five traits from rootscope.traits.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from rootscope.io import load_frames
from rootscope.traits import (
    lateral_count,
    primary_angle_distal,
    primary_angle_proximal,
    primary_length,
    primary_tip_pt_y,
)


def longest_root(stack: np.ndarray) -> np.ndarray:
    """Reduce a frame's primary instances to the single longest root.

    Args:
        stack: A frame's primary instances, shape (n_instances, n_nodes, 2).

    Returns:
        One root, shape (n_nodes, 2). "Longest" is by primary_length, so the
        split-root frames (one root detected as two instances, primary 66-71)
        collapse to the longer piece. Returns an all-NaN root when there is
        nothing to choose from -- an empty frame (0 instances) or roots that
        are all NaN -- so every trait computed from it comes out NaN.
    """
    n_nodes = stack.shape[1]
    nan_root = np.full((n_nodes, 2), np.nan)

    if stack.shape[0] == 0:
        return nan_root

    lengths = [primary_length(root) for root in stack]
    if np.all(np.isnan(lengths)):
        return nan_root

    return stack[int(np.nanargmax(lengths))]


def _n_nodes(frames: dict[int, np.ndarray]) -> int:
    """Node count from any frame; raise if the file had no frames at all."""
    for arr in frames.values():
        return arr.shape[1]
    raise ValueError("file has no frames, cannot determine node count")


def compute_traits(primary_path: str | Path, lateral_path: str | Path) -> pd.DataFrame:
    """Per-frame traits table from a primary and a lateral SLEAP file.

    One row per frame_idx present in EITHER file (the union, sorted). Primary
    traits come from the frame's longest primary root -- all NaN if that frame
    has no primary instances. lateral_count comes from the frame's lateral
    stack -- 0 if that frame has no lateral instances.

    Columns: frame_idx, primary_length, primary_angle_proximal,
    primary_angle_distal, lateral_count, primary_tip_pt_y.
    """
    primary_frames = load_frames(primary_path)
    lateral_frames = load_frames(lateral_path)

    empty_primary = np.empty((0, _n_nodes(primary_frames), 2))
    empty_lateral = np.empty((0, _n_nodes(lateral_frames), 2))

    rows = []
    for frame_idx in sorted(primary_frames.keys() | lateral_frames.keys()):
        primary = longest_root(primary_frames.get(frame_idx, empty_primary))
        lateral = lateral_frames.get(frame_idx, empty_lateral)

        rows.append(
            {
                "frame_idx": frame_idx,
                "primary_length": primary_length(primary),
                "primary_angle_proximal": primary_angle_proximal(primary),
                "primary_angle_distal": primary_angle_distal(primary),
                "lateral_count": lateral_count(lateral),
                "primary_tip_pt_y": primary_tip_pt_y(primary),
            }
        )

    return pd.DataFrame(rows)
