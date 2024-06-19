# Joins


## Join strategies


Polars supports the following join strategies by specifying the `how` argument:




| Strategy | Description |
| --- | --- |
| `inner` | Returns row with matching keys in *both* frames. Non-matching rows in either the left or right frame are discarded. |
| `left` | Returns all rows in the left dataframe, whether or not a match in the right-frame is found. Non-matching rows have their right columns null-filled. |
| `full` | Returns all rows from both the left and right dataframe. If no match is found in one frame, columns from the other frame are null-filled. |
| `cross` | Returns the Cartesian product of all rows from the left frame with all rows from the right frame. Duplicates rows are retained; the table length of `A` cross-joined with `B` is always `len(A) × len(B)`. |
| `semi` | Returns all rows from the left frame in which the join key is also present in the right frame. |
| `anti` | Returns all rows from the left frame in which the join key is *not* present in the right frame. |


A separate `coalesce` parameter determines whether to merge key columns with the same name from the left and right
frames.


### Inner join


An `inner` join produces a `DataFrame` that contains only the rows where the join key exists in both `DataFrames`. Let's
take for example the following two `DataFrames`:





 

```python

df_customers = pl.DataFrame(
    {
        "customer_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
    }
)
print(df_customers)

```





 















 

```python

df_orders = pl.DataFrame(
    {
        "order_id": ["a", "b", "c"],
        "customer_id": [1, 2, 2],
        "amount": [100, 200, 300],
    }
)
print(df_orders)

```





 











To get a `DataFrame` with the orders and their associated customer we can do an `inner` join on the `customer_id`
column:





 

```python

df_inner_customer_join = df_customers.join(df_orders, on="customer_id", how="inner")
print(df_inner_customer_join)

```





 











### Left join


The `left` outer join produces a `DataFrame` that contains all the rows from the left `DataFrame` and only the rows from
the right `DataFrame` where the join key exists in the left `DataFrame`. If we now take the example from above and want
to have a `DataFrame` with all the customers and their associated orders (regardless of whether they have placed an
order or not) we can do a `left` join:





 

```python

df_left_join = df_customers.join(df_orders, on="customer_id", how="left")
print(df_left_join)

```





 











Notice, that the fields for the customer with the `customer_id` of `3` are null, as there are no orders for this
customer.


### Outer join


The `full` outer join produces a `DataFrame` that contains all the rows from both `DataFrames`. Columns are null, if the
join key does not exist in the source `DataFrame`. Doing a `full` outer join on the two `DataFrames` from above produces
a similar `DataFrame` to the `left` join:





 

```python

df_outer_join = df_customers.join(df_orders, on="customer_id", how="full")
print(df_outer_join)

```





 














 

```python

df_outer_coalesce_join = df_customers.join(
    df_orders, on="customer_id", how="full", coalesce=True
)
print(df_outer_coalesce_join)

```





 











### Cross join


A `cross` join is a Cartesian product of the two `DataFrames`. This means that every row in the left `DataFrame` is
joined with every row in the right `DataFrame`. The `cross` join is useful for creating a `DataFrame` with all possible
combinations of the columns in two `DataFrames`. Let's take for example the following two `DataFrames`.





 

```python

df_colors = pl.DataFrame(
    {
        "color": ["red", "blue", "green"],
    }
)
print(df_colors)

```





 















 

```python

df_sizes = pl.DataFrame(
    {
        "size": ["S", "M", "L"],
    }
)
print(df_sizes)

```





 











We can now create a `DataFrame` containing all possible combinations of the colors and sizes with a `cross` join:





 

```python

df_cross_join = df_colors.join(df_sizes, how="cross")
print(df_cross_join)

```





 











  



The `inner`, `left`, `full` and `cross` join strategies are standard amongst dataframe libraries. We provide more
details on the less familiar `semi`, `anti` and `asof` join strategies below.


### Semi join


The `semi` join returns all rows from the left frame in which the join key is also present in the right frame. Consider
the following scenario: a car rental company has a `DataFrame` showing the cars that it owns with each car having a
unique `id`.





 

```python

df_cars = pl.DataFrame(
    {
        "id": ["a", "b", "c"],
        "make": ["ford", "toyota", "bmw"],
    }
)
print(df_cars)

```





 











The company has another `DataFrame` showing each repair job carried out on a vehicle.





 

```python

df_repairs = pl.DataFrame(
    {
        "id": ["c", "c"],
        "cost": [100, 200],
    }
)
print(df_repairs)

```





 











You want to answer this question: which of the cars have had repairs carried out?


An inner join does not answer this question directly as it produces a `DataFrame` with multiple rows for each car that
has had multiple repair jobs:





 

```python

df_inner_join = df_cars.join(df_repairs, on="id", how="inner")
print(df_inner_join)

```





 











However, a semi join produces a single row for each car that has had a repair job carried out.





 

```python

df_semi_join = df_cars.join(df_repairs, on="id", how="semi")
print(df_semi_join)

```





 











### Anti join


Continuing this example, an alternative question might be: which of the cars have **not** had a repair job carried out?
An anti join produces a `DataFrame` showing all the cars from `df_cars` where the `id` is not present in
the `df_repairs` `DataFrame`.





 

```python

df_anti_join = df_cars.join(df_repairs, on="id", how="anti")
print(df_anti_join)

```





 











## Asof join


An `asof` join is like a left join except that we match on nearest key rather than equal keys.
In Polars we can do an asof join with the `join_asof` method.


Consider the following scenario: a stock market broker has a `DataFrame` called `df_trades` showing transactions it has
made for different stocks.





 

```python

df_trades = pl.DataFrame(
    {
        "time": [
            datetime(2020, 1, 1, 9, 1, 0),
            datetime(2020, 1, 1, 9, 1, 0),
            datetime(2020, 1, 1, 9, 3, 0),
            datetime(2020, 1, 1, 9, 6, 0),
        ],
        "stock": ["A", "B", "B", "C"],
        "trade": [101, 299, 301, 500],
    }
)
print(df_trades)

```





 











The broker has another `DataFrame` called `df_quotes` showing prices it has quoted for these stocks.





 

```python

df_quotes = pl.DataFrame(
    {
        "time": [
            datetime(2020, 1, 1, 9, 0, 0),
            datetime(2020, 1, 1, 9, 2, 0),
            datetime(2020, 1, 1, 9, 4, 0),
            datetime(2020, 1, 1, 9, 6, 0),
        ],
        "stock": ["A", "B", "C", "A"],
        "quote": [100, 300, 501, 102],
    }
)

print(df_quotes)

```





 











You want to produce a `DataFrame` showing for each trade the most recent quote provided *before* the trade. You do this
with `join_asof` (using the default `strategy = "backward"`).
To avoid joining between trades on one stock with a quote on another you must specify an exact preliminary join on the
stock column with `by="stock"`.





 

```python

df_asof_join = df_trades.join_asof(df_quotes, on="time", by="stock")
print(df_asof_join)

```





 











If you want to make sure that only quotes within a certain time range are joined to the trades you can specify
the `tolerance` argument. In this case we want to make sure that the last preceding quote is within 1 minute of the
trade so we set `tolerance = "1m"`.


 Python





```python

df_asof_tolerance_join = df_trades.join_asof(
    df_quotes, on="time", by="stock", tolerance="1m"
)
print(df_asof_tolerance_join)

```


