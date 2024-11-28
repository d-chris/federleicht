# federleicht

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/federleicht)](https://pypi.org/project/federleicht/)
[![PyPI - Version](https://img.shields.io/pypi/v/federleicht)](https://pypi.org/project/federleicht/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/federleicht)](https://pypi.org/project/federleicht/)
[![PyPI - License](https://img.shields.io/pypi/l/federleicht)](https://raw.githubusercontent.com/d-chris/federleicht/main/LICENSE)
[![GitHub - Pytest](https://img.shields.io/github/actions/workflow/status/d-chris/federleicht/pytest.yml?logo=github&label=pytest)](https://github.com/d-chris/federleicht/actions/workflows/pytest.yml)
[![GitHub - Page](https://img.shields.io/website?url=https%3A%2F%2Fd-chris.github.io%2Ffederleicht&up_message=pdoc&logo=github&label=documentation)](https://d-chris.github.io/federleicht)
[![GitHub - Release](https://img.shields.io/github/v/tag/d-chris/federleicht?logo=github&label=github)](https://github.com/d-chris/federleicht)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://raw.githubusercontent.com/d-chris/federleicht/main/.pre-commit-config.yaml)

---

Federleicht is a Python package providing a cache decorator for `pandas.DataFrame`, utilizing the lightweight and efficient `pyarrow` feather file format.

`federleicht.cache_dataframe` is designed to decorate functions that return `pandas.DataFrame` objects. The decorator saves the DataFrame to a feather file on the first call and loads it automatically on subsequent calls if the file exists.

## Key Features

- Feather Integration: Save and load `pandas.DataFrame` effortlessly using the Feather format, known for its speed and simplicity.
- Decorator Simplicity: Add caching functionality to your functions with a single decorator line.
- Efficient Caching: Avoid redundant computations by reusing cached results.

## Cache Expiry

To implement cache expiry, `federleicht` requires all arguments of the decorated function to be serializable. The cache will expire under the following conditions:

- Argument Sensitivity: Cache will expire if the arguments (`args` / `kwargs`) of the decorated function change.
- When a `os.PathLike` object is passed as an argument, the cache will expire if the file size and / or modification time changes.
- Code Change Detection: Cache will expire if the implementation / code of the decorated function changes during development.
- Time-based Expiry: Cache will expire when it is older than a given `timedelta`.
- In addition to the immutable built-in data types, the following types for arguments are supported:
  - `os.PathLike`
  - `pandas.DataFrame`
  - `pandas.Series`
  - `numpy.ndarray`
  - `datetime.datetime`
  - `types.FunctionType`

## Installation

Install federleicht from PyPI:

```cmd
pip install federleicht
```

## Usage

Here's a quick example:

```python
import pandas as pd
from federleicht import cache_dataframe

@cache_dataframe
def generate_large_dataframe():
    # Simulate a heavy computation
    return pd.DataFrame({"col1": range(10000), "col2": range(10000)})

df = generate_large_dataframe()
```

## Benchmark

[![Static Badge](https://img.shields.io/badge/kaggle-alessandrolobello-lightblue?logo=kaggle&logoColor=lightblue)](https://www.kaggle.com/datasets/alessandrolobello/)

- **file**: Eartquakes-1990-2023.csv
- **size**: 494.8 mb
- **lines**: 3,445,752

Functions which are used to benchmark the performance of the `cache_dataframe` decorator.

```python
def read_data(file: str, **kwargs) -> pd.DataFrame:
    """
    Read the earthquake dataset from a CSV file to Benchmark cache.

    Perform some data type conversions and return the DataFrame.
    """
    df = pd.read_csv(
        file,
        header=0,
        dtype={
            "status": "category",
            "tsunami": "boolean",
            "data_type": "category",
            "state": "category",
        },
        **kwargs,
    )

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["date"] = pd.to_datetime(df["date"], format="mixed")

    return df
```

The `pandas.DataFrame` without the `attrs` dictionary will be cached in the `.pandas_cache` directory and will only expire if the file changes. For more details, see the [Cache Expiry](#cache-expiry) section.

```python
@cache_dataframe
def read_cache(file: pathlib.Path, **kwargs) -> pd.DataFrame:
    return read_data(file, **kwargs)
```

### Benchmark Results

Results strongly depend on the system configuration and the file system. The following results are obtained on:

- **OS**: Windows
- **OS Version**: 10.0.19044
- **Python**: 3.11.9
- **CPU**: AMD64 Family 23 Model 104 Stepping 1, AuthenticAMD

|   nrows | read_data [s] | build_cache [s] | read_cache [s] |
| ------: | ------------: | --------------: | -------------: |
|   10000 |         0.060 |           0.076 |          0.037 |
|   32170 |         0.172 |           0.193 |          0.033 |
|  103493 |         0.536 |           0.569 |          0.067 |
|  332943 |         1.658 |           1.791 |          0.143 |
| 1071093 |         5.383 |           5.465 |          0.366 |
| 3445752 |        16.750 |          17.720 |          1.141 |

![BenchmarkPlot ](examples/benchmark.webp)
