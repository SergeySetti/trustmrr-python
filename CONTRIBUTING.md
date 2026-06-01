# Contributing

Thanks for your interest in improving `trustmrr`!

## Setup

```bash
git clone https://github.com/SergeySetti/trustmrr-python.git
cd trustmrr-python
python -m venv .venv
.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # macOS / Linux
pip install -e ".[test]"
```

## Running tests

```bash
pytest
```

All tests run offline — the HTTP layer is mocked. New behavior should come with a test.

## Pull requests

1. Open an issue first for non-trivial changes so we can agree on the approach.
2. Branch from `main`, keep PRs focused on one change.
3. Make sure `pytest` passes locally.
4. Update [README.md](README.md) if you change the public API.
5. Don't bump the version in `pyproject.toml` — that happens at release time.

## Reporting bugs

Open a [GitHub issue](https://github.com/SergeySetti/trustmrr-python/issues) with:
- Python version and OS
- Minimal code to reproduce
- Expected vs. actual behavior (full traceback if there's one)

Don't include your API key in issues or PRs.

## Releasing (maintainers)

Publishing is automated via GitHub Actions + PyPI Trusted Publishing.

1. Bump `version` in [pyproject.toml](pyproject.toml) and [src/trustmrr/__init__.py](src/trustmrr/__init__.py).
2. Commit and push to `main`.
3. Tag the release: `git tag vX.Y.Z && git push origin vX.Y.Z`.
4. The `publish.yml` workflow runs tests, builds, and uploads to PyPI.

## License

By contributing you agree your contributions are licensed under [Apache 2.0](LICENSE).
