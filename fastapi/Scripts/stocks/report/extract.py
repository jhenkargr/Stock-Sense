import os
import re
import json
import pdfplumber


# ─────────────────────────────────────────────
#  Supabase helper
# ─────────────────────────────────────────────

def get_supabase():
    """Return a Supabase client, or None if unavailable."""
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stocks.supabase_client import get_supabase_client
        client = get_supabase_client()
        if client:
            buckets = client.storage.list_buckets()
            names = [b.name if hasattr(b, 'name') else b.get('name') for b in buckets]
            if "simplifier" not in names:
                client.storage.create_bucket("simplifier")
                print("✅ Created 'simplifier' storage bucket.")
        return client
    except Exception as e:
        print(f"Supabase unavailable: {e}")
        return None


# ─────────────────────────────────────────────
#  Text / table helpers
# ─────────────────────────────────────────────

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def table_to_markdown(table: list) -> str:
    if not table or not table[0]:
        return ""
    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table]
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    widths = [max(max(len(rows[r][c]) for r in range(len(rows))), 3) for c in range(col_count)]

    def fmt_row(row):
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"

    separator = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt_row(rows[0]), separator] + [fmt_row(r) for r in rows[1:]])


def table_to_text(table: list) -> str:
    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table]
    return "\n".join("  |  ".join(row) for row in rows)


# ─────────────────────────────────────────────
#  PDF extraction
# ─────────────────────────────────────────────

def extract_pdf(pdf_path: str) -> list[dict]:
    """Extract text and tables from every page. Returns a list of page dicts."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"📑 Total pages: {total}")
        for i, page in enumerate(pdf.pages):
            text = clean_text(page.extract_text(x_tolerance=3, y_tolerance=3) or "")
            tables = page.extract_tables() or []
            pages.append({"page": i + 1, "text": text, "tables": tables})
            print(f"  ✅ Page {i+1}/{total} — {len(text):,} chars, {len(tables)} table(s)")
    return pages


# ─────────────────────────────────────────────
#  Formatters
# ─────────────────────────────────────────────

def to_markdown(pages: list, name: str) -> str:
    lines = [f"# {name}\n"]
    for p in pages:
        lines.append(f"---\n## Page {p['page']}\n")
        if p["text"]:
            lines.append(p["text"] + "\n")
        for idx, table in enumerate(p["tables"]):
            lines.append(f"\n**Table {idx+1} — Page {p['page']}:**\n")
            lines.append(table_to_markdown(table) + "\n")
    return "\n".join(lines)


def to_plain_text(pages: list, name: str) -> str:
    lines = [f"DOCUMENT: {name}\n{'='*60}\n"]
    for p in pages:
        lines += [f"\n{'─'*40}", f"PAGE {p['page']}", f"{'─'*40}\n"]
        if p["text"]:
            lines.append(p["text"] + "\n")
        for idx, table in enumerate(p["tables"]):
            lines += [f"\n[TABLE {idx+1}]", table_to_text(table), ""]
    return "\n".join(lines)


def to_json(pages: list, name: str) -> str:
    chunks = [
        {
            "source": name,
            "page": p["page"],
            "text": p["text"],
            "tables": [
                {"table_index": i + 1, "markdown": table_to_markdown(t), "raw": t}
                for i, t in enumerate(p["tables"])
            ],
        }
        for p in pages
    ]
    return json.dumps({"document": name, "pages": chunks}, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────

def run(pdf_path: str, out_format: str = "md", save: bool = True, show: bool = False) -> str | None:
    """
    Extract text from *pdf_path* and return it as a string.
    - out_format: "md" | "txt" | "json"
    - save: save output file locally under documents/<symbol>/
    - show: print a preview to the console
    """
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    symbol   = os.path.basename(os.path.dirname(pdf_path))
    expected_name = f"{pdf_name}_extracted.{out_format}"
    supabase = get_supabase()

    # Check Supabase cache first
    if supabase:
        try:
            files = supabase.storage.from_("simplifier").list(f"documents/{symbol}")
            if isinstance(files, list) and expected_name in [f["name"] for f in files]:
                print(f"✅ Found {expected_name} in Supabase — using cached version.")
                content = supabase.storage.from_("simplifier").download(
                    f"documents/{symbol}/{expected_name}"
                ).decode("utf-8")
                if save:
                    out_path = os.path.join("documents", symbol, expected_name)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✅ Saved → {out_path}")
                return content
        except Exception as e:
            print(f"Supabase check failed: {e}")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None

    # Extract from PDF
    print(f"📄 Extracting: {pdf_path}")
    pages = extract_pdf(pdf_path)

    if out_format == "md":
        content = to_markdown(pages, pdf_name)
    elif out_format == "txt":
        content = to_plain_text(pages, pdf_name)
    else:
        content = to_json(pages, pdf_name)

    total_chars  = sum(len(p["text"]) for p in pages)
    total_tables = sum(len(p["tables"]) for p in pages)
    print(f"\n📊 Pages: {len(pages)}  |  Chars: {total_chars:,}  |  Tables: {total_tables}  |  ~{total_chars//4:,} tokens")

    if save:
        out_path = os.path.join("documents", symbol, expected_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Saved → {out_path}")

    if show:
        print(f"\n{'═'*60}\nPREVIEW (first 3000 chars):\n{'═'*60}\n")
        print(content[:3000])
        if len(content) > 3000:
            print(f"\n… [{len(content)-3000:,} more chars]")

    # Upload to Supabase
    if supabase:
        try:
            supabase.storage.from_("simplifier").upload(
                f"documents/{symbol}/{expected_name}",
                content.encode("utf-8"),
                {"upsert": "true", "content-type": "text/plain"},
            )
            print("✅ Uploaded extracted text to Supabase.")
        except Exception as e:
            print(f"Supabase upload failed: {e}")

    return content