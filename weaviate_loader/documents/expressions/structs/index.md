# The Struct datatype
Polars `Struct`s are the idiomatic way of working with multiple columns. It is also a free operation i.e. moving columns into `Struct`s does not copy any data!
For this section, let's start with a `DataFrame` that captures the average rating of a few movies across some states in the U.S.:
 
```python
ratings = pl.DataFrame(
    {
        "Movie": ["Cars", "IT", "ET", "Cars", "Up", "IT", "Cars", "ET", "Up", "ET"],
        "Theatre": ["NE", "ME", "IL", "ND", "NE", "SD", "NE", "IL", "IL", "SD"],
        "Avg_Rating": [4.5, 4.4, 4.6, 4.3, 4.8, 4.7, 4.7, 4.9, 4.7, 4.6],
        "Count": [30, 27, 26, 29, 31, 28, 28, 26, 33, 26],
    }
)
print(ratings)
```
 

## Encountering the `Struct` type
A common operation that will lead to a `Struct` column is the ever so popular `value_counts` function that is commonly used in exploratory data analysis. Checking the number of times a state appears the data will be done as so:
 
```python
out = ratings.select(pl.col("Theatre").value_counts(sort=True))
print(out)
```

Quite unexpected an output, especially if coming from tools that do not have such a data type. We're not in peril though, to get back to a more familiar output, all we need to do is `unnest` the `Struct` column into its constituent columns:
 
```python
out = ratings.select(pl.col("Theatre").value_counts(sort=True)).unnest("Theatre")
print(out)
```
 


Why `value_counts` returns a `Struct`
Polars expressions always have a `Fn(Series) -> Series` signature and `Struct` is thus the data type that allows us to provide multiple columns as input/output of an expression. In other words, all expressions have to return a `Series` object, and `Struct` allows us to stay consistent with that requirement.
## Structs as `dict`s
Polars will interpret a `dict` sent to the `Series` constructor as a `Struct`:
 
```python
rating_series = pl.Series(
    "ratings",
    [
        {"Movie": "Cars", "Theatre": "NE", "Avg_Rating": 4.5},
        {"Movie": "Toy Story", "Theatre": "ME", "Avg_Rating": 4.9},
    ],
)
print(rating_series)
```

Constructing `Series` objects
Note that `Series` here was constructed with the `name` of the series in the beginning, followed by the `values`. Providing the latter first
is considered an anti-pattern in Polars, and must be avoided.
### Extracting individual values of a `Struct`
Let's say that we needed to obtain just the `movie` value in the `Series` that we created above. We can use the `field` method to do so:
 
```python
out = rating_series.struct.field("Movie")
print(out)
```
 
### Renaming individual keys of a `Struct`
What if we need to rename individual `field`s of a `Struct` column? We first convert the `rating_series` object to a `DataFrame` so that we can view the changes easily, and then use the `rename_fields` method:
 
```python
out = (
    rating_series.to_frame()
    .select(pl.col("ratings").struct.rename_fields(["Film", "State", "Value"]))
    .unnest("ratings")
)
print(out)
```
 

## Practical use-cases of `Struct` columns
### Identifying duplicate rows
Let's get back to the `ratings` data. We want to identify cases where there are duplicates at a `Movie` and `Theatre` level. This is where the `Struct` datatype shines:
   
```python
out = ratings.filter(pl.struct("Movie", "Theatre").is_duplicated())
print(out)
```


We can identify the unique cases at this level also with `is_unique`!
### Multi-column ranking
Suppose, given that we know there are duplicates, we want to choose which rank gets a higher priority. We define `Count` of ratings to be more important than the actual `Avg_Rating` themselves, and only use it to break a tie. We can then do:
   
```python
out = ratings.with_columns(
    pl.struct("Count", "Avg_Rating")
    .rank("dense", descending=True)
    .over("Movie", "Theatre")
    .alias("Rank")
).filter(pl.struct("Movie", "Theatre").is_duplicated())
print(out)
```

That's a pretty complex set of requirements done very elegantly in Polars!
### Using multi-column apply
This was discussed in the previous section on *User Defined Functions*.