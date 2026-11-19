"""Root traits computed from SLEAP keypoints, re-implemented with NumPy only.

Every primary-root trait takes ONE root: an array of shape (n_nodes, 2), with
node 0 = base and node -1 = tip. Image y grows downward. A missing keypoint is
a row of NaN. Each function names the sleap-roots function it is validated
against.
"""

import numpy as np


def primary_length(pts: np.ndarray) -> float:
    """Length of one root: the sum of the distances between consecutive nodes.

    Args:
        pts: One root, shape (n_nodes, 2).

    Returns:
        The length in pixels. A segment that touches a missing node is skipped,
        not bridged: [A, B, NaN, D] gives |AB| only. If every segment is missing
        (no nodes, one node, or no two neighbouring nodes found), returns NaN.

    Matches `sleap_roots.lengths.get_root_lengths`.
    """
    pts = np.array(pts, dtype=float)

    gaps = np.diff(pts, axis=0)
    distances = np.linalg.norm(gaps, axis=1)
    if np.all(np.isnan(distances)):
        return np.nan
    return float(np.nansum(distances))


def _angle_from_down(base_point: np.ndarray, node_point: np.ndarray) -> float:
    """Angle in degrees between the base->node vector and straight down (0, +1).

    0 = pointing down, 90 = sideways (left or right, no sign), 180 = pointing up.
    A missing (NaN) point gives NaN.

    If node_point is exactly on base_point, the vector has no direction and this
    returns NaN. Deliberate difference: sleap-roots returns 90 in this case,
    because arctan2(0, 0) = 0. It does not occur in the reference data.
    """
    vector = node_point - base_point
    _, dy = vector
    magnitude = np.linalg.norm(vector)

    if magnitude == 0:
        return np.nan

    # cos(angle) = (vector . down) / |vector|, and vector . (0, 1) = dy.
    # Clip because rounding can push the cosine just past +/-1, giving NaN.
    cosine = dy / magnitude
    angle = np.degrees(np.arccos(np.clip(cosine, -1, 1)))
    return float(angle)


def primary_angle_proximal(pts: np.ndarray) -> float:
    """Angle from straight down of the top part of a root.

    Measured from the base (node 0) to the FIRST found node in the first half
    of the root, which is nodes 1 to (n_nodes + 1) // 2 - 1. For 6 nodes, that
    is node 1, falling back to node 2.

    Args:
        pts: One root, shape (n_nodes, 2).

    Returns:
        Degrees in [0, 180] (see `_angle_from_down`). NaN if the base is
        missing, or if no node in that half is found.

    Matches `sleap_roots.angle.get_node_ind` plus `get_root_angle`
    (proximal=True).
    """
    pts = np.array(pts, dtype=float)

    midpoint = (len(pts) + 1) // 2
    is_found = ~np.isnan(pts).any(axis=-1)

    # Skip node 0 (the base): positions in this slice are node index - 1.
    proximal_indices = np.flatnonzero(is_found[1:midpoint])

    if len(proximal_indices) == 0:
        return np.nan

    node_index = proximal_indices[0] + 1

    return _angle_from_down(pts[0], pts[node_index])


def primary_angle_distal(pts: np.ndarray) -> float:
    """Angle from straight down of the bottom part of a root.

    Measured from the base (node 0) to the LAST found node in the second half
    of the root, which is nodes (n_nodes + 1) // 2 to n_nodes - 1. For 6 nodes,
    that is node 5 (the tip), falling back to node 4, then node 3.

    Args:
        pts: One root, shape (n_nodes, 2).

    Returns:
        Degrees in [0, 180] (see `_angle_from_down`). NaN if the base is
        missing, or if no node in that half is found.

    Matches `sleap_roots.angle.get_node_ind` plus `get_root_angle`
    (proximal=False).
    """
    pts = np.array(pts, dtype=float)

    midpoint = (len(pts) + 1) // 2
    is_found = ~np.isnan(pts).any(axis=-1)

    # Positions in this slice are node index - midpoint.
    distal_indices = np.flatnonzero(is_found[midpoint:])

    if len(distal_indices) == 0:
        return np.nan

    node_index = distal_indices[-1] + midpoint

    return _angle_from_down(pts[0], pts[node_index])


def lateral_count(pts: np.ndarray) -> int:
    """Number of lateral roots in one frame.

    Args:
        pts: All lateral roots in the frame, shape (n_laterals, n_nodes, 2).

    Returns:
        n_laterals. Keypoints are not checked, so an all-NaN root still counts.
        An empty frame, shape (0, n_nodes, 2), gives 0.

    Matches `sleap_roots.points.get_count`, except for empty frames: sleap-roots
    stores those as a (1, 2, 2) NaN placeholder, so it reports 1.
    """
    return pts.shape[0]


def primary_tip_pt_y(pts: np.ndarray) -> float:
    """y coordinate of the root's tip (its last node).

    Args:
        pts: One root, shape (n_nodes, 2).

    Returns:
        The tip's y in pixels (larger = lower in the image). NaN if the tip is
        missing. There is no fallback to an earlier node.

    Matches `sleap_roots.tips.get_tips` plus `get_tip_ys`.
    """
    pts = np.array(pts, dtype=float)
    return float(pts[-1, 1])
