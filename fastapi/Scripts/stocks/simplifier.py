import os
import uvicorn
from fastapi import APIRouter, FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from stocks.report.downloader import fetch_and_save_annual_report
from stocks.report.extract import run as extract_pdf
from stocks.report.prompt import analyze_text

router = APIRouter()
PORT = 8002

@router.get("/")
def simplify_report(symbol: str = Query(..., description="Ticker symbol e.g. RELIANCE")):
    email = os.getenv("mail")
    password = os.getenv("password")
    
    if not email or not password:
        raise HTTPException(status_code=500, detail="Missing Screener credentials in environment.")
        
    try:
        # Check if already processed
        save_dir = os.path.join("documents", symbol.upper())
        output_path = os.path.join(save_dir, f"{symbol}_analysis.md")
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                analysis = f.read()
            return {"symbol": symbol, "analysis": analysis, "saved_to": output_path, "cached": True}

        # Step 1: Download Report
        filepath = fetch_and_save_annual_report(symbol, email, password)
        if not filepath:
            raise HTTPException(status_code=404, detail=f"Could not find or download report for {symbol}")
            
        # Step 2: Extract text from PDF
        extracted_text = extract_pdf(pdf_path=filepath, out_format="md", save=False, show=False)
        if not extracted_text:
            raise HTTPException(status_code=500, detail="Failed to extract text from the PDF.")
            
        # Step 3: Analyze text with LLM
        analysis = analyze_text(extracted_text)
        if analysis and analysis.startswith("Error"):
            raise HTTPException(status_code=500, detail=analysis)
            
        # Save the analysis to the same folder as the PDF
        save_dir = os.path.dirname(filepath)
        output_path = os.path.join(save_dir, f"{symbol}_analysis.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(analysis)
            
        return {"symbol": symbol, "analysis": analysis, "saved_to": output_path}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_app():
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
