# rootscope

[![CI](https://github.com/ofelix60/rootscope/actions/workflows/ci.yml/badge.svg)](https://github.com/ofelix60/rootscope/actions/workflows/ci.yml)

Compute plant root traits from [SLEAP](https://sleap.ai) root-pose predictions, using [sleap-io](https://github.com/talmolab/sleap-io), NumPy and pandas.

rootscope re-implements five per-frame traits from [sleap-roots](https://github.com/talmolab/sleap-roots)' `DicotPipeline` in a few hundred lines with no sleap-roots dependency, and checks them against sleap-roots on every CI run.

## Install

From TestPyPI (its dependencies come from PyPI):

```bash
uv pip install rootscope \
  --index https://test.pypi.org/simple/ --index-strategy unsafe-best-match
```

Or from source:

```bash
git clone https://github.com/ofelix60/rootscope && cd rootscope && uv sync
```

Requires Python 3.12+.

## Usage

```python
import rootscope

traits = rootscope.compute_traits(
    "919QDUH.primary.predictions.slp",
    "919QDUH.lateral.predictions.slp",
)
```

One row per frame:

```
 frame_idx  primary_length  primary_angle_proximal  primary_angle_distal  lateral_count  primary_tip_pt_y
         0          971.05                   50.13                  7.75              5           1020.98
         1          967.77                   49.43                  7.27              3           1020.25
         2          971.48                   49.55                  6.98              4           1020.00
```

## Traits

Lengths and coordinates are in pixels; angles are in degrees. If a frame has more than one primary root, the longest one is used.

| Column | Meaning |
|---|---|
| `primary_length` | Sum of the distances between consecutive nodes. A segment touching a missing node is skipped, not bridged. |
| `primary_angle_proximal` | Angle from straight down (0 = down, 90 = sideways, 180 = up) from the base to the first found node in the root's first half. |
| `primary_angle_distal` | The same, to the last found node in the root's second half. |
| `lateral_count` | Number of lateral roots in the frame. |
| `primary_tip_pt_y` | y of the last node (the tip). Image y grows downward, so larger = deeper. |

Missing keypoints are NaN, and a trait that can't be computed (for example, an angle with no base) is NaN.

**Input assumptions:** one skeleton per file, node 0 = base and the last node = tip, and every instance in a frame counts (user-labelled and predicted alike).

## Validation

`tests/test_vs_sleap_roots.py` runs sleap-roots 0.1.4's `DicotPipeline` and rootscope on the same files and compares all five columns frame by frame, with `atol=1e-7` (the tolerance sleap-roots' own tests use). The test data is the canola and soybean predictions from the sleap-roots test suite, 72 frames each.

**Result:** all five columns match on both plants.

Known differences, neither of which occurs in the test data:

- **Zero-length angle.** If the node used for an angle sits exactly on the base, rootscope returns NaN (no direction). sleap-roots returns 90°, because `arctan2(0, 0) = 0`.
- **Empty lateral frame.** A frame with no lateral roots gives `lateral_count = 0`. sleap-roots stores an empty frame as a single all-NaN placeholder, so it reports 1.

One thing to know about the data: in canola frames 66–71 the primary root was detected in two pieces. Like sleap-roots, rootscope uses the longer piece, so `primary_length` is shorter than the whole root in those frames.

## Development

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

CI runs the same commands on every push and pull request.

## License

BSD-3-Clause. The files in `tests/data/` come from sleap-roots and keep their own license; see [`tests/data/README.md`](tests/data/README.md).
