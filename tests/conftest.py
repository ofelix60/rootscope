from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


CANOLA_PRIMARY_SLP = DATA_DIR / "canola_7do" / "919QDUH.primary.predictions.slp"
CANOLA_LATERAL_SLP = DATA_DIR / "canola_7do" / "919QDUH.lateral.predictions.slp"
SOY_PRIMARY_SLP = DATA_DIR / "soy_6do" / "6PR6AA22JK.primary.predictions.slp"
SOY_LATERAL_SLP = DATA_DIR / "soy_6do" / "6PR6AA22JK.lateral.predictions.slp"


@pytest.fixture
def canola_primary_slp() -> Path:
    return CANOLA_PRIMARY_SLP


@pytest.fixture
def canola_lateral_slp() -> Path:
    return CANOLA_LATERAL_SLP


@pytest.fixture
def soy_primary_slp() -> Path:
    return SOY_PRIMARY_SLP


@pytest.fixture
def soy_lateral_slp() -> Path:
    return SOY_LATERAL_SLP


@pytest.fixture(scope="module", params=["canola", "soy"])
def plant_paths(request: pytest.FixtureRequest) -> tuple[str, Path, Path]:
    """(series_name, primary_path, lateral_path) for each plant, one per param."""
    pairs = {
        "canola": ("919QDUH", CANOLA_PRIMARY_SLP, CANOLA_LATERAL_SLP),
        "soy": ("6PR6AA22JK", SOY_PRIMARY_SLP, SOY_LATERAL_SLP),
    }
    return pairs[request.param]
