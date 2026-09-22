# Contributing

Thanks for helping improve Schema Compare.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and install with `python -m pip install -e . pytest`.
3. Add or update tests for behavior changes.
4. Run `python -m compileall -q src` and `pytest -q`.
5. Keep changes dependency-light, deterministic, and cross-platform.
6. Open a pull request explaining the problem, solution, and validation performed.

Please avoid committing databases containing personal, confidential, or production data.
