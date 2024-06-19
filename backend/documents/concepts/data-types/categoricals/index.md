# Categorical data


Categorical data represents string data where the values in the column have a finite set of values (usually way smaller than the length of the column). You can think about columns on gender, countries, currency pairings, etc. Storing these values as plain strings is a waste of memory and performance as we will be repeating the same string over and over again. Additionally, in the case of joins we are stuck with expensive string comparisons.


That is why Polars supports encoding string values in dictionary format. Working with categorical data in Polars can be done with two different DataTypes: `Enum`,`Categorical`. Both have their own use cases which we will explain further on this page.
First we will look at what a categorical is in Polars.


In Polars a categorical is defined as a string column which is encoded by a dictionary. A string column would be split into two elements: encodings and the actual string values.




| String Column | Categorical Column |
| --- | --- |
| | Series | | --- | | Polar Bear | | Panda Bear | | Brown Bear | | Panda Bear | | Brown Bear | | Brown Bear | | Polar Bear | | | | Physical | | --- | | 0 | | 1 | | 2 | | 1 | | 2 | | 2 | | 0 | | | Categories | | --- | | Polar Bear | | Panda Bear | | Brown Bear | | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |


The physical `0` in this case encodes (or maps) to the value 'Polar Bear', the value `1` encodes to 'Panda Bear' and the value `2` to 'Brown Bear'. This encoding has the benefit of only storing the string values once. Additionally, when we perform operations (e.g. sorting, counting) we can work directly on the physical representation which is much faster than the working with string data.


### `Enum` vs `Categorical`


Polars supports two different DataTypes for working with categorical data: `Enum` and `Categorical`. When the categories are known up front use `Enum`. When you don't know the categories or they are not fixed then you use `Categorical`. In case your requirements change along the way you can always cast from one to the other.


 Python



```python

enum_dtype = pl.Enum(["Polar", "Panda", "Brown"])
enum_series = pl.Series(["Polar", "Panda", "Brown", "Brown", "Polar"], dtype=enum_dtype)
cat_series = pl.Series(
    ["Polar", "Panda", "Brown", "Brown", "Polar"], dtype=pl.Categorical
)

```




From the code block above you can see that the `Enum` data type requires the upfront while the categorical data type infers the categories.


#### `Categorical` data type


The `Categorical` data type is a flexible one. Polars will add categories on the fly if it sees them. This sounds like a strictly better version compared to the `Enum` data type as we can simply infer the categories, however inferring comes at a cost. The main cost here is we have no control over our encodings.


Consider the following scenario where we append the following two categorical `Series`


 Python



```python

cat_series = pl.Series(
    ["Polar", "Panda", "Brown", "Brown", "Polar"], dtype=pl.Categorical
)
cat2_series = pl.Series(
    ["Panda", "Brown", "Brown", "Polar", "Polar"], dtype=pl.Categorical
)
# Triggers a CategoricalRemappingWarning: Local categoricals have different encodings, expensive re-encoding is done
print(cat_series.append(cat2_series))

```




Polars encodes the string values in order as they appear. So the series would look like this:




| cat\_series | cat2\_series |
| --- | --- |
| | | Physical | | --- | | 0 | | 1 | | 2 | | 2 | | 0 | | | Categories | | --- | | Polar | | Panda | | Brown | | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | | | | Physical | | --- | | 0 | | 1 | | 1 | | 2 | | 2 | | | Categories | | --- | | Panda | | Brown | | Polar | | | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | |


Combining the `Series` becomes a non-trivial task which is expensive as the physical value of `0` represents something different in both `Series`. Polars does support these types of operations for convenience, however in general these should be avoided due to its slower performance as it requires making both encodings compatible first before doing any merge operations.


##### Using the global string cache


One way to handle this problem is to enable a `StringCache`. When you enable the `StringCache` strings are no longer encoded in the order they appear on a per-column basis. Instead, the string cache ensures a single encoding for each string. The string `Polar` will always map the same physical for all categorical columns made under the string cache.
Merge operations (e.g. appends, joins) are cheap as there is no need to make the encodings compatible first, solving the problem we had above.


 Python



