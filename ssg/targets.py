"""Generate target."""

import json
from pathlib import Path
import shlex
import subprocess
from tempfile import NamedTemporaryFile
import typing as t

import yaml

from ssg.engines import render_jinja


class ContextRecipe(t.NamedTuple):
    """Recipe to build context for templates."""
    recipe: str     # path in src/ or command

    def eval(self) -> t.Any:
        """Evaluate context in src/."""
        src = Path("src")
        path = src/self.recipe
        if path.is_file():
            text = path.read_text()
            try:
                return json.loads(text)
            except json.decoder.JSONDecodeError:
                return yaml.safe_load(text)
            except yaml.parser.ParserError:
                pass

        with NamedTemporaryFile() as out:
            tokens = [
                out.name if a == "$out" else a
                for a in shlex.split(self.recipe)
            ]
            proc = subprocess.run(
                tokens,
                text=True,
                capture_output=True,
                check=True,
                cwd=src
            )
            return out.read_text() if out.name in tokens else proc.stdout


class Target(t.NamedTuple):
    """File to be generated."""
    template: Path
    context: t.Optional[ContextRecipe] = None
    namespace: t.Dict[str, t.Union[Path, ContextRecipe]] = {}

    def eval_context(self) -> t.Any:
        """"Evaluate template context in src/."""
        context = {} if not self.context else self.context.eval()
        if isinstance(context, dict):
            for name, recipe in self.namespace.items():
                context[name] = recipe.eval()
        return context

    def generate(self) -> str:
        """Generate target from template."""
        context = self.eval_context()
        return render_jinja(self.template, context)
