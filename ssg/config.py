"""site.yaml manager."""

from pathlib import Path
import typing as t

import yaml

from ssg.targets import ContextRecipe, Target


class Config(t.NamedTuple):
    """ssg Config."""
    ignore: t.List[Path]
    targets: t.Dict[str, Target]

    @staticmethod
    def from_dict(mapping: t.Dict[str, t.Any]) -> "Config":
        """Construct Config from dict."""
        ignore = mapping.get("ignore", [])
        targets = mapping.get("targets", {})
        return Config(
            ignore,
            {
                k: Target(
                    name=k,
                    template=Path(v["template"]),
                    context=(
                        ContextRecipe(v["context"]) if "context" in v else None
                    ),
                    namespace={
                        a: ContextRecipe(b)
                        for a, b in v.get("with", {}).items()
                    },
                )
                for k, v in targets.items()
            },
        )

    @staticmethod
    def read(path: t.Union[str, Path]) -> "Config":
        """Read config from file."""
        return Config.from_dict(yaml.load(Path(path).read_text()))
