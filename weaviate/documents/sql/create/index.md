# CREATE
In Polars, the `SQLContext` provides a way to execute SQL statements against `LazyFrames` and `DataFrames` using SQL syntax. One of the SQL statements that can be executed using `SQLContext` is the `CREATE TABLE` statement, which is used to create a new table.
The syntax for the `CREATE TABLE` statement in Polars is as follows:
```sql
CREATE TABLE table_name
AS
SELECT ...
```
In this syntax, `table_name` is the name of the new table that will be created, and `SELECT ...` is a SELECT statement that defines the data that will be inserted into the table.
Here's an example of how to use the `CREATE TABLE` statement in Polars:
 Python
   
```python
data = {"name": ["Alice", "Bob", "Charlie", "David"], "age": [25, 30, 35, 40]}
df = pl.LazyFrame(data)
ctx = pl.SQLContext(my_table=df, eager=True)
result = ctx.execute(
    """
    CREATE TABLE older_people
    AS
    SELECT * FROM my_table WHERE age > 30
"""
)
print(ctx.execute("SELECT * FROM older_people"))
```

In this example, we use the `execute()` method of the `SQLContext` to execute a `CREATE TABLE` statement that creates a new table called `older_people` based on a SELECT statement that selects all rows from the `my_table` DataFrame where the `age` column is greater than 30.
Note
Note that the result of a `CREATE TABLE` statement is not the table itself. The table is registered in the `SQLContext`. In case you want to turn the table back to a `DataFrame` you can use a `SELECT * FROM ...` statement
