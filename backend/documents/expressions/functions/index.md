# Functions


Polars expressions have a large number of built in functions. These allow you to create complex queries without the need for [user defined functions](../user-defined-functions/). There are too many to go through here, but we will cover some of the more popular use cases. If you want to view all the functions go to the API Reference for your programming language.


In the examples below we will use the following `DataFrame`:





 

```python

df = pl.DataFrame(
    {
        "nrs": [1, 2, 3, None, 5],
        "names": ["foo", "ham", "spam", "egg", "spam"],
        "random": np.random.rand(5),
        "groups": ["A", "A", "B", "C", "B"],
    }
)
print(df)

```





 











## Column naming


By default if you perform an expression it will keep the same name as the original column. In the example below we perform an expression on the `nrs` column. Note that the output `DataFrame` still has the same name.






```python

df_samename = df.select(pl.col("nrs") + 5)
print(df_samename)

```












This might get problematic in the case you use the same column multiple times in your expression as the output columns will get duplicated. For example, the following query will fail.






```python

try:
    df_samename2 = df.select(pl.col("nrs") + 5, pl.col("nrs") - 5)
    print(df_samename2)
except Exception as e:
    print(e)

```










```
the name: 'nrs' is duplicate

It's possible that multiple expressions are returning the same default column name. If this is the case, try renaming the columns with `.alias("new_name")` to avoid duplicate column names.

```

You can change the output name of an expression by using the `alias` function





 

```python

df_alias = df.select(
    (pl.col("nrs") + 5).alias("nrs + 5"),
    (pl.col("nrs") - 5).alias("nrs - 5"),
)
print(df_alias)

```





 











In case of multiple columns for example when using `all()` or `col(*)` you can apply a mapping function `name.map` to change the original column name into something else. In case you want to add a suffix (`name.suffix()`) or prefix (`name.prefix()`) these are also built in.


 Python




 
 
 


## Count unique values


There are two ways to count unique values in Polars: an exact methodology and an approximation. The approximation uses the [HyperLogLog++](https://en.wikipedia.org/wiki/HyperLogLog) algorithm to approximate the cardinality and is especially useful for very large datasets where an approximation is good enough.





   

```python

df_alias = df.select(
    pl.col("names").n_unique().alias("unique"),
    pl.approx_n_unique("names").alias("unique_approx"),
)
print(df_alias)

```





   











## Conditionals


Polars supports if-else like conditions in expressions with the `when`, `then`, `otherwise` syntax. The predicate is placed in the `when` clause and when this evaluates to `true` the `then` expression is applied otherwise the `otherwise` expression is applied (row-wise).





 

```python

df_conditional = df.select(
    pl.col("nrs"),
    pl.when(pl.col("nrs") > 2)
    .then(pl.lit(True))
    .otherwise(pl.lit(False))
    .alias("conditional"),
)
print(df_conditional)

```





 









