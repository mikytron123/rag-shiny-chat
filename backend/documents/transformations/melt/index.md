# Melts


Melt operations unpivot a DataFrame from wide format to long format


## Dataset





 

```python

import polars as pl

df = pl.DataFrame(
    {
        "A": ["a", "b", "a"],
        "B": [1, 3, 5],
        "C": [10, 11, 12],
        "D": [2, 4, 6],
    }
)
print(df)

```





 











## Eager + lazy


`Eager` and `lazy` have the same API.





 

```python

out = df.melt(id_vars=["A", "B"], value_vars=["C", "D"])
print(out)

```





 









