"""ssg entrypoint."""

from argparse import ArgumentParser
from ssg import render_from_file


def main():
    """ssg entrypoint."""
    description = "Create static sites using Jinja2 templates."
    parser = ArgumentParser("ssg", description=description)
    parser.add_argument("template")
    args = parser.parse_args()
    print(render_from_file(args.template))


if __name__ == "__main__":
    main()
