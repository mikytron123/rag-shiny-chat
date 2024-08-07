# Expressions
Polars has a powerful concept called expressions that is central to its very fast performance.
Expressions are at the core of many data science operations:
* taking a sample of rows from a column
* multiplying values in a column
* extracting a column of years from dates
* convert a column of strings to lowercase
* and so on!
However, expressions are also used within other operations:
* taking the mean of a group in a `group_by` operation
* calculating the size of groups in a `group_by` operation
* taking the sum horizontally across columns
Polars performs these core data transformations very quickly by:
* automatic query optimization on each expression
* automatic parallelization of expressions on many columns
An expression is a tree of operations that describe how to construct one or more
Series. As the outputs are Series, it is straightforward to
apply a sequence of expressions (similar to method chaining in pandas) each of which
transforms the output from the previous step.
If this seems abstract and confusing - don't worry! People quickly develop an intuition for expressions
just by looking at a few examples. We'll do that next!
## Examples
The following is an expression:
     
```python
pl.col("foo").sort().head(2)
```
     

The snippet above says:
1. Select column "foo"
2. Then sort the column (not in reversed order)
3. Then take the first two values of the sorted output
The power of expressions is that every expression produces a new expression, and that they
can be *piped* together. You can run an expression by passing them to one of Polars execution contexts.
Here we run two expressions by running `df.select`:
 
```python
df.select(pl.col("foo").sort().head(2), pl.col("bar").filter(pl.col("foo") == 1).sum())
```
 

All expressions are run in parallel, meaning that separate Polars expressions are **embarrassingly parallel**. Note that within an expression there may be more parallelization going on.
## Conclusion
This is the tip of the iceberg in terms of possible expressions. There are a ton more, and they can be combined in a variety of ways. This page is intended to get you familiar with the concept of expressions, in the section on [expressions](../../expressions/operators/) we will dive deeper.