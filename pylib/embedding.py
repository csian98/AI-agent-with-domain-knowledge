import argparse
import re
import time
from pathlib import Path

from langchain_text_splitters import CharacterTextSplitter
import snowflake_util as sf

from pylib.qdrant_engine import QdrantEngine

RAW_TXT = Path("./raw-txt")

CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50
BATCH_SIZE    = 20
 
PAGE_SEP_RE = re.compile(r"=== PAGE \d+ ===")


def load_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")
 
 
def strip_page_markers(text: str) -> str:
    return PAGE_SEP_RE.sub("", text)
 

def make_chunks(text: str) -> list[str]:
    splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
        strip_whitespace=True,
    )
    return [c for c in splitter.split_text(text) if len(c.strip()) > 20]
 
 
def process_source(con, path: Path, qdrant = None) -> None:
    if not path.exists():
        print(f" {path} does not exsists")
        return
 
    print(f"\n── Processing: {path} ──")
 
    raw = load_txt(path)
    clean = strip_page_markers(raw)
 
    # Chunk
    chunks = make_chunks(clean)
    print(f"  -> {len(chunks)} chunks")
 
    path_name = path.stem
    total = len(chunks)

    sf.clear_source(con, path_name)
 
    # Embed + insert in batches
    for batch_start in range(0, total, BATCH_SIZE):
        batch_texts = chunks[batch_start: batch_start + BATCH_SIZE]
        batch_ids   = list(range(batch_start, batch_start + len(batch_texts)))
 
        print(f"  Embedding {batch_start+1}–"
              f"{batch_start+len(batch_texts)}/{total}...", end=" ", flush=True)
        try:
            embeddings = sf.embed_batch(con, batch_texts)
        except Exception as e:
            print(f"\n  Embed failed at batch {batch_start}: {e}")
            time.sleep(2)
            continue
 
        sf.insert_batch(con, path_name, batch_ids, batch_texts, embeddings)
        if qdrant:
            size = len(batch_ids)
            for idx in range(size):
                print(f"\r[{idx + 1}/{size}]Upload Qdrant...", end='')
                qdrant.upload(path_name, batch_ids[idx], batch_texts[idx])
            print(f"\n Finish Upload Qdrant...")
        
        print("")
        time.sleep(0.5)
 
    print(f"  Done — {total} chunks stored for '{path_name}'.")

def upload_new_pdfs(paths, qdrant: QdrantEngine):
    con = sf.get_connection()
    try:
        # sf.ensure_table(con)
        for path in paths:
            process_source(con, path, qdrant)
    finally:
        con.close()

    print("\nAll new sources processed")
    

def main():
    paths = Path(RAW_TXT).glob("*.txt")
 
    con = sf.get_connection()
    try:
        sf.ensure_table(con)
        for path in paths:
            process_source(con, path)
    finally:
        con.close()
 
    print("\nAll sources processed.")


if __name__ == "__main__":
    main()
