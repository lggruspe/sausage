"""Generate target."""

import json
from pathlib import Path
import shlex
import subprocess
from tempfile import NamedTemporaryFile
import typing as t

import yaml

from ssg.engines import render_jinja


def find_wildcards(string: str) -> t.Iterable[int]:
    """Find '%'s in string."""
    i = len(string)
    while i >= 0:
        j = string.rfind("%", 0, i)
        if j == 0 or string[j - 1] != "%":
            yield j
        i = j


def replace_wildcards(string: str, replacement: str) -> str:
    """Replace '%'s in string."""
    for i in find_wildcards(string):
        string = f"{string[:i]}{replacement}{string[i+1:]}"
    return string


def has_wildcard(string: str) -> bool:
    """Check if string has '%'s."""
    try:
        return next(find_wildcards(string))
    except StopIteration:
        return False


class ContextRecipe(t.NamedTuple):
    """Recipe to build context for templates."""
    recipe: str     # path in src/ or command

    def with_replaced_wildcards(self, replacement: str) -> "ContextRecipe":
        """Construct ContextRecipe with replaced '%'s."""
        recipe = replace_wildcards(self.recipe, replacement)
        return ContextRecipe(recipe)

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

    def expand(self) -> t.Optional[t.Iterable["Target"]]:
        """Expand % in target.

        Returns None if target doesn't have %.
        """
        template = str(self.template)
        if not has_wildcard(template):
            return None

        recipes = list(self.namespace.values())
        if self.context:
            recipes.append(self.context.recipe)
        patterns = [
            replace_wildcards(t, "*")
            for r in recipes for t in shlex.split(r.recipe)
            if has_wildcard(t)
        ]

        # replacement shouldn't be ...
        src = Path("src")
        return (
            Target(
                template=self.template,
                context=(
                    self.context.with_replaced_wildcards(...)
                    if self.context else None
                ),
                namespace={
                    k: v.with_replaced_wildcards(...)
                    for k, v in self.namespace.items()
                },
            )
            for result in set.intersection(src.glob(p) for p in patterns)
        )
