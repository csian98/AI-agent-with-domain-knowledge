import os, sys

sys.path.append("pylib/")
import snowflake.connector

from qdrant_engine import QdrantEngine
from snowflake_util import *

TABLE_NAME = "DOCUMENT_EMBEDDINGS"


def get_data(conn):
    with conn.cursor() as cur:
        cur.execute(f"SELECT chunk_id, source, content FROM {TABLE_NAME}")
        df = cur.fetch_pandas_all()

    return df


def main():
    qdrant = QdrantEngine("qdrant", "chunks", "BAAI/bge-small-en-v1.5")
    qdrant.reset()

    conn = get_connection()
    df = get_data(conn)

    size = len(df)
    for idx, row in df.iterrows():
        print(f"\r[{idx + 1}/{size}] Insert into qdrant...", end="")

        qdrant.upload(row["CHUNK_ID"], row["SOURCE"], row["CONTENT"])

    print("\nComplete uploading...")
    qdrant.close()


if __name__ == "__main__":
    main()
