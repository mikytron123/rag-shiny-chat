# Parquet
Loading or writing `Parquet` files is lightning fast as the layout of data in a Polars `DataFrame` in memory mirrors the layout of a Parquet file on disk in many respects.
Unlike CSV, Parquet is a columnar format. This means that the data is stored in columns rather than rows. This is a more efficient way of storing data as it allows for better compression and faster access to data.
## Read
We can read a `Parquet` file into a `DataFrame` using the `read_parquet` function:
 
```python
df = pl.read_parquet("docs/data/path.parquet")
```

## Write
 
```python
df = pl.DataFrame({"foo": [1, 2, 3], "bar": [None, "bak", "baz"]})
df.write_parquet("docs/data/path.parquet")
```
## Scan
Polars allows you to *scan* a `Parquet` input. Scanning delays the actual parsing of the file and instead returns a lazy computation holder called a `LazyFrame`.
 
```python
df = pl.scan_parquet("docs/data/path.parquet")
```

If you want to know why this is desirable, you can read more about those Polars optimizations here.
When we scan a `Parquet` file stored in the cloud, we can also apply predicate and projection pushdowns. This can significantly reduce the amount of data that needs to be downloaded. For scanning a Parquet file in the cloud, see Cloud storage.