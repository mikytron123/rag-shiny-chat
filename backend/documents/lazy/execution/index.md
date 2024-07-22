# Query execution
Our example query on the Reddit dataset is:
 Python
 
```python
q1 = (
    pl.scan_csv("docs/data/reddit.csv")
    .with_columns(pl.col("name").str.to_uppercase())
    .filter(pl.col("comment_karma") > 0)
)
```

If we were to run the code above on the Reddit CSV the query would not be evaluated. Instead Polars takes each line of code, adds it to the internal query graph and optimizes the query graph.
When we execute the code Polars executes the optimized query graph by default.
### Execution on the full dataset
We can execute our query on the full dataset by calling the `.collect` method on the query.
 Python
   
```python
q4 = (
    pl.scan_csv(f"docs/data/reddit.csv")
    .with_columns(pl.col("name").str.to_uppercase())
    .filter(pl.col("comment_karma") > 0)
    .collect()
)
```

Above we see that from the 10 million rows there are 14,029 rows that match our predicate.
With the default `collect` method Polars processes all of your data as one batch. This means that all the data has to fit into your available memory at the point of peak memory usage in your query.
Reusing `LazyFrame` objects
Remember that `LazyFrame`s are query plans i.e. a promise on computation and is not guaranteed to cache common subplans. This means that every time you reuse it in separate downstream queries after it is defined, it is computed all over again. If you define an operation on a `LazyFrame` that doesn't maintain row order (such as a `group_by`), then the order will also change every time it is run. To avoid this, use `maintain_order=True` arguments for such operations.
### Execution on larger-than-memory data
If your data requires more memory than you have available Polars may be able to process the data in batches using *streaming* mode. To use streaming mode you simply pass the `streaming=True` argument to `collect`
 Python
   
```python
q5 = (
    pl.scan_csv(f"docs/data/reddit.csv")
    .with_columns(pl.col("name").str.to_uppercase())
    .filter(pl.col("comment_karma") > 0)
    .collect(streaming=True)
)
```

We look at streaming in more detail here.
### Execution on a partial dataset
While you're writing, optimizing or checking your query on a large dataset, querying all available data may lead to a slow development process.
You can instead execute the query with the `.fetch` method. The `.fetch` method takes a parameter `n_rows` and tries to 'fetch' that number of rows at the data source. The number of rows cannot be guaranteed, however, as the lazy API does not count how many rows there are at each stage of the query.
Here we "fetch" 100 rows from the source file and apply the predicates.
 Python
     
```python
q9 = (
    pl.scan_csv(f"docs/data/reddit.csv")
    .with_columns(pl.col("name").str.to_uppercase())
    .filter(pl.col("comment_karma") > 0)
    .fetch(n_rows=int(100))
)
```

