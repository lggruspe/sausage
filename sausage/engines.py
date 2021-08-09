"""Template engines."""

from pathlib import Path
import typing as t

from jinja2 import Environment, FileSystemLoader, StrictUndefined


env = Environment(
    loader=FileSystemLoader(["src", "templates"]),
    undefined=StrictUndefined,
)


def render_jinja(path: Path, context: t.Optional[t.Dict[t.Any, t.Any]]) -> str:
    """Render jinja template."""
    template = env.get_template(str(path))
    return template.render(context)