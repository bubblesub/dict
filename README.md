dict
====

A command line toolkit for online dictionary lookups.

Currently supports:

- WordHippo (https://www.wordhippo.com/)
- Edict2 (http://www.edrdg.org/jmdictdb/)
- JMdict (http://www.edrdg.org/jmdictdb/)
- Jisho (https://jisho.org/)
- reverso (https://www.reverso.net/)
- Urban Dictionary (https://www.urbandictionary.com/)
- Słownik Języka Polskiego (https://sjp.pl/)
- Synonim.net (https://synonim.net/)

## Installation

```
pip install --user dict
```

# Contributing

```sh
# Clone the repository:
git clone https://github.com/bubblesub/dict.git
cd dict

# Install to a local venv:
poetry install

# Install pre-commit hooks:
poetry run pre-commit install

# Enter the venv:
poetry shell
```

This project uses [poetry](https://python-poetry.org/) for packaging,
install instructions at [poetry#installation](https://python-poetry.org/docs/#installation)
