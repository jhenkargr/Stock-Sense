

import json
import os
import re
import pdfplumber


# ═══════════════════════════════════════════════
# ✏️  CONFIGURE HERE
PDF_PATH   = "reports/{symbol}/.pdf"       # <-- change this to your PDF path
OUT_FORMAT = "md"                  # "md" | "txt" | "json"
SAVE_FILE  = True                  # Save output to file?
PRINT_TEXT = True                  # Print extracted text in notebook?
# ═══════════════════════════════════════════════


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def table_to_markdown(table):
    if not table or not table[0]:
        return ""
    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table]
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    widths = [max(max(len(rows[r][c]) for r in range(len(rows))), 3) for c in range(col_count)]

    def fmt_row(row):
        return "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"

    separator = "| " + " | ".join("-" * w for w in widths) + " |"
    lines = [fmt_row(rows[0]), separator] + [fmt_row(r) for r in rows[1:]]
    return "\n".join(lines)


def table_to_text(table):
    rows = [[(cell or "").replace("\n", " ").strip() for cell in row] for row in table]
    return "\n".join("  |  ".join(row) for row in rows)


# ── Extract ───────────────────────────────────────────────────────────────────

def extract_pdf(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"📑 Total pages: {total}\n")
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables() or []
            text   = clean_text(page.extract_text(x_tolerance=3, y_tolerance=3) or "")
            pages.append({"page": i + 1, "text": text, "tables": tables})
            print(f"  ✅ Page {i+1}/{total} — {len(text):,} chars, {len(tables)} table(s)")
    return pages


# ── Formatters ────────────────────────────────────────────────────────────────

def to_markdown(pages, name):
    lines = [f"# {name}\n"]
    for p in pages:
        lines.append(f"---\n## Page {p['page']}\n")
        if p["text"]:
            lines.append(p["text"] + "\n")
        for idx, table in enumerate(p["tables"]):
            lines.append(f"\n**Table {idx+1} — Page {p['page']}:**\n")
            lines.append(table_to_markdown(table) + "\n")
    return "\n".join(lines)


def to_plain_text(pages, name):
    lines = [f"DOCUMENT: {name}\n{'='*60}\n"]
    for p in pages:
        lines += [f"\n{'─'*40}", f"PAGE {p['page']}", f"{'─'*40}\n"]
        if p["text"]:
            lines.append(p["text"] + "\n")
        for idx, table in enumerate(p["tables"]):
            lines += [f"\n[TABLE {idx+1}]", table_to_text(table), ""]
    return "\n".join(lines)


def to_json(pages, name):
    chunks = []
    for p in pages:
        chunks.append({
            "source": name,
            "page": p["page"],
            "text": p["text"],
            "tables": [
                {"table_index": i+1, "markdown": table_to_markdown(t), "raw": t}
                for i, t in enumerate(p["tables"])
            ]
        })
    return json.dumps({"document": name, "pages": chunks}, indent=2, ensure_ascii=False)


# ── Run ───────────────────────────────────────────────────────────────────────

def run(pdf_path: str, out_format=OUT_FORMAT, save=SAVE_FILE, show=PRINT_TEXT):
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"📄 Extracting: {pdf_path}")

    pages = extract_pdf(pdf_path)

    # Format
    if out_format == "md":
        content = to_markdown(pages, pdf_name)
    elif out_format == "txt":
        content = to_plain_text(pages, pdf_name)
    else:
        content = to_json(pages, pdf_name)

    # Stats
    total_chars  = sum(len(p["text"]) for p in pages)
    total_tables = sum(len(p["tables"]) for p in pages)
    print(f"\n📊 Stats:")
    print(f"   Pages        : {len(pages)}")
    print(f"   Total chars  : {total_chars:,}")
    print(f"   Tables found : {total_tables}")
    print(f"   Est. tokens  : ~{total_chars // 4:,}")

    # Save
    if save:
        os.makedirs("llm_output", exist_ok=True)
        out_path = f"llm_output/{pdf_name}.{out_format}"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ Saved → {out_path}")

    # Print preview in notebook
    if show:
        preview = content[:3000]
        print(f"\n{'═'*60}")
        print("📋 PREVIEW (first 3000 chars):")
        print(f"{'═'*60}\n")
        print(preview)
        if len(content) > 3000:
            print(f"\n... [{len(content)-3000:,} more chars] ...")

    return content   # ← pass this directly to any LLM API




