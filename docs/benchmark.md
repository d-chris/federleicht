[![Static Badge](https://img.shields.io/badge/kaggle-alessandrolobello-lightblue?logo=kaggle&logoColor=lightblue)](https://www.kaggle.com/datasets/alessandrolobello/the-ultimate-earthquake-dataset-from-1990-2023)

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

![BenchmarkPlot ](https://raw.githubusercontent.com/d-chris/federleicht/refs/heads/main/benchmark.webp)
