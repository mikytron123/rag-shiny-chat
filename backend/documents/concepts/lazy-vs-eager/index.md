# Lazy / eager API
Polars supports two modes of operation: lazy and eager. In the eager API the query is executed immediately while in the lazy API the query is only evaluated once it is 'needed'. Deferring the execution to the last minute can have significant performance advantages and is why the Lazy API is preferred in most cases. Let us demonstrate this with an example:
 
```python
df = pl.read_csv("docs/data/iris.csv")
df_small = df.filter(pl.col("sepal_length") > 5)
df_agg = df_small.group_by("species").agg(pl.col("sepal_width").mean())
print(df_agg)
```

In this example we use the eager API to:
1. Read the iris.
2. Filter the dataset based on sepal length
3. Calculate the mean of the sepal width per species
Every step is executed immediately returning the intermediate results. This can be very wasteful as we might do work or load extra data that is not being used. If we instead used the lazy API and waited on execution until all the steps are defined then the query planner could perform various optimizations. In this case:
* Predicate pushdown: Apply filters as early as possible while reading the dataset, thus only reading rows with sepal length greater than 5.
* Projection pushdown: Select only the columns that are needed while reading the dataset, thus removing the need to load additional columns (e.g. petal length & petal width)
 
```python
q = (
    pl.scan_csv("docs/data/iris.csv")
    .filter(pl.col("sepal_length") > 5)
    .group_by("species")
    .agg(pl.col("sepal_width").mean())
)
df = q.collect()
```

These will significantly lower the load on memory & CPU thus allowing you to fit bigger datasets in memory and process faster. Once the query is defined you call `collect` to inform Polars that you want to execute it. In the section on Lazy API we will go into more details on its implementation.
Eager API
In many cases the eager API is actually calling the lazy API under the hood and immediately collecting the result. This has the benefit that within the query itself optimization(s) made by the query planner can still take place.
### When to use which
In general the lazy API should be preferred unless you are either interested in the intermediate results or are doing exploratory work and don't know yet what your query is going to look like.