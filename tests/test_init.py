# pylint: disable=missing-function-docstring
"""Test sausage.init."""

from pathlib import Path

from sausage.init import init


def test_init_creates_files_in_root(tmp_path: Path) -> None:
    assert not list(tmp_path.iterdir())
    init(tmp_path)
    assert (tmp_path/"site.yaml").is_file()
