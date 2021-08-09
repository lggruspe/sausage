# pylint: disable=missing-function-docstring,redefined-outer-name
"""Test sausage.build."""

from pathlib import Path

import pytest

from sausage.build import build


@pytest.fixture
def site_root(tmp_path: Path) -> Path:
    """Initialize minimal site with empty site.yaml, src/ and public/."""
    (tmp_path/"site.yaml").touch()
    (tmp_path/"src").mkdir()
    (tmp_path/"public").mkdir()
    return tmp_path


def test_build_copies_unignored_files_in_src(site_root: Path) -> None:
    content = "<p>Hello, world!</p>"
    (site_root/"site.yaml").write_text("ignore: []")
    (site_root/"src"/"index.html").write_text(content)

    public = site_root/"public"
    assert not list(public.iterdir())

    build(site_root)

    index_html = public/"index.html"
    assert list(public.iterdir()) == [index_html]
    assert index_html.read_text() == content


def test_build_does_not_copy_ignored_paths(site_root: Path) -> None:
    (site_root/"site.yaml").write_text("ignore: ['bar.html', 'baz']")

    src = site_root/"src"
    (src/"foo.html").write_text("<p>Foo</p>")
    (src/"bar.html").write_text("<p>Bar</p>")
    (src/"baz").mkdir()

    build(site_root)

    public = site_root/"public"
    foo_html = public/"foo.html"
    assert list(public.iterdir()) == [foo_html]


def test_build_generates_simple_targets(site_root: Path) -> None:
    (site_root/"site.yaml").write_text(
        """
        targets:
          index.html:
            template: index.html
        """
    )
    (site_root/"src"/"index.html").write_text(
        "{% for i in range(5) %}a{% endfor %}"
    )

    build(site_root)

    public = site_root/"public"
    index_html = public/"index.html"

    assert list(public.iterdir()) == [index_html]
    assert index_html.read_text() == "a" * 5


def test_build_generates_targets_with_wildcards(site_root: Path) -> None:
    (site_root/"site.yaml").write_text(
        """
        ignore: ["post.html", "**/*.md"]
        targets:
          "%.html":
            template: post.html
            with:
              content: "%.md"
        """
    )
    src = site_root/"src"
    (src/"post.html").write_text("{{ content }}")
    (src/"foo.md").write_text("Foo")
    (src/"bar.md").write_text("Bar")
    (src/"baz.md").write_text("Baz")

    build(site_root)

    public = site_root/"public"

    children = list(public.iterdir())
    assert len(children) == 3

    for expected in ["foo", "bar", "baz"]:
        child = public/f"{expected}.html"
        assert child in children
        assert child.read_text() == expected.capitalize()


def test_build_uses_json_context(site_root: Path) -> None:
    (site_root/"site.yaml").write_text(
        """
        ignore: ["index.json"]
        targets:
          index.html:
            template: index.html
            context: index.json
        """
    )

    src = site_root/"src"
    (src/"index.html").write_text("{{ message }}")
    (src/"index.json").write_text('{ "message": "Hello, world!" }')

    build(site_root)

    public = site_root/"public"
    index_html = public/"index.html"
    assert list(public.iterdir()) == [index_html]
    assert index_html.read_text() == "Hello, world!"


def test_build_uses_yaml_context(site_root: Path) -> None:
    (site_root/"site.yaml").write_text(
        """
        ignore: ["index.yaml"]
        targets:
          index.html:
            template: index.html
            context: index.yaml
        """
    )

    src = site_root/"src"
    (src/"index.html").write_text("{{ message }}")
    (src/"index.yaml").write_text(
        """
        message: Hello, world!
        """
    )

    build(site_root)

    public = site_root/"public"
    index_html = public/"index.html"
    assert list(public.iterdir()) == [index_html]
    assert index_html.read_text() == "Hello, world!"


def test_build_with_context_command(site_root: Path) -> None:
    (site_root/"site.yaml").write_text(
        """
        targets:
          index.html:
            template: index.html
            with:
              message: python -c 'print("Hello, world!", end="")'
        """
    )
    (site_root/"src"/"index.html").write_text("{{ message }}")

    build(site_root)

    public = site_root/"public"
    index_html = public/"index.html"

    assert list(public.iterdir()) == [index_html]
    assert index_html.read_text() == "Hello, world!"
