# Contexts
Polars has developed its own Domain Specific Language (DSL) for transforming data. The language is very easy to use and allows for complex queries that remain human readable. The two core components of the language are Contexts and Expressions, the latter we will cover in the next section.
A context, as implied by the name, refers to the context in which an expression needs to be evaluated. There are three main contexts [1](#fn:1):
1. Selection: `df.select(...)`, `df.with_columns(...)`
2. Filtering: `df.filter()`
3. Group by / Aggregation: `df.group_by(...).agg(...)`
The examples below are performed on the following `DataFrame`:
 
```python
df = pl.DataFrame(
    {
        "nrs": [1, 2, 3, None, 5],
        "names": ["foo", "ham", "spam", "egg", None],
        "random": np.random.rand(5),
        "groups": ["A", "A", "B", "C", "B"],
    }
)
print(df)
```
 

## Selection
The selection context applies expressions over columns. A `select` may produce new columns that are aggregations, combinations of expressions, or literals.
The expressions in a selection context must produce `Series` that are all the same length or have a length of 1. Literals are treated as length-1 `Series`.
When some expressions produce length-1 `Series` and some do not, the length-1 `Series` will be broadcast to match the length of the remaining `Series`.
Note that broadcasting can also occur within expressions: for instance, in `pl.col.value() / pl.col.value.sum()`, each element of the `value` column is divided by the column's sum.
 
```python
out = df.select(
    pl.sum("nrs"),
    pl.col("names").sort(),
    pl.col("names").first().alias("first name"),
    (pl.mean("nrs") * 10).alias("10xnrs"),
)
print(out)
```
 

As you can see from the query, the selection context is very powerful and allows you to evaluate arbitrary expressions independent of (and in parallel to) each other.
Similar to the `select` statement, the `with_columns` statement also enters into the selection context. The main difference between `with_columns` and `select` is that `with_columns` retains the original columns and adds new ones, whereas `select` drops the original columns.
 
```python
df = df.with_columns(
    pl.sum("nrs").alias("nrs_sum"),
    pl.col("random").count().alias("count"),
)
print(df)
```
 

## Filtering
The filtering context filters a `DataFrame` based on one or more expressions that evaluate to the `Boolean` data type.
 
```python
out = df.filter(pl.col("nrs") > 2)
print(out)
```
 

## Group by / aggregation
In the `group_by` context, expressions work on groups and thus may yield results of any length (a group may have many members).
 
```python
out = df.group_by("groups").agg(
    pl.sum("nrs"),  # sum nrs by groups
    pl.col("random").count().alias("count"),  # count group members
    # sum random where name != null
    pl.col("random").filter(pl.col("names").is_not_null()).sum().name.suffix("_sum"),
    pl.col("names").reverse().alias("reversed names"),
)
print(out)
```
 

As you can see from the result all expressions are applied to the group defined by the `group_by` context. Besides the standard `group_by`, `group_by_dynamic`, and `group_by_rolling` are also entrances to the group by context.
---
1. There are additional List and SQL contexts which are covered later in this guide. But for simplicity, we leave them out of scope for now. [↩](#fnref:1 "Jump back to footnote 1 in the text")