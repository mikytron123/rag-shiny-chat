# Numpy
Polars expressions support NumPy ufuncs.
for a list on all supported numpy functions.
This means that if a function is not provided by Polars, we can use NumPy and we still have fast columnar operation through the NumPy API.
### Example
```python
import polars as pl
import numpy as np
df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
out = df.select(np.log(pl.all()).name.suffix("_log"))
print(out)
```

### Interoperability
Polars `Series` have support for NumPy universal functions (ufuncs). Element-wise functions such as `np.exp()`, `np.cos()`, `np.div()`, etc. all work with almost zero overhead.
However, as a Polars-specific remark: missing values are a separate bitmask and are not visible by NumPy. This can lead to a window function or a `np.convolve()` giving flawed or incomplete results.
Convert a Polars `Series` to a NumPy array with the `.to_numpy()` method. Missing values will be replaced by `np.nan` during the conversion.