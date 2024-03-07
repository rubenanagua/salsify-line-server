## Line server

#### Requirements

This problem requires Python 3.9+ and Poetry.

If Poetry is not installed, look into its [documentation](https://python-poetry.org/docs/) for instructions on how to install it.

#### Testing

Preparation: navigate to the project root and run `build.sh`

Run unit tests:

```shell
poetry run python -m unittest discover tests/unit -p "test_*.py"
```

Run integration tests:

```shell
poetry run python -m unittest discover tests/integration -p "test_*.py"
```
