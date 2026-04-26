# Testing

The default test suite is credential-free and must not call the live PrintNode API.

Run tests with:

```sh
uv run pytest
```

Package verification uses the same checks as CI:

```sh
uv run pytest
uv build
uv run twine check dist/*
```

Live PrintNode API tests may be added later, but they must be opt-in and gated by explicit environment variables. Do not commit real API keys, account credentials, customer data, or live API fixtures.
