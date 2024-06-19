# Grouping


## Grouping by fixed windows


We can calculate temporal statistics using `group_by_dynamic` to group rows into days/months/years etc.


### Annual average example


In following simple example we calculate the annual average closing price of Apple stock prices. We first load the data from CSV:





 

```python

df = pl.read_csv("docs/data/apple_stock.csv", try_parse_dates=True)
df = df.sort("Date")
print(df)

```





 












Info


The dates are sorted in ascending order - if they are not sorted in this way the `group_by_dynamic` output will not be correct!



To get the annual average closing price we tell `group_by_dynamic` that we want to:


* group by the `Date` column on an annual (`1y`) basis
* take the mean values of the `Close` column for each year:





 

```python

annual_average_df = df.group_by_dynamic("Date", every="1y").agg(pl.col("Close").mean())

df_with_year = annual_average_df.with_columns(pl.col("Date").dt.year().alias("year"))
print(df_with_year)

```





   [Available on feature dynamic\_group\_by](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dynamic_group_by")








The annual average closing price is then:





### Parameters for `group_by_dynamic`


A dynamic window is defined by a:


* **every**: indicates the interval of the window
* **period**: indicates the duration of the window
* **offset**: can be used to offset the start of the windows


The value for `every` sets how often the groups start. The time period values are flexible - for example we could take:


* the average over 2 year intervals by replacing `1y` with `2y`
* the average over 18 month periods by replacing `1y` with `1y6mo`


We can also use the `period` parameter to set how long the time period for each group is. For example, if we set the `every` parameter to be `1y` and the `period` parameter to be `2y` then we would get groups at one year intervals where each groups spanned two years.


If the `period` parameter is not specified then it is set equal to the `every` parameter so that if the `every` parameter is set to be `1y` then each group spans `1y` as well.


Because ***every*** does not have to be equal to ***period***, we can create many groups in a very flexible way. They may overlap
or leave boundaries between them.


Let's see how the windows for some parameter combinations would look. Let's start out boring. 🥱


* every: 1 day -> `"1d"`
* period: 1 day -> `"1d"`



```python

this creates adjacent windows of the same size
|--|
   |--|
      |--|

```

* every: 1 day -> `"1d"`
* period: 2 days -> `"2d"`



```python

these windows have an overlap of 1 day
|----|
   |----|
      |----|

```

* every: 2 days -> `"2d"`
* period: 1 day -> `"1d"`



```python

this would leave gaps between the windows
data points that in these gaps will not be a member of any group
|--|
       |--|
              |--|

```

#### `truncate`


The `truncate` parameter is a Boolean variable that determines what datetime value is associated with each group in the output. In the example above the first data point is on 23rd February 1981. If `truncate = True` (the default) then the date for the first year in the annual average is 1st January 1981. However, if `truncate = False` then the date for the first year in the annual average is the date of the first data point on 23rd February 1981. Note that `truncate` only affects what's shown in the
`Date` column and does not affect the window boundaries.


### Using expressions in `group_by_dynamic`


We aren't restricted to using simple aggregations like `mean` in a group by operation - we can use the full range of expressions available in Polars.


In the snippet below we create a `date range` with every **day** (`"1d"`) in 2021 and turn this into a `DataFrame`.


Then in the `group_by_dynamic` we create dynamic windows that start every **month** (`"1mo"`) and have a window length of `1` month. The values that match these dynamic windows are then assigned to that group and can be aggregated with the powerful expression API.


Below we show an example where we use **group\_by\_dynamic** to compute:


* the number of days until the end of the month
* the number of days in a month





     

```python

df = (
    pl.date_range(
        start=date(2021, 1, 1),
        end=date(2021, 12, 31),
        interval="1d",
        eager=True,
    )
    .alias("time")
    .to_frame()
)

out = df.group_by_dynamic("time", every="1mo", period="1mo", closed="left").agg(
    pl.col("time").cum_count().reverse().head(3).alias("day/eom"),
    ((pl.col("time") - pl.col("time").first()).last().dt.total_days() + 1).alias(
        "days_in_month"
    ),
)
print(out)

```





       [Available on feature dynamic\_group\_by](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dynamic_group_by")  [Available on feature dtype-date](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dtype-date")  [Available on feature range](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag range")











## Grouping by rolling windows


The rolling operation, `rolling`, is another entrance to the `group_by`/`agg` context. But different from the `group_by_dynamic` where the windows are fixed by a parameter `every` and `period`. In a `rolling`, the windows are not fixed at all! They are determined
by the values in the `index_column`.


So imagine having a time column with the values `{2021-01-06, 2021-01-10}` and a `period="5d"` this would create the following
windows:



```python

2021-01-01   2021-01-06
    |----------|

       2021-01-05   2021-01-10
             |----------|

```

Because the windows of a rolling group by are always determined by the values in the `DataFrame` column, the number of
groups is always equal to the original `DataFrame`.


## Combining group by operations


Rolling and dynamic group by operations can be combined with normal group by operations.


Below is an example with a dynamic group by.





 

```python

df = pl.DataFrame(
    {
        "time": pl.datetime_range(
            start=datetime(2021, 12, 16),
            end=datetime(2021, 12, 16, 3),
            interval="30m",
            eager=True,
        ),
        "groups": ["a", "a", "a", "b", "b", "a", "a"],
    }
)
print(df)

```





 














 

```python

out = df.group_by_dynamic(
    "time",
    every="1h",
    closed="both",
    group_by="groups",
    include_boundaries=True,
).agg(pl.len())
print(out)

```





   [Available on feature dynamic\_group\_by](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag dynamic_group_by")









