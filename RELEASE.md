# Release Process

This fork is being prepared for maintained releases, but publishing is blocked until the distribution-name and PyPI ownership decision is complete.

## Current Release Blocker

The historical PyPI distribution name is `PrintNodeApi`. Do not publish until one of these paths is confirmed:

- PyPI maintainer access is granted for `PrintNodeApi`; or
- the fork chooses and tests a distinct distribution name, such as `printnode-api`, while preserving the `printnodeapi` import package.

## Versioning

Use semantic versioning once maintained releases begin.

- Patch releases: bug fixes, packaging fixes, documentation corrections, and compatibility fixes that preserve public API behavior.
- Minor releases: new PrintNode API coverage, new optional features, or deprecations that preserve compatibility.
- Major releases: breaking API changes, import-path changes, or removal of documented compatibility.

Keep the package version in `pyproject.toml` and the top `CHANGELOG.md` release section in sync.

## Pre-Release Checklist

1. Confirm the package name and PyPI/TestPyPI trusted publisher configuration.
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

Use a clean environment and the chosen distribution name:

```sh
uv venv /tmp/printnodeapi-release-smoke
source /tmp/printnodeapi-release-smoke/bin/activate
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ <distribution-name>
python -c "from printnodeapi import Gateway; print(Gateway.__name__)"
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
