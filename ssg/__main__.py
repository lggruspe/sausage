"""ssg command-line interface."""

from argparse import ArgumentParser

from ssg.build import build
from ssg.init import init


DESCRIPTION = "Create static sites using Jinja2 templates."

parser = ArgumentParser("ssg", description=DESCRIPTION)
subparsers = parser.add_subparsers()

init_parser = subparsers.add_parser("init")
init_parser.set_defaults(callback=init)

build_parser = subparsers.add_parser("build")
build_parser.set_defaults(callback=build)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.callback:
        args.callback()
