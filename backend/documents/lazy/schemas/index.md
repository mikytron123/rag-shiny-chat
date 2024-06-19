# Schema


The schema of a Polars `DataFrame` or `LazyFrame` sets out the names of the columns and their datatypes. You can see the schema with the `.schema` method on a `DataFrame` or `LazyFrame`


 Python


   

```python

q3 = pl.DataFrame({"foo": ["a", "b", "c"], "bar": [0, 1, 2]}).lazy()

print(q3.schema)

```







```python

OrderedDict({'foo': String, 'bar': Int64})

```

The schema plays an important role in the lazy API.


## Type checking in the lazy API


One advantage of the lazy API is that Polars will check the schema before any data is processed. This check happens when you execute your lazy query.


We see how this works in the following simple example where we call the `.round` expression on the integer `bar` column.


 Python


   

```python

q4 = (
    pl.DataFrame({"foo": ["a", "b", "c"], "bar": [0, 1, 2]})
    .lazy()
    .with_columns(pl.col("bar").round(0))
)

```






The `.round` expression is only valid for columns with a floating point dtype. Calling `.round` on an integer column means the operation will raise an `InvalidOperationError` when we evaluate the query with `collect`. This schema check happens before the data is processed when we call `collect`.


 Python



```python

try:
    print(q4.collect())
except Exception as e:
    print(e)

```





```
`round` operation not supported for dtype `i64`

```

If we executed this query in eager mode the error would only be found once the data had been processed in all earlier steps.


When we execute a lazy query Polars checks for any potential `InvalidOperationError` before the time-consuming step of actually processing the data in the pipeline.


## The lazy API must know the schema


In the lazy API the Polars query optimizer must be able to infer the schema at every step of a query plan. This means that operations where the schema is not knowable in advance cannot be used with the lazy API.


The classic example of an operation where the schema is not knowable in advance is a `.pivot` operation. In a `.pivot` the new column names come from data in one of the columns. As these column names cannot be known in advance a `.pivot` is not available in the lazy API.


## Dealing with operations not available in the lazy API


If your pipeline includes an operation that is not available in the lazy API it is normally best to:


* run the pipeline in lazy mode up until that point
* execute the pipeline with `.collect` to materialize a `DataFrame`
* do the non-lazy operation on the `DataFrame`
* convert the output back to a `LazyFrame` with `.lazy` and continue in lazy mode


We show how to deal with a non-lazy operation in this example where we:


* create a simple `DataFrame`
* convert it to a `LazyFrame` with `.lazy`
* do a transformation using `.with_columns`
* execute the query before the pivot with `.collect` to get a `DataFrame`
* do the `.pivot` on the `DataFrame`
* convert back in lazy mode
* do a `.filter`
* finish by executing the query with `.collect` to get a `DataFrame`


 Python


     

```python

lazy_eager_query = (
    pl.DataFrame(
        {
            "id": ["a", "b", "c"],
            "month": ["jan", "feb", "mar"],
            "values": [0, 1, 2],
        }
    )
    .lazy()
    .with_columns((2 * pl.col("values")).alias("double_values"))
    .collect()
    .pivot(
        index="id", columns="month", values="double_values", aggregate_function="first"
    )
    .lazy()
    .filter(pl.col("mar").is_null())
    .collect()
)
print(lazy_eager_query)

```