```python

with pl.StringCache():
    cat_series = pl.Series(
        ["Polar", "Panda", "Brown", "Brown", "Polar"], dtype=pl.Categorical
    )
    cat2_series = pl.Series(
        ["Panda", "Brown", "Brown", "Polar", "Polar"], dtype=pl.Categorical
    )
    print(cat_series.append(cat2_series))

```




However, the string cache does come at a small performance hit during construction of the `Series` as we need to look up / insert the string value in the cache. Therefore, it is preferred to use the `Enum` Data Type if you know your categories in advance.


#### `Enum data type`


In the `Enum` data type we specify the categories in advance. This way we ensure categoricals from different columns or different datasets have the same encoding and there is no need for expensive re-encoding or cache lookups.


 Python



```python

dtype = pl.Enum(["Polar", "Panda", "Brown"])
cat_series = pl.Series(["Polar", "Panda", "Brown", "Brown", "Polar"], dtype=dtype)
cat2_series = pl.Series(["Panda", "Brown", "Brown", "Polar", "Polar"], dtype=dtype)
print(cat_series.append(cat2_series))

```




Polars will raise an `OutOfBounds` error when a value is encountered which is not specified in the `Enum`.


 Python



```python

dtype = pl.Enum(["Polar", "Panda", "Brown"])
try:
    cat_series = pl.Series(["Polar", "Panda", "Brown", "Black"], dtype=dtype)
except Exception as e:
    print(e)

```python






```
conversion from `str` to `enum` failed in column '' for 1 out of 4 values: ["Black"]

Ensure that all values in the input column are present in the categories of the enum datatype.

```

### Comparisons


The following types of comparisons operators are allowed for categorical data:


* Categorical vs Categorical
* Categorical vs String


#### `Categorical` Type


For the `Categorical` type comparisons are valid if they have the same global cache set or if they have the same underlying categories in the same order.


 Python



```python

with pl.StringCache():
    cat_series = pl.Series(["Brown", "Panda", "Polar"], dtype=pl.Categorical)
    cat_series2 = pl.Series(["Polar", "Panda", "Black"], dtype=pl.Categorical)
    print(cat_series == cat_series2)

```







For `Categorical` vs `String` comparisons Polars uses lexical ordering to determine the result:


 Python



```python

cat_series = pl.Series(["Brown", "Panda", "Polar"], dtype=pl.Categorical)
print(cat_series <= "Cat")

```







 Python



```python

cat_series = pl.Series(["Brown", "Panda", "Polar"], dtype=pl.Categorical)
cat_series_utf = pl.Series(["Panda", "Panda", "Polar"])
print(cat_series <= cat_series_utf)

```







#### `Enum` Type


For `Enum` type comparisons are valid if they have the same categories.


 Python



```python

dtype = pl.Enum(["Polar", "Panda", "Brown"])
cat_series = pl.Series(["Brown", "Panda", "Polar"], dtype=dtype)
cat_series2 = pl.Series(["Polar", "Panda", "Brown"], dtype=dtype)
print(cat_series == cat_series2)

```







For `Enum` vs `String` comparisons the order within the categories is used instead of lexical ordering. In order for a comparison to be valid all values in the `String` column should be present in the `Enum` categories list.


 Python



```python

try:
    cat_series = pl.Series(
        ["Low", "Medium", "High"], dtype=pl.Enum(["Low", "Medium", "High"])
    )
    cat_series <= "Excellent"
except Exception as e:
    print(e)

```python






```
conversion from `str` to `enum` failed in column '' for 1 out of 1 values: ["Excellent"]

Ensure that all values in the input column are present in the categories of the enum datatype.

```python


 Python



```
dtype = pl.Enum(["Low", "Medium", "High"])
cat_series = pl.Series(["Low", "Medium", "High"], dtype=dtype)
print(cat_series <= "Medium")

```python






```
shape: (3,)
Series: '' [bool]
[
    true
    true
    false
]

```python


 Python



```
dtype = pl.Enum(["Low", "Medium", "High"])
cat_series = pl.Series(["Low", "Medium", "High"], dtype=dtype)
cat_series2 = pl.Series(["High", "High", "Low"], dtype=dtype)
print(cat_series <= cat_series2)

```python






```
shape: (3,)
Series: '' [bool]
[
    true
    true
    false
]

```