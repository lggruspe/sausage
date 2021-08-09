"""Template engines."""

from pathlib import Path
import typing as t

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class JinjaEngine:  # pylint: disable=too-few-public-methods
    """Jinja template engine."""
    def __init__(self, root: Path):
        self.env = Environment(
            loader=FileSystemLoader([root/"src", root/"templates"]),
            undefined=StrictUndefined,
        )

    def render(self, path: Path, context: t.Optional[t.Dict[t.Any, t.Any]]
               ) -> str:
        """Render jinja template."""
        template = self.env.get_template(str(path))
        return template.render(context)
