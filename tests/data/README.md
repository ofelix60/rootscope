# Test data

Test fixtures for rootscope: SLEAP root-pose predictions for two plants, copied unmodified from [talmolab/sleap-roots](https://github.com/talmolab/sleap-roots).

## Source

- **Repository:** https://github.com/talmolab/sleap-roots
- **Commit:** [`6394cb9`](https://github.com/talmolab/sleap-roots/tree/6394cb996a70e7e3f9ebe9c17150a0c423fc0e18/tests/data) (`6394cb996a70e7e3f9ebe9c17150a0c423fc0e18`)
- **Path in source repo:** `tests/data/canola_7do/` and `tests/data/soy_6do/`

## License

These files are © 2022 Talmo Lab at the Salk Institute and are distributed under the BSD 3-Clause License. The full license text is in [`LICENSE-sleap-roots`](LICENSE-sleap-roots), as the license requires. rootscope's own license does not apply to these files.

## Files

Each plant was imaged in a clear cylinder rotating in front of a camera, giving 72 frames of the same plant from different angles. The `.slp` files hold the model's predicted points for each root in each frame. In every skeleton, node 0 is the base and the last node is the tip.

| File | Plant | Roots | Frames | Nodes per root | Roots per frame |
|---|---|---|---|---|---|
| `canola_7do/919QDUH.primary.predictions.slp` | canola, 7 days old | primary | 72 | 6 | 1–2 |
| `canola_7do/919QDUH.lateral.predictions.slp` | canola, 7 days old | lateral | 72 | 3 | 3–6 |
| `soy_6do/6PR6AA22JK.primary.predictions.slp` | soybean, 6 days old | primary | 72 | 6 | 1 |
| `soy_6do/6PR6AA22JK.lateral.predictions.slp` | soybean, 6 days old | lateral | 72 | 4 | 5–11 |

Things to know when using them:

- **Missing points are NaN.** The model often misses the base (node 0).
- **No tracks.** `labels.tracks` is empty, so `labels.numpy()` returns zero instances by default. Read the data frame by frame instead.
- **Not the same root across frames.** Instance order within a frame is arbitrary.
- **Canola primary, frames 66–71:** the main root wastwo instances).
- **Videos not included.** The `.h5` image files (~32he points load without them.

## Why two plants

Canola and soybean have different root architectures.ch sleap-roots on both, it's unlikely to be acoincidence of one dataset.

## Why not Git LFS

The four files total about 220 KB. LFS adds setup cosd CI run, and is only worth it for large files like
the source repo's 32 MB `.h5` videos.

## Checksums (SHA-256)

```
1b393942cca2768a3fc368762eaddf81e1f65ef6e1ddee143b5ab75a4636d688  canola_7do/919QDUH.lateral.predictions.slp
8a9492cc5798c42667d1a54e84105e93f3501b83b3c40dba6b69f9QDUH.primary.predictions.slp
c82362f6574691a135805f57aa08ff58726c66a9104f8353e61314a42b7ad552  soy_6do/6PR6AA22JK.lateral.predictions.slp
d6279eca98566360c91fd54a24575047d4061518dfeff6ccf5cc9A22JK.primary.predictions.slp
```

To verify: `cd tests/data && shasum -a 256 -c <<< "$(' README.md)"`
