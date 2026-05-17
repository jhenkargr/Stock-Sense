import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv('../.env')

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_filename_from_url(url: str) -> str:
    """Extract a .pdf filename from a URL, falling back to a default."""
    path = unquote(urlparse(url).path)
    filename = os.path.basename(path)
    if not filename or not filename.lower().endswith(".pdf"):
        filename = "annual_report.pdf"
    return filename


def calculate_hash(file_content: bytes) -> str:
    """Return the SHA-256 hex-digest of raw bytes."""
    return hashlib.sha256(file_content).hexdigest()


def get_existing_hashes(directory: str) -> dict[str, str]:
    """
    Walk *directory* and return {sha256_hex: filename} for every PDF found.
    Returns an empty dict if the directory doesn't exist yet.
    """
    hashes: dict[str, str] = {}
    if not os.path.exists(directory):
        return hashes

    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "rb") as f:
                file_hash = calculate_hash(f.read())
            hashes[file_hash] = filename

    return hashes


# ─────────────────────────────────────────────
#  Screener scraper
# ─────────────────────────────────────────────

def get_latest_annual_report(
    symbol: str,
    email: str,
    password: str,
) -> dict | None:
    """
    Log into Screener.in and return the latest annual-report metadata for
    *symbol* as {"title": ..., "pdf_url": ...}, or None on failure.
    """
    session = requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }

    # ── 1. Fetch login page and grab CSRF token ──────────────────────────────
    print("🔐 Logging into Screener.in …")
    login_page = session.get("https://www.screener.in/login/", headers=headers, timeout=15)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if not csrf_input:
        print("❌ Could not find CSRF token on login page.")
        return None
    csrf = csrf_input["value"]

    # ── 2. POST credentials ───────────────────────────────────────────────────
    login_resp = session.post(
        "https://www.screener.in/login/",
        data={
            "csrfmiddlewaretoken": csrf,
            "username": email,
            "password": password,
        },
        headers={**headers, "Referer": "https://www.screener.in/login/"},
        timeout=15,
    )

    if "logout" not in login_resp.text.lower():
        print("⚠️  Login may have failed — check your credentials.")

    # ── 3. Fetch company page ─────────────────────────────────────────────────
    company_url = f"https://www.screener.in/company/{symbol}/consolidated/"
    print(f"🔍 Fetching company page: {company_url}")
    resp = session.get(company_url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # ── 4. Locate the #documents section ─────────────────────────────────────
    section = soup.find("section", {"id": "documents"})
    if not section:
        print("❌ Documents section not found on the company page.")
        return None

    # ── 5. Collect "Financial Year XXXX" links ────────────────────────────────
    annual_reports: list[dict] = []
    for a in section.find_all("a", href=True):
        title = a.get_text(strip=True)
        if "Financial Year" in title:
            annual_reports.append({"title": title, "pdf_url": a["href"]})

    if not annual_reports:
        print("❌ No annual reports found in the documents section.")
        return None

    # First entry is the latest
    latest = annual_reports[0]
    print(f"📄 Found: {latest['title']}")
    return latest


# ─────────────────────────────────────────────
#  PDF downloader with duplicate detection
# ─────────────────────────────────────────────

def download_pdf(url: str, save_dir: str = "reports") -> str | None:
    """
    Download a PDF from *url* into *save_dir*.

    • Uses browser-like headers to avoid 403 errors.
    • Computes SHA-256 of the downloaded content and refuses to save
      duplicates that are already present in *save_dir*.
    • Returns the filepath of the saved (or already-existing) PDF,
      or None on failure.
    """
    os.makedirs(save_dir, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "application/pdf,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": f"{urlparse(url).scheme}://{urlparse(url).netloc}/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    print(f"\n📥 Downloading PDF …\n   {url}")
    session = requests.Session()

    # Warm up cookies on the base domain
    try:
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        session.get(base_url, headers=headers, timeout=15)
    except Exception:
        pass

    # ── Download ──────────────────────────────────────────────────────────────
    try:
        response = session.get(url, headers=headers, timeout=60)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print("💡 The server might require authentication or the link has expired.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: could not reach the server.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout: server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

    pdf_content = response.content

    # ── Validate ──────────────────────────────────────────────────────────────
    if not pdf_content:
        print("❌ Downloaded file is empty.")
        return None

    if not pdf_content[:5].startswith(b"%PDF"):
        content_type = response.headers.get("Content-Type", "unknown")
        print(f"⚠️  Content-Type: {content_type} — may not be a valid PDF.")
        if b"<html" in pdf_content[:500].lower() or b"<!doctype" in pdf_content[:500].lower():
            print("❌ Server returned an HTML page instead of a PDF.")
            return None

    # ── Size & hash ───────────────────────────────────────────────────────────
    file_size_kb = len(pdf_content) / 1024
    size_str = (
        f"{file_size_kb / 1024:.2f} MB" if file_size_kb >= 1024 else f"{file_size_kb:.2f} KB"
    )
    downloaded_hash = calculate_hash(pdf_content)

    print(f"📦 Size : {size_str}")
    print(f"🔑 Hash : {downloaded_hash[:16]}…")

    # ── Duplicate check ───────────────────────────────────────────────────────
    existing_hashes = get_existing_hashes(save_dir)
    if downloaded_hash in existing_hashes:
        existing_file = existing_hashes[downloaded_hash]
        print(f"\n⚠️  DUPLICATE DETECTED!")
        print(f"   Identical PDF already saved as: '{save_dir}/{existing_file}'")
        print("🚫 File NOT saved (duplicate).")
        return os.path.join(save_dir, existing_file)

    # ── Resolve filename / handle naming conflicts ────────────────────────────
    filename = get_filename_from_url(url)
    filepath = os.path.join(save_dir, filename)

    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(save_dir, filename)
            counter += 1
        print(f"📝 Filename adjusted to avoid conflict: {filename}")

    # ── Save ──────────────────────────────────────────────────────────────────
    with open(filepath, "wb") as f:
        f.write(pdf_content)

    print(f"\n✅ PDF saved successfully!")
    print(f"   📁 Path : {filepath}")
    print(f"   📦 Size : {size_str}")
    return filepath


# ─────────────────────────────────────────────
#  Orchestrator
# ─────────────────────────────────────────────

def fetch_and_save_annual_report(symbol: str, email: str, password: str) -> str | None:
    """
    End-to-end pipeline:
      1. Log into Screener and get the latest annual-report URL.
      2. Download the PDF.
      3. Save to  reports/<SYMBOL>/  with duplicate detection.

    Returns the saved filepath or None.
    """
    print("=" * 60)
    print(f"  Annual Report Downloader  —  {symbol.upper()}")
    print("=" * 60)
    
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        if supabase:
            buckets = supabase.storage.list_buckets()
            bucket_names = [b.name if hasattr(b, 'name') else b.get('name') for b in buckets]
            if "simplifier" not in bucket_names:
                supabase.storage.create_bucket("simplifier")
                print("✅ Created new 'simplifier' storage bucket.")
                
            files = supabase.storage.from_("simplifier").list(f"documents/{symbol.upper()}")
            if isinstance(files, list):
                pdf_files = [f["name"] for f in files if f["name"].endswith(".pdf")]
                if pdf_files:
                    print(f"✅ Found PDF in Supabase! Downloading...")
                    pdf_bytes = supabase.storage.from_("simplifier").download(f"documents/{symbol.upper()}/{pdf_files[0]}")
                    save_dir = os.path.join("documents", symbol.upper())
                    os.makedirs(save_dir, exist_ok=True)
                    filepath = os.path.join(save_dir, pdf_files[0])
                    with open(filepath, "wb") as f:
                        f.write(pdf_bytes)
                    return filepath
    except Exception as e:
        print("Supabase connection error:", e)

    # Step 1 – scrape
    report = get_latest_annual_report(symbol, email, password)
    if not report:
        print("❌ Could not retrieve annual report metadata. Aborting.")
        return None

    print(f"\n📋 Latest Annual Report : {report['title']}")
    print(f"   URL                  : {report['pdf_url']}")

    # Step 2 – download into documents/<symbol>/
    save_dir = os.path.join("documents", symbol.upper())
    filepath = download_pdf(report["pdf_url"], save_dir=save_dir)

    if filepath:
        try:
            from supabase_client import get_supabase_client
            supabase = get_supabase_client()
            if supabase:
                filename = os.path.basename(filepath)
                with open(filepath, "rb") as f:
                    supabase.storage.from_("simplifier").upload(f"documents/{symbol.upper()}/{filename}", f.read(), {"upsert": "true"})
                print("✅ Uploaded PDF to Supabase Storage (bucket 'simplifier')")
        except Exception as e:
            print("Supabase connection error:", e)

    return filepath

