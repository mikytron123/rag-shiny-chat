# Streaming API
One additional benefit of the lazy API is that it allows queries to be executed in a streaming manner. Instead of processing the data all-at-once Polars can execute the query in batches allowing you to process datasets that are larger-than-memory.
To tell Polars we want to execute a query in streaming mode we pass the `streaming=True` argument to `collect`
 
```python
q1 = (
    pl.scan_csv("docs/data/iris.csv")
    .filter(pl.col("sepal_length") > 5)
    .group_by("species")
    .agg(pl.col("sepal_width").mean())
)
df = q1.collect(streaming=True)
```


## When is streaming available?
Streaming is still in development. We can ask Polars to execute any lazy query in streaming mode. However, not all lazy operations support streaming. If there is an operation for which streaming is not supported Polars will run the query in non-streaming mode.
Streaming is supported for many operations including:
* `filter`,`slice`,`head`,`tail`
* `with_columns`,`select`
* `group_by`
* `join`
* `unique`
* `sort`
* `explode`,`melt`
* `scan_csv`,`scan_parquet`,`scan_ipc`
This list is not exhaustive. Polars is in active development, and more operations can be added without explicit notice.
### Example with supported operations
To determine which parts of your query are streaming, use the `explain` method. Below is an example that demonstrates how to inspect the query plan. More information about the query plan can be found in the chapter on the [Lazy API](https://docs.pola.rs/user-guide/lazy/query-plan/).
 
```python
print(q1.explain(streaming=True))
```
 

### Example with non-streaming operations
 
```python
q2 = pl.scan_csv("docs/data/iris.csv").with_columns(
    pl.col("sepal_length").mean().over("species")
)
print(q2.explain(streaming=True))
```
 

