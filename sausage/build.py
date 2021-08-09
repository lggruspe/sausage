"""'sausage build' command."""

from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from sausage.config import Config


def clear(directory: Path) -> None:
    """Clear contents of directory."""
    assert directory.is_dir()
    for child in directory.iterdir():
        if child.is_dir():
            clear(child)
            child.rmdir()
        elif child.is_file():
            child.unlink(missing_ok=True)


def build(root: Path) -> None:
    """Generate site in public/.

    Assumes the site has been initialized.
    """
    config = Config.read(root/"site.yaml")
    with TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        shutil.copytree(root/"src", tmp, dirs_exist_ok=True)

        for target in config.targets.values():
            for targ in target.expand(root):
                (tmp/targ.name).write_text(targ.generate(root))

        public = root/"public"
        public.mkdir(exist_ok=True)
        clear(public)
        for child in tmp.iterdir():
            shutil.move(child, public)
        for pattern in config.ignore:
            for path in public.glob(pattern):
                if path.is_dir():
                    clear(path)
                    path.rmdir()
                if path.is_file():
                    path.unlink()
