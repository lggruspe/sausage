"""Template renderer."""

import json
from pathlib import Path
import typing as t

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template


env = Environment(
    loader=FileSystemLoader(["", "templates"]),
    undefined=StrictUndefined,
)


def load_context_from_file(path: Path) -> t.Dict[str, t.Any]:
    """Load json from file."""
    if not path.is_file():
        return {}
    return json.loads(path.read_text())


def find_context(template: Template) -> Path:
    """Look for template context.

    - If template is in templates/, looks in data/.
    - Otherwise, looks the same directory as template.
    """
    path = Path(template.filename)
    templates = Path("templates")
    if templates.is_dir() and templates in path.parents:
        path = Path("data")/path.relative_to(templates)
    return path.parent/(path.name + ".json")


def get_context(template: Template) -> t.Dict[str, t.Any]:
    """Get context mapping for template."""
    return load_context_from_file(find_context(template))


def render_from_file(path: Path) -> str:
    """Get template and context from path and render.

    Note: only the entrypoint's context is used.
    """
    template = env.get_template(path)
    context = get_context(template)
    return template.render(context)
