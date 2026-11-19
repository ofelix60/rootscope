"""Tests for rootscope.io.load_frames.

Expected shapes and counts were measured from the canola and soy fixture files.
"""

from collections import Counter
from pathlib import Path

import sleap_io as sio

from rootscope.io import load_frames


def test_primary_has_72_frames(canola_primary_slp: Path) -> None:
    assert len(load_frames(canola_primary_slp)) == 72


def test_primary_frame_0_shape(canola_primary_slp: Path) -> None:
    assert load_frames(canola_primary_slp)[0].shape == (1, 6, 2)


def test_primary_frame_66_is_split_root(canola_primary_slp: Path) -> None:
    # frames 66-71: the one primary root comes back as 2 instances
    assert load_frames(canola_primary_slp)[66].shape == (2, 6, 2)


def test_lateral_frame_0_count(canola_lateral_slp: Path) -> None:
    # lateral frame 0: 5 instances, 3 nodes each
    assert load_frames(canola_lateral_slp)[0].shape == (5, 3, 2)


def test_lateral_instance_distribution(canola_lateral_slp: Path) -> None:
    # instances per frame across all 72 frames, as a check that the whole file
    # was read, not just the first frame
    frames = load_frames(canola_lateral_slp)
    counts = Counter(arr.shape[0] for arr in frames.values())
    assert counts == {4: 44, 3: 12, 5: 11, 6: 5}


def test_soy_node_counts(soy_primary_slp: Path, soy_lateral_slp: Path) -> None:
    # soy skeletons: primary 6 nodes, lateral 4 (vs canola's lateral 3)
    primary = next(iter(load_frames(soy_primary_slp).values()))
    lateral = next(iter(load_frames(soy_lateral_slp).values()))
    assert primary.shape[1] == 6
    assert lateral.shape[1] == 4


def test_empty_frame_loads_as_zero_instances(
    canola_primary_slp: Path, tmp_path: Path
) -> None:
    # Build a file with a real empty frame and check load_frames gives it
    # (0, n_nodes, 2). This exercises the else branch no real file reaches.
    labels = sio.load_slp(canola_primary_slp)
    video = labels.videos[0]
    real_frame = labels.labeled_frames[0]
    empty_frame = sio.LabeledFrame(video=video, frame_idx=1, instances=[])

    new_labels = sio.Labels(
        videos=[video],
        skeletons=labels.skeletons,
        labeled_frames=[
            sio.LabeledFrame(video=video, frame_idx=0, instances=real_frame.instances),
            empty_frame,
        ],
    )
    out_path = tmp_path / "with_empty.slp"
    sio.save_slp(new_labels, out_path)

    frames = load_frames(out_path)
    assert frames[0].shape == (1, 6, 2)
    assert frames[1].shape == (0, 6, 2)
    assert len(frames[1]) == 0
