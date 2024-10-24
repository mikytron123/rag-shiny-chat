# Casting
Casting converts the underlying  of a column to a new one. Polars uses Arrow to manage the data in memory and relies on the compute kernels in the Rust implementation to do the conversion. Casting is available with the `cast()` method.
The `cast` method includes a `strict` parameter that determines how Polars behaves when it encounters a value that can't be converted from the source `DataType` to the target `DataType`. By default, `strict=True`, which means that Polars will throw an error to notify the user of the failed conversion and provide details on the values that couldn't be cast. On the other hand, if `strict=False`, any values that can't be converted to the target `DataType` will be quietly converted to `null`.
## Numerics
Let's take a look at the following `DataFrame` which contains both integers and floating point numbers.
 
```python
df = pl.DataFrame(
    {
        "integers": [1, 2, 3, 4, 5],
        "big_integers": [1, 10000002, 3, 10000004, 10000005],
        "floats": [4.0, 5.0, 6.0, 7.0, 8.0],
        "floats_with_decimal": [4.532, 5.5, 6.5, 7.5, 8.5],
    }
)
print(df)
```
 

To perform casting operations between floats and integers, or vice versa, we can invoke the `cast()` function.
 
```python
out = df.select(
    pl.col("integers").cast(pl.Float32).alias("integers_as_floats"),
    pl.col("floats").cast(pl.Int32).alias("floats_as_integers"),
    pl.col("floats_with_decimal")
    .cast(pl.Int32)
    .alias("floats_with_decimal_as_integers"),
)
print(out)
```
 

Note that in the case of decimal values these are rounded downwards when casting to an integer.
##### Downcast
Reducing the memory footprint is also achievable by modifying the number of bits allocated to an element. As an illustration, the code below demonstrates how casting from `Int64` to `Int16` and from `Float64` to `Float32` can be used to lower memory usage.
 
```python
out = df.select(
    pl.col("integers").cast(pl.Int16).alias("integers_smallfootprint"),
    pl.col("floats").cast(pl.Float32).alias("floats_smallfootprint"),
)
print(out)
```
 

#### Overflow
When performing downcasting, it is crucial to ensure that the chosen number of bits (such as 64, 32, or 16) is sufficient to accommodate the largest and smallest numbers in the column. For example, using a 32-bit signed integer (`Int32`) allows handling integers within the range of -2147483648 to +2147483647, while using `Int8` covers integers between -128 to 127. Attempting to cast to a `DataType` that is too small will result in a `ComputeError` thrown by Polars, as the operation is not supported.
 
```python
try:
    out = df.select(pl.col("big_integers").cast(pl.Int8))
    print(out)
except Exception as e:
    print(e)
```
 

```
conversion from `i64` to `i8` failed in column 'big_integers' for 3 out of 5 values: [10000002, 10000004, 10000005]
```
You can set the `strict` parameter to `False`, this converts values that are overflowing to null values.
 
```python
out = df.select(pl.col("big_integers").cast(pl.Int8, strict=False))
print(out)
```
 

## Strings
Strings can be casted to numerical data types and vice versa:
 
```python
df = pl.DataFrame(
    {
        "integers": [1, 2, 3, 4, 5],
        "float": [4.0, 5.03, 6.0, 7.0, 8.0],
        "floats_as_string": ["4.0", "5.0", "6.0", "7.0", "8.0"],
    }
)
out = df.select(
    pl.col("integers").cast(pl.String),
    pl.col("float").cast(pl.String),
    pl.col("floats_as_string").cast(pl.Float64),
)
print(out)
```
 

In case the column contains a non-numerical value, Polars will throw a `ComputeError` detailing the conversion error. Setting `strict=False` will convert the non float value to `null`.
 
```python
df = pl.DataFrame({"strings_not_float": ["4.0", "not_a_number", "6.0", "7.0", "8.0"]})
try:
    out = df.select(pl.col("strings_not_float").cast(pl.Float64))
    print(out)
except Exception as e:
    print(e)
```
 

```
conversion from `str` to `f64` failed in column 'strings_not_float' for 1 out of 5 values: ["not_a_number"]
```
## Booleans
Booleans can be expressed as either 1 (`True`) or 0 (`False`). It's possible to perform casting operations between a numerical `DataType` and a boolean, and vice versa. However, keep in mind that casting from a string (`String`) to a boolean is not permitted.
 
```python
df = pl.DataFrame(
    {
        "integers": [-1, 0, 2, 3, 4],
        "floats": [0.0, 1.0, 2.0, 3.0, 4.0],
        "bools": [True, False, True, False, True],
    }
)
out = df.select(pl.col("integers").cast(pl.Boolean), pl.col("floats").cast(pl.Boolean))
print(out)
```
 

## Dates
Temporal data types such as `Date` or `Datetime` are represented as the number of days (`Date`) and microseconds (`Datetime`) since epoch. Therefore, casting between the numerical types and the temporal data types is allowed.
 
```python
from datetime import date, datetime
df = pl.DataFrame(
    {
        "date": pl.date_range(date(2022, 1, 1), date(2022, 1, 5), eager=True),
        "datetime": pl.datetime_range(
            datetime(2022, 1, 1), datetime(2022, 1, 5), eager=True
        ),
    }
)
out = df.select(pl.col("date").cast(pl.Int64), pl.col("datetime").cast(pl.Int64))
print(out)
```
 

To convert between strings and `Dates`/`Datetimes`, `dt.to_string` and `str.to_datetime` are utilized. Polars adopts the chrono format syntax for formatting. It's worth noting that `str.to_datetime` features additional options that support timezone functionality. Refer to the API documentation for further information.
   
```python
df = pl.DataFrame(
    {
        "date": pl.date_range(date(2022, 1, 1), date(2022, 1, 5), eager=True),
        "string": [
            "2022-01-01",
            "2022-01-02",
            "2022-01-03",
            "2022-01-04",
            "2022-01-05",
        ],
    }
)
out = df.select(
    pl.col("date").dt.to_string("%Y-%m-%d"),
    pl.col("string").str.to_datetime("%Y-%m-%d"),
)
print(out)
```

