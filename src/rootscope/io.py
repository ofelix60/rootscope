"""Load SLEAP prediction files into per-frame keypoint arrays.

One function, load_frames, turns a .slp file into a dict of per-frame
instance arrays for pipeline.py to build traits from.
"""

from pathlib import Path

import numpy as np
import sleap_io as sio


def load_frames(path: str | Path) -> dict[int, np.ndarray]:
    """Map each frame_idx to its instances, shape (n_instances, n_nodes, 2).

    Keyed by frame.frame_idx, not loop position, so a frame absent from the
    file simply has no key. pipeline.py must handle that when primary and
    lateral files don't cover the same frames.

    An empty frame (no instances) maps to np.empty((0, n_nodes, 2)): same
    axes as a real frame, zero instances, so an instance count comes out 0
    rather than raising.

    Assumes one skeleton per file (uses skeletons[0]).

    frame.instances includes every instance, both user-labelled and
    predicted. sleap-roots instead uses user_instances + unused_predictions,
    which avoids counting a user-corrected root twice; in these files every
    frame has 0 user instances, so the two are equivalent here.
    """
    labels = sio.load_slp(path, open_videos=False)
    n_nodes = len(labels.skeletons[0].node_names)

    frames: dict[int, np.ndarray] = {}
    for frame in labels.labeled_frames:
        instances = [instance.numpy() for instance in frame.instances]
        if instances:
            frames[frame.frame_idx] = np.stack(instances)
        else:
            frames[frame.frame_idx] = np.empty((0, n_nodes, 2))
    return frames
