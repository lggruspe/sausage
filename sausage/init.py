"""'sausage init' command."""

from pathlib import Path
from shutil import copy2


def init(root: Path) -> None:
    """Initialize site in root directory.

    Creates:

    - public/
    - src/
    - templates/
    - README.md
    - site.yaml
    """
    assert root.is_dir()

    data = Path(__file__).parent/"data"
    copy2(data/"README.md", root/"README.md")
    copy2(data/"site.yaml", root/"site.yaml")
    (root/"src").mkdir(exist_ok=True)
    (root/"public").mkdir(exist_ok=True)
    (root/"templates").mkdir(exist_ok=True)

    src = root/"src"
    copy2(data/"_index.html", src)
    copy2(data/"_index.html.json", src)
    copy2(data/"_index.md", src)
    copy2(data/"_index.footer.md", src)

    (src/"posts").mkdir(exist_ok=True)
    copy2(data/"posts"/"_post.html", src/"posts")
