import argparse
import pdfplumber
from pathlib import Path
from pdfplumber import page


PDFS = [Path("./domain-knowledge/Ads cookbook .pdf"), Path("./ads_data_html/licensing.pdf")]
RAW_TXT  = Path("./raw-txt")
PAGE_SEP = "=== PAGE {page} ==="

# Words starting past this fraction of page width belong to the right column.
COLUMN_SPLIT_RATIO = 0.47
# Minimum fraction of words that must be in the right column for a page to be treated as two-column layout.
TWO_COL_THRESHOLD = 0.15


def _is_two_column(page: page) -> tuple[bool, float]:
    words = page.extract_words() # words = a list of dictionaries, containing attributes like "text", "x0", "top", "x1", "bottom", "width", and "height"
    if not words:
        return False, None

    mid = page.width * COLUMN_SPLIT_RATIO
    # Allow a 40-pt dead-zone around the midpoint to avoid false positives
    left  = [w for w in words if w["x1"] < mid - 20]
    right = [w for w in words if w["x0"] > mid + 20]

    if not right:
        return False, None

    right_fraction = len(right) / len(words)
    if right_fraction < TWO_COL_THRESHOLD:
        return False, None
    
    right_x0s = [w["x0"] for w in right]
    split_x = min(right_x0s) - 10        # a little padding
    return True, split_x


def _extract_column(page, x_start: float, x_end: float) -> str:
    cropped = page.crop((x_start, 0, x_end, page.height))
    text = cropped.extract_text(x_tolerance=1, y_tolerance=3)
    return text or ""


def pdf_to_txt(pdf_path: Path) -> str:
    parts = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)

        for page_num, page in enumerate(pdf.pages, start=1):
            two_col, split_x = _is_two_column(page)

            if two_col:
                left_text  = _extract_column(page, 0, split_x)
                right_text = _extract_column(page, split_x, page.width)
                text = left_text
                if right_text.strip():
                    text = text.rstrip("\n") + "\n\n" + right_text
            else:
                text = page.extract_text(x_tolerance=1, y_tolerance=3)

            parts.append(f"{PAGE_SEP.format(page=page_num)}\n\n{text}")
            print(f"  Page {page_num}/{total} {'[2-col]' if two_col else '[1-col]'}",
                  end="\r")

    print()
    return "\n\n".join(parts)


def convert_all():
    RAW_TXT.mkdir(parents=True, exist_ok=True)

    for pdf in PDFS:

        out_path = RAW_TXT / (pdf.stem + ".txt")

        print(f"Converting: {pdf.name}")
        try:
            text = pdf_to_txt(pdf)
            out_path.write_text(text, encoding="utf-8")
            print(f"  Saved: {out_path}")
        except Exception as e:
            print(f"  Failed: {pdf.name} | {e}")


def convert_new(saved_pdfs):
    RAW_TXT.mkdir(parents=True, exist_ok=True)
    saved_txt = []

    for pdf in saved_pdfs:
        out_path = RAW_TXT / (pdf.stem + ".txt")
        saved_txt.append(out_path)

        print(f"Converting: {pdf.name}")
        try:
            text = pdf_to_txt(pdf)
            out_path.write_text(text, encoding="utf-8")
            print(f"  Saved: {out_path}")
        except Exception as e:
            print(f"  Failed: {pdf.name} | {e}")

    return saved_txt

if __name__ == "__main__":
    convert_all()
