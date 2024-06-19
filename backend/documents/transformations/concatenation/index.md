# Concatenation


There are a number of ways to concatenate data from separate DataFrames:


* two dataframes with **the same columns** can be **vertically** concatenated to make a **longer** dataframe
* two dataframes with **non-overlapping columns** can be **horizontally** concatenated to make a **wider** dataframe
* two dataframes with **different numbers of rows and columns** can be **diagonally** concatenated to make a dataframe which might be longer and/ or wider. Where column names overlap values will be vertically concatenated. Where column names do not overlap new rows and columns will be added. Missing values will be set as `null`


## Vertical concatenation - getting longer


In a vertical concatenation you combine all of the rows from a list of `DataFrames` into a single longer `DataFrame`.





 

```python

df_v1 = pl.DataFrame(
    {
        "a": [1],
        "b": [3],
    }
)
df_v2 = pl.DataFrame(
    {
        "a": [2],
        "b": [4],
    }
)
df_vertical_concat = pl.concat(
    [
        df_v1,
        df_v2,
    ],
    how="vertical",
)
print(df_vertical_concat)

```





 











Vertical concatenation fails when the dataframes do not have the same column names.


## Horizontal concatenation - getting wider


In a horizontal concatenation you combine all of the columns from a list of `DataFrames` into a single wider `DataFrame`.





 

```python

df_h1 = pl.DataFrame(
    {
        "l1": [1, 2],
        "l2": [3, 4],
    }
)
df_h2 = pl.DataFrame(
    {
        "r1": [5, 6],
        "r2": [7, 8],
        "r3": [9, 10],
    }
)
df_horizontal_concat = pl.concat(
    [
        df_h1,
        df_h2,
    ],
    how="horizontal",
)
print(df_horizontal_concat)

```





 











Horizontal concatenation fails when dataframes have overlapping columns.


When dataframes have different numbers of rows,
columns will be padded with `null` values at the end up to the maximum length.





 

```python

df_h1 = pl.DataFrame(
    {
        "l1": [1, 2],
        "l2": [3, 4],
    }
)
df_h2 = pl.DataFrame(
    {
        "r1": [5, 6, 7],
        "r2": [8, 9, 10],
    }
)
df_horizontal_concat = pl.concat(
    [
        df_h1,
        df_h2,
    ],
    how="horizontal",
)
print(df_horizontal_concat)

```





 











## Diagonal concatenation - getting longer, wider and `null`ier


In a diagonal concatenation you combine all of the row and columns from a list of `DataFrames` into a single longer and/or wider `DataFrame`.





 

```python

df_d1 = pl.DataFrame(
    {
        "a": [1],
        "b": [3],
    }
)
df_d2 = pl.DataFrame(
    {
        "a": [2],
        "d": [4],
    }
)

df_diagonal_concat = pl.concat(
    [
        df_d1,
        df_d2,
    ],
    how="diagonal",
)
print(df_diagonal_concat)

```





 











Diagonal concatenation generates nulls when the column names do not overlap.


When the dataframe shapes do not match and we have an overlapping semantic key then [we can join the dataframes](../joins/) instead of concatenating them.


## Rechunking


Before a concatenation we have two dataframes `df1` and `df2`. Each column in `df1` and `df2` is in one or more chunks in memory. By default, during concatenation the chunks in each column are copied to a single new chunk - this is known as **rechunking**. Rechunking is an expensive operation, but is often worth it because future operations will be faster.
If you do not want Polars to rechunk the concatenated `DataFrame` you specify `rechunk = False` when doing the concatenation.