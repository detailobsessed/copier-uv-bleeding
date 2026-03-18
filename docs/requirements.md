# Requirements

To use this Copier template, you will need:

- [Git v2](https://git-scm.com/)
- [Python 3.14+](https://www.python.org) (bleeding edge)
- [Copier](https://copier.readthedocs.io/en/stable/)

To install Git version 2, [follow the official instructions](https://git-scm.com/downloads).

To install Python 3.14, use [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.14
```

To install Copier, use [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install copier --with copier-template-extensions
```
