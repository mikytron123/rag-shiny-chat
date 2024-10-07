# SELECT
In Polars SQL, the `SELECT` statement is used to retrieve data from a table into a `DataFrame`. The basic syntax of a `SELECT` statement in Polars SQL is as follows:
Here, `column1`, `column2`, etc. are the columns that you want to select from the table. You can also use the wildcard `*` to select all columns. `table_name` is the name of the table or that you want to retrieve data from. In the sections below we will cover some of the more common SELECT variants
 Python
   
```python
df = pl.DataFrame(
    {
        "city": [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "Amsterdam",
        ],
        "country": ["USA", "USA", "USA", "USA", "USA", "Netherlands"],
        "population": [8399000, 3997000, 2705000, 2320000, 1680000, 900000],
    }
)
ctx = pl.SQLContext(population=df, eager=True)
print(ctx.execute("SELECT * FROM population"))
```

### GROUP BY
The `GROUP BY` statement is used to group rows in a table by one or more columns and compute aggregate functions on each group.
 Python
 
```python
result = ctx.execute(
    """
        SELECT country, AVG(population) as avg_population
        FROM population
        GROUP BY country
    """
)
print(result)
```

### ORDER BY
The `ORDER BY` statement is used to sort the result set of a query by one or more columns in ascending or descending order.
 Python
 
```python
result = ctx.execute(
    """
        SELECT city, population
        FROM population
        ORDER BY population
    """
)
print(result)
```

### JOIN
 Python
   
```python
income = pl.DataFrame(
    {
        "city": [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Amsterdam",
            "Rotterdam",
            "Utrecht",
        ],
        "country": [
            "USA",
            "USA",
            "USA",
            "USA",
            "Netherlands",
            "Netherlands",
            "Netherlands",
        ],
        "income": [55000, 62000, 48000, 52000, 42000, 38000, 41000],
    }
)
ctx.register_many(income=income)
result = ctx.execute(
    """
        SELECT country, city, income, population
        FROM population
        LEFT JOIN income on population.city = income.city
    """
)
print(result)
```

### Functions
Polars provides a wide range of SQL functions, including:
* Mathematical functions: `ABS`, `EXP`, `LOG`, `ASIN`, `ACOS`, `ATAN`, etc.
* String functions: `LOWER`, `UPPER`, `LTRIM`, `RTRIM`, `STARTS_WITH`,`ENDS_WITH`.
* Aggregation functions: `SUM`, `AVG`, `MIN`, `MAX`, `COUNT`, `STDDEV`, `FIRST` etc.
* Array functions: `EXPLODE`, `UNNEST`,`ARRAY_SUM`,`ARRAY_REVERSE`, etc.
For a full list of supported functions go the API documentation. The example below demonstrates how to use a function in a query
 Python
 
```python
result = ctx.execute(
    """
        SELECT city, population
        FROM population
        WHERE STARTS_WITH(country,'U')
    """
)
print(result)
```

### Table Functions
In the examples earlier we first generated a DataFrame which we registered in the `SQLContext`. Polars also support directly reading from CSV, Parquet, JSON and IPC in your SQL query using table functions `read_xxx`.
 Python
 
```python
result = ctx.execute(
    """
        SELECT *
        FROM read_csv('docs/data/iris.csv')
    """
)
print(result)
```

