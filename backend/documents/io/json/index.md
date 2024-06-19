# JSON files


Polars can read and write both standard JSON and newline-delimited JSON (NDJSON).


## Read


### JSON


Reading a JSON file should look familiar:





 

```python

df = pl.read_json("docs/data/path.json")

```





   [Available on feature json](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag json")








### Newline Delimited JSON


JSON objects that are delimited by newlines can be read into Polars in a much more performant way than standard json.


Polars can read an NDJSON file into a `DataFrame` using the `read_ndjson` function:





 

```python

df = pl.read_ndjson("docs/data/path.json")

```





   [Available on feature json](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag json")








## Write





   

```python

df = pl.DataFrame({"foo": [1, 2, 3], "bar": [None, "bak", "baz"]})
df.write_json("docs/data/path.json")

```





     [Available on feature json](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag json")








## Scan


Polars allows you to *scan* a JSON input **only for newline delimited json**. Scanning delays the actual parsing of the
file and instead returns a lazy computation holder called a `LazyFrame`.





 

```python

df = pl.scan_ndjson("docs/data/path.json")

```





   [Available on feature json](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag json")

