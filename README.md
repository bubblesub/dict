template_project
================

This is a template that I use for a typical vanilla Python project. Includes:

- MIT license
- CLI endpoint template
- pre-commit configuration
    - black
    - isort
    - pylint
    - mypy
- setup.cfg template
- type hints stubs (PEP-561)
- GitHub actions template
- Makefile with

To use it:
- copy the directory tree
- replace every `template_project` occurrence with a name of your project
- replace every `Author Name` occurrence with your name
- change README.md
- change the `description` in `setup.cfg`
- go through Makefile and setup.cfg.

## Installation

```
pip install --user template_project
```

## Contributing

This project uses [precommit](https://pre-commit.com/). You can install it with
`python3 -m pip install --user pre-commit` and running `pre-commit install`.
