# Filtering
Filtering date columns works in the same way as with other types of columns using the `.filter` method.
Polars uses Python's native `datetime`, `date` and `timedelta` for equality comparisons between the datatypes `pl.Datetime`, `pl.Date` and `pl.Duration`.
In the following example we use a time series of Apple stock prices.
 
```python
import polars as pl
from datetime import datetime
df = pl.read_csv("docs/data/apple_stock.csv", try_parse_dates=True)
print(df)
```

## Filtering by single dates
We can filter by a single date by casting the desired date string to a `Date` object
in a filter expression:
 
```python
filtered_df = df.filter(
    pl.col("Date") == datetime(1995, 10, 16),
)
print(filtered_df)
```
 

Note we are using the lowercase `datetime` method rather than the uppercase `Datetime` data type.
## Filtering by a date range
We can filter by a range of dates using the `is_between` method in a filter expression with the start and end dates:
   
```python
filtered_range_df = df.filter(
    pl.col("Date").is_between(datetime(1995, 7, 1), datetime(1995, 11, 1)),
)
print(filtered_range_df)
```
   

## Filtering with negative dates
Say you are working with an archeologist and are dealing in negative dates.
Polars can parse and store them just fine, but the Python `datetime` library
does not. So for filtering, you should use attributes in the `.dt` namespace:
 
```python
ts = pl.Series(["-1300-05-23", "-1400-03-02"]).str.to_date()
negative_dates_df = pl.DataFrame({"ts": ts, "values": [3, 4]})
negative_dates_filtered_df = negative_dates_df.filter(pl.col("ts").dt.year() < -1300)
print(negative_dates_filtered_df)
```

