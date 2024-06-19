# Getting started


This chapter is here to help you get started with Polars. It covers all the fundamental features and functionalities of the library, making it easy for new users to familiarise themselves with the basics from initial installation and setup to core functionalities. If you're already an advanced user or familiar with Dataframes, feel free to skip ahead to the [next chapter about installation options](../installation/).


## Installing Polars






```python

pip install polars

```









## Reading & writing


Polars supports reading and writing for common file formats (e.g. csv, json, parquet), cloud storage (S3, Azure Blob, BigQuery) and databases (e.g. postgres, mysql). Below we show the concept of reading and writing to disk.





 

```python

import polars as pl
from datetime import datetime

df = pl.DataFrame(
    {
        "integer": [1, 2, 3],
        "date": [
            datetime(2025, 1, 1),
            datetime(2025, 1, 2),
            datetime(2025, 1, 3),
        ],
        "float": [4.0, 5.0, 6.0],
        "string": ["a", "b", "c"],
    }
)

print(df)

```





 











In the example below we write the DataFrame to a csv file called `output.csv`. After that, we read it back using `read_csv` and then `print` the result for inspection.





   

```python

df.write_csv("docs/data/output.csv")
df_csv = pl.read_csv("docs/data/output.csv")
print(df_csv)

```





     [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")











For more examples on the CSV file format and other data formats, start with the [IO section](../io/) of the user guide.


## Expressions


`Expressions` are the core strength of Polars. The `expressions` offer a modular structure that allows you to combine simple concepts into complex queries. Below we cover the basic components that serve as building block (or in Polars terminology contexts) for all your queries:


* `select`
* `filter`
* `with_columns`
* `group_by`


To learn more about expressions and the context in which they operate, see the user guide sections: [Contexts](../concepts/contexts/) and [Expressions](../concepts/expressions/).


### Select


To select a column we need to do two things:


1. Define the `DataFrame` we want the data from.
2. Select the data that we need.


In the example below you see that we select `col('*')`. The asterisk stands for all columns.





 

```python

df.select(pl.col("*"))

```





 











You can also specify the specific columns that you want to return. There are two ways to do this. The first option is to pass the column names, as seen below.





 

```python

df.select(pl.col("a", "b"))

```





 











Follow these links to other parts of the user guide to learn more about [basic operations](../expressions/operators/) or [column selections](../expressions/column-selections/).


### Filter


The `filter` option allows us to create a subset of the `DataFrame`. We use the same `DataFrame` as earlier and we filter between two specified dates.





 

```python

df.filter(
    pl.col("c").is_between(datetime(2025, 12, 2), datetime(2025, 12, 3)),
)

```





 











With `filter` you can also create more complex filters that include multiple columns.





 

```python

df.filter((pl.col("a") <= 3) & (pl.col("d").is_not_nan()))

```





 











### Add columns


`with_columns` allows you to create new columns for your analyses. We create two new columns `e` and `b+42`. First we sum all values from column `b` and store the results in column `e`. After that we add `42` to the values of `b`. Creating a new column `b+42` to store these results.





 

```python

df.with_columns(pl.col("b").sum().alias("e"), (pl.col("b") + 42).alias("b+42"))

```





 











### Group by


We will create a new `DataFrame` for the Group by functionality. This new `DataFrame` will include several 'groups' that we want to group by.





 

```python

df2 = pl.DataFrame(
    {
        "x": range(8),
        "y": ["A", "A", "A", "B", "B", "C", "X", "X"],
    }
)

```





 














 

```python

df2.group_by("y", maintain_order=True).len()

```





 














 

```python

df2.group_by("y", maintain_order=True).agg(
    pl.col("*").count().alias("count"),
    pl.col("*").sum().alias("sum"),
)

```





 











### Combination


Below are some examples on how to combine operations to create the `DataFrame` you require.





   

```python

df_x = df.with_columns((pl.col("a") * pl.col("b")).alias("a * b")).select(
    pl.all().exclude(["c", "d"])
)

print(df_x)

```





   














   

```python

df_y = df.with_columns((pl.col("a") * pl.col("b")).alias("a * b")).select(
    pl.all().exclude("d")
)

print(df_y)

```





   











## Combining DataFrames


There are two ways `DataFrame`s can be combined depending on the use case: join and concat.


### Join


Polars supports all types of join (e.g. left, right, inner, outer). Let's have a closer look on how to `join` two `DataFrames` into a single `DataFrame`. Our two `DataFrames` both have an 'id'-like column: `a` and `x`. We can use those columns to `join` the `DataFrames` in this example.





 

```python

df = pl.DataFrame(
    {
        "a": range(8),
        "b": np.random.rand(8),
        "d": [1, 2.0, float("nan"), float("nan"), 0, -5, -42, None],
    }
)

df2 = pl.DataFrame(
    {
        "x": range(8),
        "y": ["A", "A", "A", "B", "B", "C", "X", "X"],
    }
)
joined = df.join(df2, left_on="a", right_on="x")
print(joined)

```





 











To see more examples with other types of joins, see the [Transformations section](../transformations/joins/) in the user guide.


### Concat


We can also `concatenate` two `DataFrames`. Vertical concatenation will make the `DataFrame` longer. Horizontal concatenation will make the `DataFrame` wider. Below you can see the result of an horizontal concatenation of our two `DataFrames`.





 

```python

stacked = df.hstack(df2)
print(stacked)

```





 









