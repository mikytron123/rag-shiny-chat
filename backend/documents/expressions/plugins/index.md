# Expression plugins
Expression plugins are the preferred way to create user defined functions. They allow you to compile a Rust function
and register that as an expression into the Polars library. The Polars engine will dynamically link your function at runtime
and your expression will run almost as fast as native expressions. Note that this works without any interference of Python
and thus no GIL contention.
They will benefit from the same benefits default expressions have:
* Optimization
* Parallelism
* Rust native performance
To get started we will see what is needed to create a custom expression.
## Our first custom expression: Pig Latin
For our first expression we are going to create a pig latin converter. Pig latin is a silly language where in every word
the first letter is removed, added to the back and finally "ay" is added. So the word "pig" would convert to "igpay".
We could of course already do that with expressions, e.g. `col("name").str.slice(1) + col("name").str.slice(0, 1) + "ay"`,
but a specialized function for this would perform better and allows us to learn about the plugins.
### Setting up
We start with a new library as the following `Cargo.toml` file

### Writing the expression
In this library we create a helper function that converts a `&str` to pig-latin, and we create the function that we will
expose as an expression. To expose a function we must add the `#[polars_expr(output_type=DataType)]` attribute and the function
must always accept `inputs: &[Series]` as its first argument.
This is all that is needed on the Rust side. On the Python side we must setup a folder with the same name as defined in
the `Cargo.toml`, in this case "expression\_lib". We will create a folder in the same directory as our Rust `src` folder
named `expression_lib` and we create an `expression_lib/__init__.py`. The resulting file structure should look something like this:
Then we create a new class `Language` that will hold the expressions for our new `expr.language` namespace. The function
name of our expression can be registered. Note that it is important that this name is correct, otherwise the main Polars
package cannot resolve the function name. Furthermore we can set additional keyword arguments that explain to Polars how
this expression behaves. In this case we tell Polars that this function is elementwise. This allows Polars to run this
expression in batches. Whereas for other operations this would not be allowed, think for instance of a sort, or a slice.
```python
# expression_lib/__init__.py
from pathlib import Path
from typing import TYPE_CHECKING
import polars as pl
from polars.plugins import register_plugin_function
from polars.type_aliases import IntoExpr
def pig_latinnify(expr: IntoExpr) -> pl.Expr:
    """Pig-latinnify expression."""
    return register_plugin_function(
        plugin_path=Path(__file__).parent,
        function_name="pig_latinnify",
        args=expr,
        is_elementwise=True,
    )
```
We can then compile this library in our environment by installing `maturin` and running `maturin develop --release`.
And that's it. Our expression is ready to use!
```python
import polars as pl
from expression_lib import pig_latinnify
df = pl.DataFrame(
    {
        "convert": ["pig", "latin", "is", "silly"],
    }
)
out = df.with_columns(pig_latin=pig_latinnify("convert"))
```
Alternatively, you can register a custom namespace, which enables you to write:
```python
out = df.with_columns(
    pig_latin=pl.col("convert").language.pig_latinnify(),
)
```
## Accepting kwargs
If you want to accept `kwargs` (keyword arguments) in a polars expression, all you have to do is define a Rust `struct`
and make sure that it derives `serde::Deserialize`.

On the Python side the kwargs can be passed when we register the plugin.
```python
def append_args(
    expr: IntoExpr,
    float_arg: float,
    integer_arg: int,
    string_arg: str,
    boolean_arg: bool,
) -> pl.Expr:
    """
    This example shows how arguments other than `Series` can be used.
    """
    return register_plugin_function(
        plugin_path=Path(__file__).parent,
        function_name="append_kwargs",
        args=expr,
        kwargs={
            "float_arg": float_arg,
            "integer_arg": integer_arg,
            "string_arg": string_arg,
            "boolean_arg": boolean_arg,
        },
        is_elementwise=True,
    )
```
## Output data types
Output data types of course don't have to be fixed. They often depend on the input types of an expression. To accommodate
this you can provide the `#[polars_expr()]` macro with an `output_type_func` argument that points to a function. This
function can map input fields `&[Field]` to an output `Field` (name and data type).
In the snippet below is an example where we use the utility `FieldsMapper` to help with this mapping.
That's all you need to know to get started. Take a look at [this repo](https://github.com/pola-rs/pyo3-polars/tree/main/example/derive_expression) to see how this all fits together, and at [this tutorial](https://marcogorelli.github.io/polars-plugins-tutorial/)
to gain a more thorough understanding.
## Community plugins
Here is a curated (non-exhaustive) list of community-implemented plugins.
* [polars-xdt](https://github.com/pola-rs/polars-xdt) Polars plugin with extra datetime-related functionality
 which isn't quite in-scope for the main library
* [polars-distance](https://github.com/ion-elgreco/polars-distance) Polars plugin for pairwise distance functions
* [polars-ds](https://github.com/abstractqqq/polars_ds_extension) Polars extension aiming to simplify common numerical/string data analysis procedures
* [polars-hash](https://github.com/ion-elgreco/polars-hash) Stable non-cryptographic and cryptographic hashing functions for Polars
* [polars-reverse-geocode](https://github.com/MarcoGorelli/polars-reverse-geocode) Offline reverse geocoder for finding the closest city
 to a given (latitude, longitude) pair
## Other material
* [Ritchie Vink - Keynote on Polars Plugins](https://youtu.be/jKW-CBV7NUM)
* [Polars plugins tutorial](https://marcogorelli.github.io/polars-plugins-tutorial/) Learn how to write a plugin by
 going through some very simple and minimal examples
* [cookiecutter-polars-plugin](https://github.com/MarcoGorelli/cookiecutter-polars-plugins) Project template for Polars Plugins