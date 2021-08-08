"""sausage command-line interface."""

from argparse import ArgumentParser

from sausage.build import build
from sausage.init import init


def create_parser() -> ArgumentParser:
    """Create sausage CLI parser."""
    description = "A flexible template-based static site generator."
    parser = ArgumentParser("sausage", description=description)
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(callback=init)

    build_parser = subparsers.add_parser("build")
    build_parser.set_defaults(callback=build)
    return parser


def main() -> None:
    """Sausage entrypoint."""
    parser = create_parser()
    args = parser.parse_args()
    if args.callback:
        args.callback()


if __name__ == "__main__":
    main()
