# CSV


## Read & write


Reading a CSV file should look familiar:





 

```python

df = pl.read_csv("docs/data/path.csv")

```





   [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")








Writing a CSV file is similar with the `write_csv` function:





 

```python

df = pl.DataFrame({"foo": [1, 2, 3], "bar": [None, "bak", "baz"]})
df.write_csv("docs/data/path.csv")

```





   [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")








## Scan


Polars allows you to *scan* a CSV input. Scanning delays the actual parsing of the
file and instead returns a lazy computation holder called a `LazyFrame`.





 

```python

df = pl.scan_csv("docs/data/path.csv")

```





   [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")








If you want to know why this is desirable, you can read more about these Polars
optimizations [here](../../concepts/lazy-vs-eager/).