import os
from dotenv import load_dotenv
import snowflake.connector
import json

load_dotenv()

EMBED_MODEL = "snowflake-arctic-embed-l-v2.0"
VECTOR_DIM    = 1024
TABLE_NAME = "DOCUMENT_EMBEDDINGS"

def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema = os.getenv("SNOWFLAKE_SCHEMA")
    )


def ensure_table(con) -> None:
    with con.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                id       INTEGER AUTOINCREMENT PRIMARY KEY,
                source   VARCHAR,
                chunk_id INTEGER,
                content  VARCHAR,
                embedding VECTOR(FLOAT, {VECTOR_DIM})
            )
        """)
    print(f"Table '{TABLE_NAME}' is ready.")

def embed_text(con, text: str) -> list[float]:
    """
    Used when embedding single text such as query
    """
    with con.cursor() as cur:
        cur.execute(
            "SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024(%s, %s)",
            (EMBED_MODEL, text),
        )
        return cur.fetchone()[0]
    
def embed_batch(con, texts: list[str]) -> list[list[float]]:
    """
    Faster than calling embed_text() in a loop.
    """

    parts  = ["SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024(%s, %s) AS emb"] * len(texts)
    params = []
    for text in texts:
        params.extend([EMBED_MODEL, text])
 
    with con.cursor() as cur:
        cur.execute(" UNION ALL ".join(parts), params)
        return [row[0] for row in cur.fetchall()]

def insert_batch(con, source: str, chunk_ids: list[int], contents: list[str], embeddings: list[list[float]], table: str = TABLE_NAME) -> None:
    """
    Insert a batch of chunks + embeddings into the vector table.
    """
    
    select_rows = " UNION ALL ".join(
        [f"SELECT %s, %s, %s, PARSE_JSON(%s)::VECTOR(FLOAT, {VECTOR_DIM})"] * len(chunk_ids)
    )

    params = []
    for chunk_id, content, emb in zip(chunk_ids, contents, embeddings):
        params.extend([source, chunk_id, content, json.dumps(emb)])
 
    with con.cursor() as cur:
        cur.execute(f"""
            INSERT INTO {table} (source, chunk_id, content, embedding)
            {select_rows}
            """,
            params,
        )

def clear_source(con, source: str, table: str = TABLE_NAME) -> None:
    """
    Remove all existing rows for a source before re-inserting.
    """
    
    with con.cursor() as cur:
        cur.execute(f"DELETE FROM {table} WHERE source = %s", (source,))

def similarity_search(con, query_text: str, top_k: int = 5,
                      table: str = TABLE_NAME) -> list[dict]:
    """
    Embed a query and return the top-k most similar chunks.
    """
    query_embedding = embed_text(con, query_text)
 
    with con.cursor() as cur:
        cur.execute(
            f"""
            SELECT
                chunk_id,
                source,
                content,
                VECTOR_COSINE_SIMILARITY(
                    embedding,
                    PARSE_JSON(%s)::VECTOR(FLOAT, {VECTOR_DIM})
                ) AS score
            FROM {table}
            ORDER BY score DESC
            LIMIT %s
            """,
            (json.dumps(query_embedding), top_k),
        )
        col_names = [d[0].lower() for d in cur.description]
        return [dict(zip(col_names, row)) for row in cur.fetchall()]
