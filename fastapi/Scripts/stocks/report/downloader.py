import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv('../.env')


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
            # Make sure the bucket exists
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
#  PDF helpers
# ─────────────────────────────────────────────

def get_filename_from_url(url: str) -> str:
    """Extract a .pdf filename from a URL, falling back to a default."""
    path = unquote(urlparse(url).path)
    filename = os.path.basename(path)
    if not filename or not filename.lower().endswith(".pdf"):
        filename = "annual_report.pdf"
    return filename


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def existing_hashes(directory: str) -> dict[str, str]:
    """Return {sha256: filename} for every PDF already in *directory*."""
    result = {}
    if not os.path.exists(directory):
        return result
    for name in os.listdir(directory):
        if name.lower().endswith(".pdf"):
            with open(os.path.join(directory, name), "rb") as f:
                result[sha256(f.read())] = name
    return result


# ─────────────────────────────────────────────
#  Screener scraper
# ─────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


def get_latest_annual_report(symbol: str, email: str, password: str) -> dict | None:
    """
    Log into Screener.in and return the latest annual-report metadata:
    {"title": ..., "pdf_url": ...}, or None on failure.
    """
    session = requests.Session()

    # 1. Grab CSRF token from the login page
    print("🔐 Logging into Screener.in …")
    login_page = session.get("https://www.screener.in/login/", headers=HEADERS, timeout=15)
    soup = BeautifulSoup(login_page.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if not csrf_input:
        print("❌ CSRF token not found.")
        return None

    # 2. Log in
    session.post(
        "https://www.screener.in/login/",
        data={"csrfmiddlewaretoken": csrf_input["value"], "username": email, "password": password},
        headers={**HEADERS, "Referer": "https://www.screener.in/login/"},
        timeout=15,
    )

    # 3. Fetch the company page
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    print(f"🔍 Fetching: {url}")
    resp = session.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 4. Find annual report links in the #documents section
    section = soup.find("section", {"id": "documents"})
    if not section:
        print("❌ Documents section not found.")
        return None

    for a in section.find_all("a", href=True):
        title = a.get_text(strip=True)
        if "Financial Year" in title:
            print(f"📄 Found: {title}")
            return {"title": title, "pdf_url": a["href"]}

    print("❌ No annual reports found.")
    return None


# ─────────────────────────────────────────────
#  PDF downloader
# ─────────────────────────────────────────────

def download_pdf(url: str, save_dir: str) -> str | None:
    """
    Download a PDF from *url* into *save_dir*.
    Skips saving if an identical file (by SHA-256) already exists.
    Returns the saved filepath, or None on failure.
    """
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n📥 Downloading: {url}")

    session = requests.Session()
    # Warm up cookies on the base domain
    try:
        session.get(f"{urlparse(url).scheme}://{urlparse(url).netloc}", headers=HEADERS, timeout=15)
    except Exception:
        pass

    try:
        response = session.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

    content = response.content
    if not content:
        print("❌ Downloaded file is empty.")
        return None

    # Basic PDF validation
    if not content[:5].startswith(b"%PDF"):
        if b"<html" in content[:500].lower():
            print("❌ Server returned HTML instead of a PDF.")
            return None
        print("⚠️  File may not be a valid PDF — proceeding anyway.")

    size_kb = len(content) / 1024
    size_str = f"{size_kb/1024:.2f} MB" if size_kb >= 1024 else f"{size_kb:.2f} KB"
    file_hash = sha256(content)
    print(f"📦 Size: {size_str}  |  Hash: {file_hash[:16]}…")

    # Duplicate check
    hashes = existing_hashes(save_dir)
    if file_hash in hashes:
        existing = hashes[file_hash]
        print(f"⚠️  Duplicate — identical file already saved as '{save_dir}/{existing}'")
        return os.path.join(save_dir, existing)

    # Resolve filename (avoid conflicts)
    filename = get_filename_from_url(url)
    filepath = os.path.join(save_dir, filename)
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(save_dir, f"{name}_{counter}{ext}")
            counter += 1

    with open(filepath, "wb") as f:
        f.write(content)

    print(f"✅ Saved → {filepath}")
    return filepath


# ─────────────────────────────────────────────
#  Main pipeline
# ─────────────────────────────────────────────

def fetch_and_save_annual_report(symbol: str, email: str, password: str) -> str | None:
    """
    1. Check Supabase for an existing PDF.
    2. If not found, scrape Screener.in and download the latest annual report.
    3. Upload the new PDF to Supabase.
    Returns the local filepath, or None on failure.
    """
    print("=" * 60)
    print(f"  Annual Report Downloader  —  {symbol.upper()}")
    print("=" * 60)

    save_dir = os.path.join("documents", symbol.upper())
    supabase = get_supabase()

    # Check Supabase first
    if supabase:
        try:
            files = supabase.storage.from_("simplifier").list(f"documents/{symbol.upper()}")
            pdf_files = [f["name"] for f in files if f["name"].endswith(".pdf")]
            if pdf_files:
                print(f"✅ Found PDF in Supabase — downloading locally…")
                content = supabase.storage.from_("simplifier").download(
                    f"documents/{symbol.upper()}/{pdf_files[0]}"
                )
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(save_dir, pdf_files[0])
                with open(filepath, "wb") as f:
                    f.write(content)
                print(f"✅ Saved → {filepath}")
                return filepath
        except Exception as e:
            print(f"Supabase check failed: {e}")

    # Scrape and download
    report = get_latest_annual_report(symbol, email, password)
    if not report:
        print("❌ Could not retrieve annual report metadata.")
        return None

    print(f"\n📋 Latest: {report['title']}")
    filepath = download_pdf(report["pdf_url"], save_dir)

    # Upload to Supabase
    if filepath and supabase:
        try:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as f:
                supabase.storage.from_("simplifier").upload(
                    f"documents/{symbol.upper()}/{filename}",
                    f.read(),
                    {"upsert": "true"},
                )
            print("✅ Uploaded PDF to Supabase.")
        except Exception as e:
            print(f"Supabase upload failed: {e}")

    return filepath