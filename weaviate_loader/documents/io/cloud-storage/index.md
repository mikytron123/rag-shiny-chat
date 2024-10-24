# Cloud storage
Polars can read and write to AWS S3, Azure Blob Storage and Google Cloud Storage. The API is the same for all three storage providers.
To read from cloud storage, additional dependencies may be needed depending on the use case and cloud storage provider:

```python
$ pip install fsspec s3fs adlfs gcsfs
```

## Reading from cloud storage
Polars can read a CSV, IPC or Parquet file in eager mode from cloud storage.
     
```python
import polars as pl
source = "s3://bucket/*.parquet"
df = pl.read_parquet(source)
```


This eager query downloads the file to a buffer in memory and creates a `DataFrame` from there. Polars uses `fsspec` to manage this download internally for all cloud storage providers.
## Scanning from cloud storage with query optimisation
Polars can scan a Parquet file in lazy mode from cloud storage. We may need to provide further details beyond the source url such as authentication details or storage region. Polars looks for these as environment variables but we can also do this manually by passing a `dict` as the `storage_options` argument.
 
```python
import polars as pl
source = "s3://bucket/*.parquet"
storage_options = {
    "aws_access_key_id": "<secret>",
    "aws_secret_access_key": "<secret>",
    "aws_region": "us-east-1",
}
df = pl.scan_parquet(source, storage_options=storage_options)
```

This query creates a `LazyFrame` without downloading the file. In the `LazyFrame` we have access to file metadata such as the schema. Polars uses the `object_store.rs` library internally to manage the interface with the cloud storage providers and so no extra dependencies are required in Python to scan a cloud Parquet file.
If we create a lazy query with [predicate and projection pushdowns](../../lazy/optimizations/), the query optimizer will apply them before the file is downloaded. This can significantly reduce the amount of data that needs to be downloaded. The query evaluation is triggered by calling `collect`.

```python
import polars as pl
source = "s3://bucket/*.parquet"
df = pl.scan_parquet(source).filter(pl.col("id") < 100).select("id","value").collect()
```

## Scanning with PyArrow
We can also scan from cloud storage using PyArrow. This is particularly useful for partitioned datasets such as Hive partitioning.
We first create a PyArrow dataset and then create a `LazyFrame` from the dataset.
 
```python
import polars as pl
import pyarrow.dataset as ds
dset = ds.dataset("s3://my-partitioned-folder/", format="parquet")
(
    pl.scan_pyarrow_dataset(dset)
    .filter(pl.col("foo") == "a")
    .select(["foo", "bar"])
    .collect()
)
```

## Writing to cloud storage
We can write a `DataFrame` to cloud storage in Python using s3fs for S3, adlfs for Azure Blob Storage and gcsfs for Google Cloud Storage. In this example, we write a Parquet file to S3.
 
```python
import polars as pl
import s3fs
df = pl.DataFrame({
    "foo": ["a", "b", "c", "d", "d"],
    "bar": [1, 2, 3, 4, 5],
})
fs = s3fs.S3FileSystem()
destination = "s3://bucket/my_file.parquet"
# write parquet
with fs.open(destination, mode='wb') as f:
    df.write_parquet(f)
```