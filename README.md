## Line server

### How it works

This line server was built with [FastAPI](https://fastapi.tiangolo.com/) as the web framework, with asyncio to
make concurrency possible.

The path of the file to serve is provided via env var `FILE_PATH_TO_SERVE` to the system, and this env var is created
automatically when running the system via the provided `run.sh` shell script.

A pre-processing step is executed to speed up requests. This step consists in reading the entire file, one line at a 
time, and keeping track of the number of bytes read before a given line starts in a list. For instance, a file with
the contents being `ABC\nDEFG\nHI\n` would be read, one line at a time, resulting in the list `[0, 4, 9]` being
stored. When a request is received for the line of index 2, the system will consult this list and skip the first 9
bytes of the file, reading it until a newline character is found: `HI\n`.

This ensures that performance remains acceptable even with very large files.

#### Running

As required, the project can be built by running `./build.sh`. This will execute a `poetry install` command.
To run it, use the following command from the project root:

```shell
./run.sh PATH_TO_FILE
```

Where `PATH_TO_FILE` is the path to the file to serve. This is a mandatory parameter, and the shell script will exit 
with an error if it is not provided. If you do not have a test file, look into the section below as you can easily 
generate some. This file is assumed to only contain ASCII characters represented by a single byte.

The application will run on port 8000.
- OpenAPI documentation of all endpoints (a single one!): http://localhost:8000/docs
- Request the first line of the served file: http://localhost:8000/lines/0

### Performance with large files

To facilitate the generation of files, a file generation script was provided. The following is an usage example to
create a file with 1M lines, and a random number of characters per line between 0 and 2000, resulting in a file size
of around ~1 GB:

```shell
python file_generator.py .test1gb.txt -l 1000000 -c 2000
```

Due to the pre-processing step, and the fact that list lookups by index are of linear time complexity (O(1)), requests
are handled instantly. The index of the requested line is irrelevant in this regard, as it takes the same time to
retrieve the first line (index 0) or the millionth line.

As such, a more interesting calculation is checking how long the pre-processing step takes as the size of the served 
file varies:

| File size  | Time    |
|------------|---------|
| 10 MB      | 0.009 s |
| 100 MB     | 0.067 s |
| 1 GB       | 0.665 s |
| 10 GB      | 7.437 s |

These tests can be replicated by creating files with the included file generation script, loading the application with 
a file of your choosing, and waiting for a log message stating that the file is loaded in X seconds.

This table shows that the pre-processing time increases with the size of the file to serve in a linear fashion, and it
should be possible to pre-process these values to 100 GB or 1 TB files, as long as the resulting array fits into 
memory.

### Performance with many users

Due to the pre-processing step, requests are handled in a time that is perceived as instant, even with 10 or 100 users 
performing simultaneous requests on a single worker. By using FastAPI with asyncio, requests should not block the main
thread, allowing the application to serve many users.

While tests with thousands of simultaneous requests were not performed, the performance of this application should be 
improvable simply by starting the application with several workers (this can be done with the `--workers` parameter).
Different workers should be subject to different GIL (Global Interpreter Lock) instances, meaning true parallelization
should be possible. However, this scenario was not tested as this could represent a significant time investment.

### Sources (documentation, websites, papers, ...)

The most important source was the documentation of [FastAPI](https://fastapi.tiangolo.com/) for two reasons: to 
understand how it works under the hood, and to get re-acquainted with the framework's classes and functionality.

In addition, the official documentation pages of some built-in libraries (such as 
[tempfile](https://docs.python.org/3/library/tempfile.html) and
[asyncio](https://docs.python.org/3/library/asyncio.html)) were also consulted.

### Third-party libraries/tools

An obvious third-party tool is Poetry as the package and dependency manager. Poetry simplifies isolation from other
projects by automatically managing virtual environments, and updating dependencies while ensuring their compatibility
is generally free of any pains.

FastAPI was chosen as the web framework as it is rising in popularity due to its asynchronous capabilities as well as
its easy integration with data validation libraries like [Pydantic](https://docs.pydantic.dev/latest/). While this 
may not seem to be too important due to the simplicity of the requirements for this project, it helps lay out a
great foundation that would be easily extendable and maintainable. A good alternative would be Flask.

[Uvicorn](https://www.uvicorn.org/) was used as the web server implementation. To be honest, I didn't dig too deep in 
comparisons with other frameworks, as it did not feel like a good investment of my time -- it's very easy to switch
to another implementation with near-zero changes in the source code if desired.

### Time constraints

Around 5 hours were spent in the exercise, including 1-1.5 hours spent writing this file. Perhaps an hour or slightly 
more could've been shaved off if I had more experience with FastAPI.

If time were not a constraint, the following would've been looked into:
- Unit tests would've been re-written to reduce code repetition
- Performance with many users and scalability with more workers would've been analyzed in detail
- The pre-processing step could be re-evaluated. Instead of occurring once per app instance, it could occur only once
at all if the list containing the number of bytes before each line were stored in a file or database
- A CI pipeline would've been added with a linter and validation of unit/integration tests

### Code critique

I am proud of the written solution, and principles like single-responsibility and isolation are respected.
A unit test suite with great code coverage is provided, and the needed integration tests to ensure that the API
works as required are provided as well.

The chosen web framework allows for easy extension of the project, either via more endpoints in the same domain 
(serving lines of a file), or via different domains, by adding more routers to append to the main application.

The pre-processing step could've been improved as it is a synchronous step, executed once per app instance, and the 
resulting array needs to be kept track of for the entire execution time. This makes a stateless approach impossible. 
However, the performance of this step is perfectly acceptable as it increases linearly with file size. In my opinion,
it wouldn't be a big issue for now, but it would need to be looked into again before any significant extension of
this solution.

The provided code is documented, including documentation on OpenAPI. I would not expect significant frustration or 
difficulties if another developer would have to extend or improve on this solution.

### Requirements

This problem requires Python 3.9+ and Poetry.

If Poetry is not installed, look into its [documentation](https://python-poetry.org/docs/) for instructions on how
to install it.

### Testing

Preparation: navigate to the project root and run `build.sh`

Run unit tests:

```shell
poetry run python -m unittest discover tests/unit -p "test_*.py"
```

Run integration tests:

```shell
poetry run python -m unittest discover tests/integration -p "test_*.py"
```
