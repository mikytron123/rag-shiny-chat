from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    model_name_or_path="BAAI/bge-small-en-v1.5", cache_folder="/tmp"
)
