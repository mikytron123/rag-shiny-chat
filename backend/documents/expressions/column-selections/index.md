# Column selections
Let's create a dataset to use in this section:
 
```python
from datetime import date, datetime
import polars as pl
df = pl.DataFrame(
    {
        "id": [9, 4, 2],
        "place": ["Mars", "Earth", "Saturn"],
        "date": pl.date_range(date(2022, 1, 1), date(2022, 1, 3), "1d", eager=True),
        "sales": [33.4, 2142134.1, 44.7],
        "has_people": [False, True, False],
        "logged_at": pl.datetime_range(
            datetime(2022, 12, 1), datetime(2022, 12, 1, 0, 0, 2), "1s", eager=True
        ),
    }
).with_row_index("index")
print(df)
```
 

## Expression expansion
As we've seen in the previous section, we can select specific columns using the `pl.col` method. It can also select multiple columns - both as a means of convenience, and to *expand* the expression.
This kind of convenience feature isn't just decorative or syntactic sugar. It allows for a very powerful application of DRY principles in your code: a single expression that specifies multiple columns expands into a list of expressions (depending on the DataFrame schema), resulting in being able to select multiple columns + run computation on them!
### Select all, or all but some
We can select all columns in the `DataFrame` object by providing the argument `*`:
 
```python
out = df.select(pl.col("*"))
# Is equivalent to
out = df.select(pl.all())
print(out)
```
 

Often, we don't just want to include all columns, but include all *while* excluding a few. This can be done easily as well:
 
```python
out = df.select(pl.col("*").exclude("logged_at", "index"))
print(out)
```
 

### By multiple strings
Specifying multiple strings allows expressions to *expand* to all matching columns:
 
```python
out = df.select(pl.col("date", "logged_at").dt.to_string("%Y-%h-%d"))
print(out)
```

### By regular expressions
Multiple column selection is possible by regular expressions also, by making sure to wrap the regex by `^` and `$` to let `pl.col` know that a regex selection is expected:

```python
out = df.select(pl.col("^.*(as|sa).*$"))
print(out)
```


### By data type
`pl.col` can select multiple columns using Polars data types:
 
```python
out = df.select(pl.col(pl.Int64, pl.UInt32, pl.Boolean).n_unique())
print(out)
```
 

## Using `selectors`
Polars also allows for the use of intuitive selections for columns based on their name, `dtype` or other properties; and this is built on top of existing functionality outlined in `col` used above. It is recommended to use them by importing and aliasing `polars.selectors` as `cs`.
### By `dtype`
To select just the integer and string columns, we can do:
 
```python
import polars.selectors as cs
out = df.select(cs.integer(), cs.string())
print(out)
```

### Applying set operations
These *selectors* also allow for set based selection operations. For instance, to select the **numeric** columns **except** the **first** column that indicates row numbers:
   
```python
out = df.select(cs.numeric() - cs.first())
print(out)
```

We can also select the row number by name **and** any **non**-numeric columns:
   
```python
out = df.select(cs.by_name("index") | ~cs.numeric())
print(out)
```

### By patterns and substrings
*Selectors* can also be matched by substring and regex patterns:
   
```python
out = df.select(cs.contains("index"), cs.matches(".*_.*"))
print(out)
```

### Converting to expressions
What if we want to apply a specific operation on the selected columns (i.e. get back to representing them as **expressions** to operate upon)? We can simply convert them using `as_expr` and then proceed as normal:
 
```python
out = df.select(cs.temporal().as_expr().dt.to_string("%Y-%h-%d"))
print(out)
```

### Debugging `selectors`
Polars also provides two helpful utility functions to aid with using selectors: `is_selector` and `expand_selector`:
 
```python
from polars.selectors import is_selector
out = cs.numeric()
print(is_selector(out))
out = cs.boolean() | cs.numeric()
print(is_selector(out))
out = cs.numeric() + pl.lit(123)
print(is_selector(out))
```

To predetermine the column names that are selected, which is especially useful for a LazyFrame object:
 
```python
from polars.selectors import expand_selector
out = cs.temporal()
print(expand_selector(df, out))
out = ~(cs.temporal() | cs.numeric())
print(expand_selector(df, out))
```
