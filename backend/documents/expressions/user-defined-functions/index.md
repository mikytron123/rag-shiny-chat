# User-defined functions (Python)


You should be convinced by now that Polars expressions are so powerful and flexible that there is much less need for custom Python functions
than in other libraries.


Still, you need to have the power to be able to pass an expression's state to a third party library or apply your black box function
over data in Polars.


For this we provide the following expressions:


* `map_batches`
* `map_elements`


## To `map_batches` or to `map_elements`.


These functions have an important distinction in how they operate and consequently what data they will pass to the user.


A `map_batches` passes the `Series` backed by the `expression` as is.


`map_batches` follows the same rules in both the `select` and the `group_by` context, this will
mean that the `Series` represents a column in a `DataFrame`. Note that in the `group_by` context, that column is not yet
aggregated!


Use cases for `map_batches` are for instance passing the `Series` in an expression to a third party library. Below we show how
we could use `map_batches` to pass an expression column to a neural network model.


 Python




 



```python

df.with_columns([
    pl.col("features").map_batches(lambda s: MyNeuralNetwork.forward(s.to_numpy())).alias("activations")
])

```

 Rust





```python

df.with_columns([
    col("features").map(|s| Ok(my_nn.forward(s))).alias("activations")
])

```

Use cases for `map_batches` in the `group_by` context are slim. They are only used for performance reasons, but can quite easily lead to incorrect results. Let me explain why.






```python

df = pl.DataFrame(
    {
        "keys": ["a", "a", "b"],
        "values": [10, 7, 1],
    }
)
print(df)

```












In the snippet above we group by the `"keys"` column. That means we have the following groups:



```python

"a" -> [10, 7]
"b" -> [1]

```

If we would then apply a `shift` operation to the right, we'd expect:



```python

"a" -> [null, 10]
"b" -> [null]

```

Let's try that out and see what we get:






```python

out = df.group_by("keys", maintain_order=True).agg(
    pl.col("values")
    .map_batches(lambda s: s.shift(), is_elementwise=True)
    .alias("shift_map_batches"),
    pl.col("values").shift().alias("shift_expression"),
)
print(out)

```




```
let out = df
    .clone()
    .lazy()
    .group_by(["keys"])
    .agg([
        col("values")
            .map(|s| Ok(Some(s.shift(1))), GetOutput::default())
            // note: the `'shift_map_batches'` alias is just there to show how you
            // get the same output as in the Python API example.
            .alias("shift_map_batches"),
        col("values").shift(lit(1)).alias("shift_expression"),
    ])
    .collect()?;

println!("{}", out);

```python






```
shape: (2, 3)
┌──────┬───────────────────┬──────────────────┐
│ keys ┆ shift_map_batches ┆ shift_expression │
│ ---  ┆ ---               ┆ ---              │
│ str  ┆ list[i64]         ┆ list[i64]        │
╞══════╪═══════════════════╪══════════════════╡
│ a    ┆ [null, 10]        ┆ [null, 10]       │
│ b    ┆ [7]               ┆ [null]           │
└──────┴───────────────────┴──────────────────┘

```

Ouch.. we clearly get the wrong results here. Group `"b"` even got a value from group `"a"` 😵.


This went horribly wrong because `map_batches` applied the function before aggregation, due to the `is_elementwise=True` parameter being provided. So that means the whole column `[10, 7, 1]` got shifted to `[null, 10, 7]` and was then aggregated.


So my advice is to never use `map_batches` in the `group_by` context unless you know you need it and know what you are doing.


## To `map_elements`


Luckily we can fix previous example with `map_elements`. `map_elements` works on the smallest logical elements for that operation.


That is:


* `select context` -> single elements
* `group by context` -> single groups


So with `map_elements` we should be able to fix our example:


 Python




 






```python

out = df.group_by("keys", maintain_order=True).agg(
    pl.col("values")
    .map_elements(lambda s: s.shift(), return_dtype=pl.List(int))
    .alias("shift_map_elements"),
    pl.col("values").shift().alias("shift_expression"),
)
print(out)

```




```
let out = df
    .clone()
    .lazy()
    .group_by([col("keys")])
    .agg([
        col("values")
            .apply(|s| Ok(Some(s.shift(1))), GetOutput::default())
            // note: the `'shift_map_elements'` alias is just there to show how you
            // get the same output as in the Python API example.
            .alias("shift_map_elements"),
        col("values").shift(lit(1)).alias("shift_expression"),
    ])
    .collect()?;
println!("{}", out);

```python






```
shape: (2, 3)
┌──────┬────────────────────┬──────────────────┐
│ keys ┆ shift_map_elements ┆ shift_expression │
│ ---  ┆ ---                ┆ ---              │
│ str  ┆ list[i64]          ┆ list[i64]        │
╞══════╪════════════════════╪══════════════════╡
│ a    ┆ [null, 10]         ┆ [null, 10]       │
│ b    ┆ [null]             ┆ [null]           │
└──────┴────────────────────┴──────────────────┘

```

