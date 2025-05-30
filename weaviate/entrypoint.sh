/bin/weaviate --host 0.0.0.0 --port $WEAVIATE_PORT --scheme http &

pid=$!

sleep 10

echo 'creating collection'
wget --header 'content-type: application/json' --post-data '{
    "class": "document_collection",
    "properties": [
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "file_path",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "file_name",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "file_type",
            "tokenization": "word"
        },
        {
            "dataType": [
                "int"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "file_size"
        },
        {
            "dataType": [
                "date"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "creation_date"
        },
        {
            "dataType": [
                "date"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "last_modified_date"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": true,
            "name": "text",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "link",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "embedding_model",
            "tokenization": "word"
        }
    ],
    "vectorIndexConfig": {
        "distance": "cosine"
    },
    "vectorIndexType": "hnsw",
    "vectorizer": "none"
}' http://localhost:${WEAVIATE_PORT}/v1/schema

wget --header 'content-type: application/json' --post-data '{
    "class": "cache",
    "properties": [
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": true,
            "name": "query",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "embedding_model",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "llm",
            "tokenization": "word"
        },
        {
            "dataType": [
                "date"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "created_on"
        },
        {
            "dataType": [
                "date"
            ],
            "indexFilterable": true,
            "indexSearchable": false,
            "name": "last_modified_date"
        }
    ],
    "vectorIndexConfig": {
        "distance": "cosine"
    },
    "vectorIndexType": "hnsw",
    "vectorizer": "none"
}' http://localhost:${WEAVIATE_PORT}/v1/schema
echo 'done'

wait $pid