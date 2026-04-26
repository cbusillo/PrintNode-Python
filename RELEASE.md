# Release Process

This fork is being prepared for maintained releases under the `printnode-community` distribution name. The import package is `printnode_community`.

## Package Name

The historical PyPI distribution name is `PrintNodeApi`, but upstream has not responded to maintainer handoff requests. This community-maintained fork will publish as `printnode-community` instead.

PyPI normalizes `printnode-community` and `printnode_community` as the same project name. Prefer documenting `uv add printnode_community` and `python -m pip install printnode_community` so the install command visually matches the `printnode_community` import namespace.

Before the first release, verify that `printnode-community` is still available on both PyPI and TestPyPI, then configure trusted publishing for that name.

## Versioning

Use semantic versioning once maintained releases begin.

- Patch releases: bug fixes, packaging fixes, documentation corrections, and compatibility fixes that preserve public API behavior.
- Minor releases: new PrintNode API coverage, new optional features, or deprecations that preserve compatibility.
- Major releases: breaking API changes, import-path changes, or removal of documented compatibility.

Keep the package version in `pyproject.toml` and the top `CHANGELOG.md` release section in sync.

## Pre-Release Checklist

1. Confirm `printnode-community` is still available and PyPI/TestPyPI trusted publisher configuration is ready.
2. Confirm `main` is green in CI.
3. Create a release branch from `main`.
4. Update `pyproject.toml` with the release version.
5. Update `CHANGELOG.md` by moving relevant `Unreleased` entries under the release version and date.
6. Run local verification:

```sh
uv sync --locked
uv run pytest
rm -rf dist && uv build
uv run twine check dist/*
```

7. Open a release PR and wait for required CI checks.
8. Merge the release PR.
9. Create a signed Git tag if signing is configured; otherwise create an annotated tag:

```sh
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

10. Create a GitHub Release from the tag using the changelog section as release notes.
11. Run the manual `Publish` workflow for TestPyPI first.
12. Install from TestPyPI in a clean environment and smoke-test imports.
13. Run the manual `Publish` workflow for PyPI only after TestPyPI passes.

## TestPyPI Smoke Test

Use a clean environment:

```sh
uv venv /tmp/printnode_community-release-smoke
source /tmp/printnode_community-release-smoke/bin/activate
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ printnode_community
python -c "from printnode_community import Gateway; print(Gateway.__name__)"
deactivate
```

## GitHub Environments

Configure two GitHub environments before publishing:

- `testpypi`
- `pypi`

Both environments should require manual approval. Configure each environment as a trusted publisher in the corresponding PyPI project before running the workflow.

The `Publish` workflow uses GitHub OpenID Connect through `id-token: write`; do not add PyPI API tokens unless trusted publishing is unavailable.

## Rollback

Published packages cannot be overwritten. If a bad release is published:

- yank the release on PyPI if appropriate;
- document the issue in `CHANGELOG.md` and GitHub Releases;
- publish a new patch release with the fix.
