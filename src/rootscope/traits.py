import numpy as np


# 1
def primary_length(pts: np.ndarray) -> float:
    pts = np.array(pts, dtype=float)

    gaps = np.diff(pts, axis=0)
    distances = np.linalg.norm(gaps, axis=1)
    if np.all(np.isnan(distances)):
        return np.nan
    return float(np.nansum(distances))


# 3
def lateral_count(pts: np.ndarray) -> int:
    pts = np.array(pts, dtype=float)

    return pts.shape[0]
