# Visualization
Data in a Polars `DataFrame` can be visualized using common visualization libraries.
We illustrate plotting capabilities using the Iris dataset. We scan a CSV and then do a group-by on the `species` column and get the mean of the `petal_length`.
 Python
```python
import polars as pl
path = "docs/data/iris.csv"
df = pl.scan_csv(path).group_by("species").agg(pl.col("petal_length").mean()).collect()
print(df)
```

## Built-in plotting with hvPlot
Polars has a `plot` method to create interactive plots using hvPlot.
 Python
```python
df.plot.bar(
    x="species",
    y="petal_length",
    width=650,
)
```

hvplot\_bar
 
 

## Matplotlib
To create a bar chart we can pass columns of a `DataFrame` directly to Matplotlib as a `Series` for each column. Matplotlib does not have explicit support for Polars objects but Matplotlib can accept a Polars `Series` because it can convert each Series to a numpy array, which is zero-copy for numeric
data without null values.
 Python
```python
import matplotlib.pyplot as plt
plt.bar(x=df["species"], height=df["petal_length"])
```

## Seaborn, Plotly & Altair
Seaborn, Plotly & Altair can accept a Polars `DataFrame` by leveraging the dataframe interchange protocol, which offers zero-copy conversion where possible.
### Seaborn
 Python
```python
import seaborn as sns
sns.barplot(
    df,
    x="species",
    y="petal_length",
)
```
### Plotly
 Python
```python
import plotly.express as px
px.bar(
    df,
    x="species",
    y="petal_length",
    width=400,
)
```

 
   
### Altair
 Python
```python
import altair as alt
alt.Chart(df, width=700).mark_bar().encode(x="species:N", y="petal_length:Q")
```