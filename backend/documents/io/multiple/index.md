# Multiple
## Dealing with multiple files.
Polars can deal with multiple files differently depending on your needs and memory strain.
Let's create some files to give us some context:
 Python
 
```python
import polars as pl
df = pl.DataFrame({"foo": [1, 2, 3], "bar": [None, "ham", "spam"]})
for i in range(5):
    df.write_csv(f"docs/data/my_many_files_{i}.csv")
```

## Reading into a single `DataFrame`
To read multiple files into a single `DataFrame`, we can use globbing patterns:
 Python
 
```python
df = pl.read_csv("docs/data/my_many_files_*.csv")
print(df)
```

To see how this works we can take a look at the query plan. Below we see that all files are read separately and
concatenated into a single `DataFrame`. Polars will try to parallelize the reading.
 Python
 
```python
pl.scan_csv("docs/data/my_many_files_*.csv").show_graph()
```
## Reading and processing in parallel
If your files don't have to be in a single table you can also build a query plan for each file and execute them in parallel
on the Polars thread pool.
All query plan execution is embarrassingly parallel and doesn't require any communication.
 Python
 
```python
import glob
import polars as pl
queries = []
for file in glob.glob("docs/data/my_many_files_*.csv"):
    q = pl.scan_csv(file).group_by("bar").agg(pl.len(), pl.sum("foo"))
    queries.append(q)
dataframes = pl.collect_all(queries)
print(dataframes)
```

