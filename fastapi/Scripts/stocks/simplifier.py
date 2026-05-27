import os
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from stocks.report.downloader import fetch_and_save_annual_report
from stocks.report.extract import run as extract_pdf
from stocks.report.prompt import analyze_text

router = APIRouter()
PORT = 8002


# ─────────────────────────────────────────────
#  Supabase helper
# ─────────────────────────────────────────────

def get_supabase():
    """Return a Supabase client, or None if unavailable."""
    try:
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
#  API route
# ─────────────────────────────────────────────

@router.get("/")
def simplify_report(symbol: str = Query(..., description="Ticker symbol, e.g. RELIANCE")):
    email    = os.getenv("mail")
    password = os.getenv("password")

    if not email or not password:
        raise HTTPException(status_code=500, detail="Missing Screener credentials in environment.")

    symbol = symbol.upper()
    supabase = get_supabase()

    # 1. Return cached analysis if it exists in Supabase, or fetch cached extracted text
    extracted_text = None
    if supabase:
        try:
            expected_name = f"{symbol}_cohere_analysis.md"
            files = supabase.storage.from_("simplifier").list(f"documents/{symbol}")
            if isinstance(files, list):
                file_names = [f["name"] for f in files]
                if expected_name in file_names:
                    print(f"✅ Returning cached analysis for {symbol}.")
                    content = supabase.storage.from_("simplifier").download(
                        f"documents/{symbol}/{expected_name}"
                    ).decode("utf-8")
                    return {"symbol": symbol, "analysis": content, "cached": True}
                
                # Check for cached extracted text to bypass PDF download/extraction
                extracted_file = None
                for name in file_names:
                    if name.endswith("_extracted.md") or name.endswith("_extracted.txt") or name.endswith("_extracted.json"):
                        extracted_file = name
                        break
                
                if extracted_file:
                    print(f"✅ Found cached extracted text in Supabase: {extracted_file}")
                    extracted_text = supabase.storage.from_("simplifier").download(
                        f"documents/{symbol}/{extracted_file}"
                    ).decode("utf-8")
        except Exception as e:
            print(f"Supabase cache check failed: {e}")

    # 2. If no cached extracted text, download the annual report PDF and extract
    if not extracted_text:
        filepath = fetch_and_save_annual_report(symbol, email, password)
        if not filepath:
            raise HTTPException(status_code=404, detail=f"Could not find or download report for {symbol}.")

        # Extract text from the PDF
        extracted_text = extract_pdf(pdf_path=filepath, out_format="md", save=False, show=False)
        if not extracted_text:
            raise HTTPException(status_code=500, detail="Failed to extract text from the PDF.")

    # 4. Analyze with LLM
    analysis = analyze_text(extracted_text, symbol=symbol)
    if not analysis or analysis.startswith("Error"):
        raise HTTPException(status_code=500, detail=analysis or "Analysis failed.")

    # 5. Upload analysis to Supabase
    if supabase:
        try:
            expected_name = f"{symbol}_cohere_analysis.md"
            supabase.storage.from_("simplifier").upload(
                f"documents/{symbol}/{expected_name}",
                analysis.encode("utf-8"),
                {"upsert": "true", "content-type": "text/markdown"},
            )
            print("✅ Uploaded analysis to Supabase.")
        except Exception as e:
            print(f"Supabase upload failed: {e}")

    return {"symbol": symbol, "analysis": analysis, "cached": False}


# ─────────────────────────────────────────────
#  App setup
# ─────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    print(f"Docs at http://127.0.0.1:{PORT}/docs")
    uvicorn.run("stocks.simplifier:app", host="127.0.0.1", port=PORT, reload=True)