And observe, a valid result! 🎉


## `map_elements` in the `select` context


In the `select` context, the `map_elements` expression passes elements of the column to the Python function.


*Note that you are now running Python, this will be slow.*


Let's go through some examples to see what to expect. We will continue with the `DataFrame` we defined at the start of
this section and show an example with the `map_elements` function and a counter example where we use the expression API to
achieve the same goals.


### Adding a counter


In this example we create a global `counter` and then add the integer `1` to the global state at every element processed.
Every iteration the result of the increment will be added to the element value.



> Note, this example isn't provided in Rust. The reason is that the global `counter` value would lead to data races when this `apply` is evaluated in parallel. It would be possible to wrap it in a `Mutex` to protect the variable, but that would be obscuring the point of the example. This is a case where the Python Global Interpreter Lock's performance tradeoff provides some safety guarantees.






```python

counter = 0


def add_counter(val: int) -> int:
    global counter
    counter += 1
    return counter + val


out = df.select(
    pl.col("values").map_elements(add_counter).alias("solution_map_elements"),
    (pl.col("values") + pl.int_range(1, pl.len() + 1)).alias("solution_expr"),
)
print(out)

```




```python



```python








### Combining multiple column values


If we want to have access to values of different columns in a single `map_elements` function call, we can create `struct` data
type. This data type collects those columns as fields in the `struct`. So if we'd create a struct from the columns
`"keys"` and `"values"`, we would get the following struct elements:



```python

[
    {"keys": "a", "values": 10},
    {"keys": "a", "values": 7},
    {"keys": "b", "values": 1},
]

```

In Python, those would be passed as `dict` to the calling Python function and can thus be indexed by `field: str`. In Rust, you'll get a `Series` with the `Struct` type. The fields of the struct can then be indexed and downcast.






```python

out = df.select(
    pl.struct(["keys", "values"])
    .map_elements(lambda x: len(x["keys"]) + x["values"])
    .alias("solution_map_elements"),
    (pl.col("keys").str.len_bytes() + pl.col("values")).alias("solution_expr"),
)
print(out)

```




```
let out = df
    .lazy()
    .select([
        // pack to struct to get access to multiple fields in a custom `apply/map`
        as_struct(vec![col("keys"), col("values")])
            // we will compute the len(a) + b
            .apply(
                |s| {
                    // downcast to struct
                    let ca = s.struct_()?;

                    // get the fields as Series
                    let s_a = &ca.fields()[0];
                    let s_b = &ca.fields()[1];

                    // downcast the `Series` to their known type
                    let ca_a = s_a.str()?;
                    let ca_b = s_b.i32()?;

                    // iterate both `ChunkedArrays`
                    let out: Int32Chunked = ca_a
                        .into_iter()
                        .zip(ca_b)
                        .map(|(opt_a, opt_b)| match (opt_a, opt_b) {
                            (Some(a), Some(b)) => Some(a.len() as i32 + b),
                            _ => None,
                        })
                        .collect();

                    Ok(Some(out.into_series()))
                },
                GetOutput::from_type(DataType::Int32),
            )
            // note: the `'solution_map_elements'` alias is just there to show how you
            // get the same output as in the Python API example.
            .alias("solution_map_elements"),
        (col("keys").str().count_matches(lit("."), true) + col("values"))
            .alias("solution_expr"),
    ])
    .collect()?;
println!("{}", out);

```python






```
shape: (3, 2)
┌───────────────────────┬───────────────┐
│ solution_map_elements ┆ solution_expr │
│ ---                   ┆ ---           │
│ i64                   ┆ i64           │
╞═══════════════════════╪═══════════════╡
│ 11                    ┆ 11            │
│ 8                     ┆ 8             │
│ 2                     ┆ 2             │
└───────────────────────┴───────────────┘

```

`Structs` are covered in detail in the next section.


### Return types?


Custom Python functions are black boxes for Polars. We really don't know what kind of black arts you are doing, so we have
to infer and try our best to understand what you meant.


As a user it helps to understand what we do to better utilize custom functions.


The data type is automatically inferred. We do that by waiting for the first non-null value. That value will then be used
to determine the type of the `Series`.


The mapping of Python types to Polars data types is as follows:


* `int` -> `Int64`
* `float` -> `Float64`
* `bool` -> `Boolean`
* `str` -> `String`
* `list[tp]` -> `List[tp]` (where the inner type is inferred with the same rules)
* `dict[str, [tp]]` -> `struct`
* `Any` -> `object` (Prevent this at all times)


Rust types map as follows:


* `i32` or `i64` -> `Int64`
* `f32` or `f64` -> `Float64`
* `bool` -> `Boolean`
* `String` or `str` -> `String`
* `Vec<tp>` -> `List[tp]` (where the inner type is inferred with the same rules)