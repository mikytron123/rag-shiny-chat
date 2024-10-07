# Basic operators
This section describes how to use basic operators (e.g. addition, subtraction) in conjunction with Expressions. We will provide various examples using different themes in the context of the following dataframe.
Note
In Rust and Python it is possible to use the operators directly (as in `+ - * / < >`) as the language allows operator overloading. For instance, the operator `+` translates to the `.add()` method. You can choose the one you prefer.

 
```python
df = pl.DataFrame(
    {
        "nrs": [1, 2, 3, None, 5],
        "names": ["foo", "ham", "spam", "egg", None],
        "random": np.random.rand(5),
        "groups": ["A", "A", "B", "C", "B"],
    }
)
print(df)
```
 

### Numerical
 
```python
df_numerical = df.select(
    (pl.col("nrs") + 5).alias("nrs + 5"),
    (pl.col("nrs") - 5).alias("nrs - 5"),
    (pl.col("nrs") * pl.col("random")).alias("nrs * random"),
    (pl.col("nrs") / pl.col("random")).alias("nrs / random"),
)
print(df_numerical)
```
 

### Logical
 
```python
df_logical = df.select(
    (pl.col("nrs") > 1).alias("nrs > 1"),
    (pl.col("random") <= 0.5).alias("random <= .5"),
    (pl.col("nrs") != 1).alias("nrs != 1"),
    (pl.col("nrs") == 1).alias("nrs == 1"),
    ((pl.col("random") <= 0.5) & (pl.col("nrs") > 1)).alias("and_expr"),  # and
    ((pl.col("random") <= 0.5) | (pl.col("nrs") > 1)).alias("or_expr"),  # or
)
print(df_logical)
```
 

