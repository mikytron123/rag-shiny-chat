# Data structures
The core base data structures provided by Polars are `Series` and `DataFrame`.
## Series
Series are a 1-dimensional data structure. Within a series all elements have the same [Data Type](../data-types/overview/) .
The snippet below shows how to create a simple named `Series` object.
 
```python
import polars as pl
s = pl.Series("a", [1, 2, 3, 4, 5])
print(s)
```
 

## DataFrame
A `DataFrame` is a 2-dimensional data structure that is backed by a `Series`, and it can be seen as an abstraction of a collection (e.g. list) of `Series`. Operations that can be executed on a `DataFrame` are very similar to what is done in a `SQL` like query. You can `GROUP BY`, `JOIN`, `PIVOT`, but also define custom functions.
 
```python
from datetime import datetime
df = pl.DataFrame(
    {
        "integer": [1, 2, 3, 4, 5],
        "date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
        "float": [4.0, 5.0, 6.0, 7.0, 8.0],
    }
)
print(df)
```
 

### Viewing data
This part focuses on viewing data in a `DataFrame`. We will use the `DataFrame` from the previous example as a starting point.
#### Head
The `head` function shows by default the first 5 rows of a `DataFrame`. You can specify the number of rows you want to see (e.g. `df.head(10)`).
 
```python
print(df.head(3))
```
 

#### Tail
The `tail` function shows the last 5 rows of a `DataFrame`. You can also specify the number of rows you want to see, similar to `head`.
 
```python
print(df.tail(3))
```
 

#### Sample
If you want to get an impression of the data of your `DataFrame`, you can also use `sample`. With `sample` you get an *n* number of random rows from the `DataFrame`.
 
```python
print(df.sample(2))
```
 

#### Describe
`Describe` returns summary statistics of your `DataFrame`. It will provide several quick statistics if possible.
 
```python
print(df.describe())
```

```python
// Not available in Rust
```

