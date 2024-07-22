# Strings
The following section discusses operations performed on `String` data, which is a frequently used `DataType` when working with `DataFrames`. However, processing strings can often be inefficient due to their unpredictable memory size, causing the CPU to access many random memory locations. To address this issue, Polars utilizes Arrow as its backend, which stores all strings in a contiguous block of memory. As a result, string traversal is cache-optimal and predictable for the CPU.
String processing functions are available in the `str` namespace.
##### Accessing the string namespace
The `str` namespace can be accessed through the `.str` attribute of a column with `String` data type. In the following example, we create a column named `animal` and compute the length of each element in the column in terms of the number of bytes and the number of characters. If you are working with ASCII text, then the results of these two computations will be the same, and using `lengths` is recommended since it is faster.
   
```python
df = pl.DataFrame({"animal": ["Crab", "cat and dog", "rab$bit", None]})
out = df.select(
    pl.col("animal").str.len_bytes().alias("byte_count"),
    pl.col("animal").str.len_chars().alias("letter_count"),
)
print(out)
```
   

#### String parsing
Polars offers multiple methods for checking and parsing elements of a string. Firstly, we can use the `contains` method to check whether a given pattern exists within a substring. Subsequently, we can extract these patterns and replace them using other methods, which will be demonstrated in upcoming examples.
##### Check for existence of a pattern
To check for the presence of a pattern within a string, we can use the contains method. The `contains` method accepts either a regular substring or a regex pattern, depending on the value of the `literal` parameter. If the pattern we're searching for is a simple substring located either at the beginning or end of the string, we can alternatively use the `starts_with` and `ends_with` functions.
     
```python
out = df.select(
    pl.col("animal"),
    pl.col("animal").str.contains("cat|bit").alias("regex"),
    pl.col("animal").str.contains("rab$", literal=True).alias("literal"),
    pl.col("animal").str.starts_with("rab").alias("starts_with"),
    pl.col("animal").str.ends_with("dog").alias("ends_with"),
)
print(out)
```

##### Extract a pattern
The `extract` method allows us to extract a pattern from a specified string. This method takes a regex pattern containing one or more capture groups, which are defined by parentheses `()` in the pattern. The group index indicates which capture group to output.
 
```python
df = pl.DataFrame(
    {
        "a": [
            "http://vote.com/ballon_dor?candidate=messi&ref=polars",
            "http://vote.com/ballon_dor?candidat=jorginho&ref=polars",
            "http://vote.com/ballon_dor?candidate=ronaldo&ref=polars",
        ]
    }
)
out = df.select(
    pl.col("a").str.extract(r"candidate=(\w+)", group_index=1),
)
print(out)
```
 

To extract all occurrences of a pattern within a string, we can use the `extract_all` method. In the example below, we extract all numbers from a string using the regex pattern `(\d+)`, which matches one or more digits. The resulting output of the `extract_all` method is a list containing all instances of the matched pattern within the string.
 
```python
df = pl.DataFrame({"foo": ["123 bla 45 asd", "xyz 678 910t"]})
out = df.select(
    pl.col("foo").str.extract_all(r"(\d+)").alias("extracted_nrs"),
)
print(out)
```
 

##### Replace a pattern
We have discussed two methods for pattern matching and extraction thus far, and now we will explore how to replace a pattern within a string. Similar to `extract` and `extract_all`, Polars provides the `replace` and `replace_all` methods for this purpose. In the example below we replace one match of `abc` at the end of a word (`\b`) by `ABC` and we replace all occurrence of `a` with `-`.
   
```python
df = pl.DataFrame({"id": [1, 2], "text": ["123abc", "abc456"]})
out = df.with_columns(
    pl.col("text").str.replace(r"abc\b", "ABC"),
    pl.col("text").str.replace_all("a", "-", literal=True).alias("text_replace_all"),
)
print(out)
```


#### API documentation
In addition to the examples covered above, Polars offers various other string manipulation methods for tasks such as formatting, stripping, splitting, and more. To explore these additional methods, you can go to the API documentation of your chosen programming language for Polars.