import shutil

import pytest


@pytest.fixture(scope="session")
def fixtures_dir():
    from pathlib import Path
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def headers_dir(fixtures_dir):
    return fixtures_dir / "headers"


@pytest.fixture
def parse_args():
    return ["-x", "c", "-std=c11"]


@pytest.fixture
def has_gcc():
    return shutil.which("gcc") is not None
