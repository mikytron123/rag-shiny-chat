# Pivots
Pivot a column in a `DataFrame` and perform one of the following aggregations:
* first
* sum
* min
* max
* mean
* median
The pivot operation consists of a group by one, or multiple columns (these will be the
new y-axis), the column that will be pivoted (this will be the new x-axis) and an
aggregation.
## Dataset
 
```python
df = pl.DataFrame(
    {
        "foo": ["A", "A", "B", "B", "C"],
        "N": [1, 2, 2, 4, 2],
        "bar": ["k", "l", "m", "n", "o"],
    }
)
print(df)
```
 

## Eager
 
```python
out = df.pivot(index="foo", columns="bar", values="N", aggregate_function="first")
print(out)
```
 

## Lazy
A Polars `LazyFrame` always need to know the schema of a computation statically (before collecting the query).
As a pivot's output schema depends on the data, and it is therefore impossible to determine the schema without
running the query.
Polars could have abstracted this fact for you just like Spark does, but we don't want you to shoot yourself in the foot
with a shotgun. The cost should be clear upfront.
 
```python
q = (
    df.lazy()
    .collect()
    .pivot(index="foo", columns="bar", values="N", aggregate_function="first")
    .lazy()
)
out = q.collect()
print(out)
```
 

