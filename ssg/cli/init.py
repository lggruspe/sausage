"""'ssg init' command."""

from pathlib import Path
from shutil import copy2


def init() -> None:
    """Initialize site in current directory.

    Creates:

    - public/
    - src/
    - templates/
    - README.md
    - site.yaml
    """
    data = Path(__file__).parent/"data"
    copy2(data/"README.md", Path("README.md"))
    copy2(data/"site.yaml", Path("site.yaml"))
    Path("src").mkdir(exist_ok=True)
    Path("public").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
