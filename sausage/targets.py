"""Generate target."""

from itertools import chain
import json
from pathlib import Path
import shlex
import subprocess
from tempfile import NamedTemporaryFile
import typing as t

import yaml

from sausage.engines import JinjaEngine
from sausage.wildcards import (
    get_wildcard_candidates, has_wildcard, replace_wildcards
)


class ContextRecipe(t.NamedTuple):
    """Recipe to build context for templates."""
    recipe: str     # path in src/ or command

    def with_replaced_wildcards(self, replacement: str) -> "ContextRecipe":
        """Construct ContextRecipe with replaced '%'s."""
        recipe = replace_wildcards(self.recipe, replacement)
        return ContextRecipe(recipe)

    def eval(self, root: Path) -> t.Any:
        """Evaluate context in root/src/."""
        src = root/"src"
        path = src/self.recipe
        if path.is_file():
            text = path.read_text()
            try:
                return json.loads(text)
            except json.decoder.JSONDecodeError:
                return yaml.safe_load(text)
            except yaml.parser.ParserError:
                pass

        with NamedTemporaryFile() as temp_file:
            out = Path(temp_file.name)
            tokens = [
                str(out) if a == "$out" else a
                for a in shlex.split(self.recipe)
            ]
            proc = subprocess.run(
                tokens,
                text=True,
                capture_output=True,
                check=True,
                cwd=src
            )
            return out.read_text() if str(out) in tokens else proc.stdout


class Target(t.NamedTuple):
    """File to be generated."""
    name: str
    template: Path
    context: t.Optional[ContextRecipe] = None
    namespace: t.Dict[str, ContextRecipe] = {}

    def eval_context(self, root: Path) -> t.Any:
        """"Evaluate template context in root/src/."""
        context = {} if not self.context else self.context.eval(root)
        if isinstance(context, dict):
            for name, recipe in self.namespace.items():
                context[name] = recipe.eval(root)
        return context

    def generate(self, root: Path) -> str:
        """Generate target from template."""
        engine = JinjaEngine(root)
        context = self.eval_context(root)
        return engine.render(self.template, context)

    def get_globs(self) -> t.Iterable[str]:
        """Extract wildcard patterns used by target.

        Converts '%' into '*' for globbing.
        """
        recipes = chain(
            self.namespace.values(),
            [self.context] if self.context else [],
        )
        for recipe in recipes:
            for token in shlex.split(recipe.recipe):
                if has_wildcard(token):
                    yield replace_wildcards(token, "*")

    def expand(self, root: Path) -> t.Iterator["Target"]:
        """Expand into concrete targets.

        E.g. % gets replaced with appropriate values.
        If the target doesn't have %, then it only yields itself.
        """
        if not has_wildcard(self.name):
            yield self
            return

        patterns = self.get_globs()
        replacements = set.intersection(
            *(set(get_wildcard_candidates(root, p)) for p in patterns)
        )
        yield from (
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
