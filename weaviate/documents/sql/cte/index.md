# Common Table Expressions
Common Table Expressions (CTEs) are a feature of SQL that allow you to define a temporary named result set that can be referenced within a SQL statement. CTEs provide a way to break down complex SQL queries into smaller, more manageable pieces, making them easier to read, write, and maintain.
A CTE is defined using the `WITH` keyword followed by a comma-separated list of subqueries, each of which defines a named result set that can be used in subsequent queries. The syntax for a CTE is as follows:
```python
WITH cte_name AS (
    subquery
)
SELECT ...
```
In this syntax, `cte_name` is the name of the CTE, and `subquery` is the subquery that defines the result set. The CTE can then be referenced in subsequent queries as if it were a table or view.
CTEs are particularly useful when working with complex queries that involve multiple levels of subqueries, as they allow you to break down the query into smaller, more manageable pieces that are easier to understand and debug. Additionally, CTEs can help improve query performance by allowing the database to optimize and cache the results of subqueries, reducing the number of times they need to be executed.
Polars supports Common Table Expressions (CTEs) using the WITH clause in SQL syntax. Below is an example
 Python
   
```python
ctx = pl.SQLContext()
df = pl.LazyFrame(
    {"name": ["Alice", "Bob", "Charlie", "David"], "age": [25, 30, 35, 40]}
)
ctx.register("my_table", df)
result = ctx.execute(
    """
    WITH older_people AS (
        SELECT * FROM my_table WHERE age > 30
    )
    SELECT * FROM older_people WHERE STARTS_WITH(name,'C')
""",
    eager=True,
)
print(result)
```

In this example, we use the `execute()` method of the `SQLContext` to execute a SQL query that includes a CTE. The CTE selects all rows from the `my_table` LazyFrame where the `age` column is greater than 30 and gives it the alias `older_people`. We then execute a second SQL query that selects all rows from the `older_people` CTE where the `name` column starts with the letter 'C'.