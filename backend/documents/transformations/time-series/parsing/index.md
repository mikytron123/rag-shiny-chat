# Parsing


Polars has native support for parsing time series data and doing more sophisticated operations such as temporal grouping and resampling.


## Datatypes


Polars has the following datetime datatypes:


* `Date`: Date representation e.g. 2014-07-08. It is internally represented as days since UNIX epoch encoded by a 32-bit signed integer.
* `Datetime`: Datetime representation e.g. 2014-07-08 07:00:00. It is internally represented as a 64 bit integer since the Unix epoch and can have different units such as ns, us, ms.
* `Duration`: A time delta type that is created when subtracting `Date/Datetime`. Similar to `timedelta` in Python.
* `Time`: Time representation, internally represented as nanoseconds since midnight.


## Parsing dates from a file


When loading from a CSV file Polars attempts to parse dates and times if the `try_parse_dates` flag is set to `True`:





 

```python

df = pl.read_csv("docs/data/apple_stock.csv", try_parse_dates=True)
print(df)

```





   [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")











On the other hand binary formats such as parquet have a schema that is respected by Polars.


## Casting strings to dates


You can also cast a column of datetimes encoded as strings to a datetime type. You do this by calling the string `str.to_date` method and passing the format of the date string:





   

```python

df = pl.read_csv("docs/data/apple_stock.csv", try_parse_dates=False)

df = df.with_columns(pl.col("Date").str.to_date("%Y-%m-%d"))
print(df)

```





     [Available on feature csv](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag csv")  [Available on feature dtype-date](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dtype-date")











[The format string specification can be found here.](https://docs.rs/chrono/latest/chrono/format/strftime/index.html).


## Extracting date features from a date column


You can extract data features such as the year or day from a date column using the `.dt` namespace on a date column:





 

```python

df_with_year = df.with_columns(pl.col("Date").dt.year().alias("year"))
print(df_with_year)

```





 











## Mixed offsets


If you have mixed offsets (say, due to crossing daylight saving time),
then you can use `utc=True` and then convert to your time zone:





     [Available on feature timezone](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag timezone")

```python

data = [
    "2021-03-27T00:00:00+0100",
    "2021-03-28T00:00:00+0100",
    "2021-03-29T00:00:00+0200",
    "2021-03-30T00:00:00+0200",
]
mixed_parsed = (
    pl.Series(data)
    .str.to_datetime("%Y-%m-%dT%H:%M:%S%z")
    .dt.convert_time_zone("Europe/Brussels")
)
print(mixed_parsed)

```





     [Available on feature dtype-datetime](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dtype-datetime")  [Available on feature timezones](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag timezones")









