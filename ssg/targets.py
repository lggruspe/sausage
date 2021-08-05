"""Generate target."""

from itertools import chain
import json
from pathlib import Path
import shlex
import subprocess
from tempfile import NamedTemporaryFile
import typing as t

import yaml

from ssg.engines import render_jinja
from ssg.wildcards import (
    get_wildcard_candidates, has_wildcard, replace_wildcards
)


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
    name: str
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

    def get_globs(self) -> t.Iterable[str]:
        """Extract wildcard patterns used by target.

        Converts '%' into '*' for globbing.
        """
        recipes = iter(self.namespace.values())
        if self.context:
            recipes = chain(recipes, self.context)

        for recipe in recipes:
            for token in shlex.split(recipe.recipe):
                if has_wildcard(token):
                    yield replace_wildcards(token, "*")

    def expand(self) -> t.Optional[t.Iterable["Target"]]:
        """Expand % in target.

        Returns None if target doesn't have %.
        """
        template = str(self.template)
        if not has_wildcard(template):
            return None

        patterns = self.get_globs()
        replacements = set.intersection(map(get_wildcard_candidates, patterns))

        if not replacements:
            return None
        return (
            Target(
                name=replace_wildcards(self.name, replacement),
                template=self.template,
                context=(
                    self.context.with_replaced_wildcards(replacement)
                    if self.context else None
                ),
                namespace={
                    k: v.with_replaced_wildcards(replacement)
                    for k, v in self.namespace.items()
                },
            )
            for replacement in replacements
        )
