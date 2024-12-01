from pathlib import Path


def main():
    """
    Render the README.md file using the README.md.jinja2 template.

    Requires following PyPi packages:
    - 'jinja2'

    Returns non-zero on failure.
    """

    try:
        from jinja2 import Environment

        file = Path("docs/README.md.jinja2")
        readme = file.with_suffix("")

        env = Environment(
            keep_trailing_newline=True,
        )
        env.filters["include"] = lambda f: Path(f).read_text().strip()

        template = env.from_string(file.read_text())

        with open(readme.name, "w") as f:
            f.write(template.render())

    except Exception as e:
        print(f"{readme=} creation failed!\n\t{e}")
        return 1

    print(f"{readme=} created successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
