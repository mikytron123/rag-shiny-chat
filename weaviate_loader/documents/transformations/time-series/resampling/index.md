# Resampling
We can resample by either:
* upsampling (moving data to a higher frequency)
* downsampling (moving data to a lower frequency)
* combinations of these e.g. first upsample and then downsample
## Downsampling to a lower frequency
Polars views downsampling as a special case of the **group\_by** operation and you can do this with `group_by_dynamic` and `group_by_rolling` - [see the temporal group by page for examples](../rolling/).
## Upsampling to a higher frequency
Let's go through an example where we generate data at 30 minute intervals:
   
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
        "values": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    }
)
print(df)
```


Upsampling can be done by defining the new sampling interval. By upsampling we are adding in extra rows where we do not have data. As such upsampling by itself gives a DataFrame with nulls. These nulls can then be filled with a fill strategy or interpolation.
### Upsampling strategies
In this example we upsample from the original 30 minutes to 15 minutes and then use a `forward` strategy to replace the nulls with the previous non-null value:
 
```python
out1 = df.upsample(time_column="time", every="15m").fill_null(strategy="forward")
print(out1)
```
 

In this example we instead fill the nulls by linear interpolation:
     
```python
out2 = (
    df.upsample(time_column="time", every="15m")
    .interpolate()
    .fill_null(strategy="forward")
)
print(out2)
```
     

