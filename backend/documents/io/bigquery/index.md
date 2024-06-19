# Google BigQuery


To read or write from GBQ, additional dependencies are needed:


 Python





```python

$ pip install google-cloud-bigquery

```

## Read


We can load a query into a `DataFrame` like this:


 Python


   [Available on feature pyarrow](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag pyarrow")  [Available on feature fsspec](/user-guide/installation/#feature-flags "To use this functionality enable the feature flag fsspec")

```
import polars as pl
from google.cloud import bigquery

client = bigquery.Client()

# Perform a query.
QUERY = (
    'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
    'WHERE state = "TX" '
    'LIMIT 100')
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

df = pl.from_arrow(rows.to_arrow())

```python







## Write


 Python



```
from google.cloud import bigquery

client = bigquery.Client()

# Write DataFrame to stream as parquet file; does not hit disk
with io.BytesIO() as stream:
    df.write_parquet(stream)
    stream.seek(0)
    job = client.load_table_from_file(
        stream,
        destination='tablename',
        project='projectname',
        job_config=bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
        ),
    )
job.result()  # Waits for the job to complete

```