import requests
import json
import re
import os
import time
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '..', '.env')
load_dotenv(env_path)

# ═══════════════════════════════════════════════
# ✏️  CONFIGURE HERE
# ═══════════════════════════════════════════════
TEXT_FILE       = "llm_output/file.md"
OUTPUT_FILE     = "llm_output/file_analysis.md"
NVIDIA_API_KEY  = os.getenv("NVIDIA_API_KEY")
STREAM          = True
MAX_TOKENS      = 16384
TEMPERATURE     = 0.60
TOP_P           = 0.95
MAX_CONTEXT     = 262144
SAFE_INPUT_LIMIT = MAX_CONTEXT - MAX_TOKENS - 2000
CHUNK_TOKEN_SIZE = 50000
API_URL         = "https://integrate.api.nvidia.com/v1/chat/completions"

# ── Model choices (fallback if primary is down) ──
PRIMARY_MODEL   = "qwen/qwen3.5-122b-a10b"
FALLBACK_MODELS = [
    "qwen/qwen2.5-72b-instruct",
    "meta/llama-3.1-405b-instruct",
    "meta/llama-3.1-70b-instruct",
]

# ── Retry settings ──
MAX_RETRIES     = 3
RETRY_DELAY     = 30    # seconds between retries

# ═══════════════════════════════════════════════
# ✏️  PROMPTS
# ═══════════════════════════════════════════════
CHUNK_INSTRUCTION = """
You are a senior equity research analyst. Analyze this PARTIAL section of a company's Annual Report.
Extract ALL relevant information you can find related to these categories:

1. Company Overview (business model, segments, markets)
2. Financial Performance (revenue, profit, margins, EPS, debt, cash flow)
3. Capital Allocation (CapEx, acquisitions, R&D, expansion projects)
4. Future Outlook & Growth Strategy (guidance, new products, expansion plans)
5. Risks & Concerns (regulatory, competition, macro risks, lawsuits)
6. Dividends & Shareholder Returns (dividends, buybacks, bonus shares)
7. Management & Governance (leadership changes, promoter holding, related party transactions)
8. Competitive Position (market share, competitors, moat)

Extract every number, fact, and detail you can find. This is ONE PART of the full report.
Be thorough. Include all financial figures with exact numbers.
"""

FINAL_INSTRUCTION = """
You are a senior equity research analyst. Below are analyses of DIFFERENT SECTIONS of the same company's Annual Report.

Combine all the information and produce ONE comprehensive, well-structured analysis.

Structure your response EXACTLY in the following sections:

---

## 🏢 1. Company Overview
- What the company does (business model in simple words)
- Key segments / divisions
- Markets & geographies they operate in

---

## 💰 2. Financial Performance
- Revenue, Net Profit, EBITDA (current year vs last year)
- Profit margins (gross, net, operating)
- Earnings Per Share (EPS)
- Debt levels and Debt-to-Equity ratio
- Cash flow from operations
- Any red flags (losses, declining revenue, high debt)

---

## 📈 3. Where Money Was Invested (Capital Allocation)
- Major capital expenditures (CapEx)
- Acquisitions or mergers
- R&D spending
- New plants, infrastructure, or expansion projects
- Investments in subsidiaries or joint ventures

---

## 🔮 4. Future Outlook & Growth Strategy
- Management's guidance for next year (revenue, growth targets)
- New products, services, or markets being targeted
- Expansion plans (domestic and international)
- Key projects under development
- Any tailwinds or opportunities mentioned

---

## ⚠️ 5. Risks & Concerns
- Key risks mentioned by management
- Regulatory or legal issues
- Market competition threats
- Macroeconomic risks (currency, inflation, interest rates)
- Any ongoing lawsuits or liabilities

---

## 🧾 6. Dividends & Shareholder Returns
- Dividend declared (amount per share, yield)
- Share buybacks if any
- Bonus shares or stock splits

---

## 👔 7. Management & Governance
- Key leadership changes
- Promoter holding changes
- Any concerns about corporate governance
- Related party transactions (if significant)

---

## 🏆 8. Competitive Position
- Market share or industry ranking (if mentioned)
- Key competitors
- Competitive advantages (moat) highlighted by management

---

## 📌 9. Key Takeaways for Investors
- Top 5 positive highlights
- Top 3 concerns or watch-out points
- Overall sentiment: Bullish / Neutral / Cautious (with reason)

---

Use simple, clear language. Avoid jargon. Where numbers are available, always include them.
If any section has no data available in the report, write: "Not mentioned in this report."
Remove any duplicate information. Keep the best/most complete version of each fact.
"""


# ═══════════════════════════════════════════════
# ✅  VALIDATION
# ═══════════════════════════════════════════════
if not NVIDIA_API_KEY:
    print("❌ ERROR: NVIDIA_API_KEY not found in .env!")
    # We don't exit here so it can be imported, but it will fail later if used.

ACTIVE_MODEL = None


# ═══════════════════════════════════════════════
# 🔧  CHECK MODEL AVAILABILITY
# ═══════════════════════════════════════════════
def check_model_available(model_name):
    """Quick test to see if a model is available."""
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Say OK"}],
        "max_tokens": 5,
        "stream": False
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return True
        else:
            try:
                err = resp.json().get("error", {}).get("detail", "")
                if "DEGRADED" in str(err).upper():
                    return False
            except Exception:
                pass
            return False
    except Exception:
        return False


def find_working_model():
    """Find a working model from primary + fallbacks."""
    print(f"\n🔍 Checking model availability...")

    # Check primary first
    print(f"   Testing: {PRIMARY_MODEL}...", end=" ", flush=True)
    if check_model_available(PRIMARY_MODEL):
        print("✅ Available!")
        return PRIMARY_MODEL
    else:
        print("❌ DEGRADED/Unavailable")

    # Try fallbacks
    for model in FALLBACK_MODELS:
        print(f"   Testing: {model}...", end=" ", flush=True)
        if check_model_available(model):
            print("✅ Available!")
            return model
        else:
            print("❌ Unavailable")

    return None


# ═══════════════════════════════════════════════
# 🔧  HELPER: Call NVIDIA API (with retry)
# ═══════════════════════════════════════════════
def call_nvidia_api(system_prompt, user_prompt, max_tokens=MAX_TOKENS, model_name=None):
    """Send request to NVIDIA API with automatic retry."""

    if model_name is None:
        model_name = ACTIVE_MODEL

    total_input = system_prompt + user_prompt
    input_chars = len(total_input)
    input_tokens_est = input_chars // 4

    print(f"   📤 Sending ~{input_tokens_est:,} input tokens, requesting {max_tokens:,} output tokens")
    print(f"   🤖 Model: {model_name}")

    # Auto-adjust if too large
    if input_tokens_est + max_tokens > MAX_CONTEXT:
        print(f"   ⚠️  May exceed context limit!")
        max_tokens = MAX_CONTEXT - input_tokens_est - 2000
        if max_tokens < 500:
            print(f"   ❌ Input too large. Skipping.")
            return None
        print(f"   📤 Adjusted max_tokens to: {max_tokens:,}")

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "text/event-stream" if STREAM else "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "stream": STREAM,
    }

    # Only add thinking for Qwen models
    if "qwen" in model_name.lower():
        payload["chat_template_kwargs"] = {"enable_thinking": True}

    # ── Retry loop ──
    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            print(f"\n   🔄 Retry {attempt}/{MAX_RETRIES} after {RETRY_DELAY}s delay...")
            time.sleep(RETRY_DELAY)

        try:
            response = requests.post(
                API_URL, headers=headers, json=payload,
                stream=STREAM, timeout=300
            )
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection error (attempt {attempt}/{MAX_RETRIES})")
            continue
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout (attempt {attempt}/{MAX_RETRIES})")
            continue
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {e}")
            continue

        # ── Check HTTP status ──
        if response.status_code != 200:
            try:
                error_body = response.json()
                error_msg = str(error_body.get("error", {}).get("detail", ""))
                if not error_msg:
                    error_msg = str(error_body.get("error", {}).get("message", ""))
            except Exception:
                error_msg = response.text[:300]

            print(f"   ❌ HTTP {response.status_code}: {error_msg[:200]}")

            # DEGRADED = model is down, retry won't help with same model
            if "DEGRADED" in error_msg.upper():
                print(f"   🚫 Model is DEGRADED (temporarily down on NVIDIA servers)")
                print(f"   This is NOT your fault. The model service is having issues.")
                return None  # Don't retry, model itself is broken

            # Rate limit = wait and retry
            if response.status_code == 429:
                print(f"   ⏳ Rate limited. Waiting {RETRY_DELAY * 2}s...")
                time.sleep(RETRY_DELAY * 2)
                continue

            # Other errors = retry
            if attempt < MAX_RETRIES:
                continue
            else:
                print(f"   ❌ All {MAX_RETRIES} attempts failed.")
                return None

        # ── SUCCESS: Process response ──
        full_response = ""

        if STREAM:
            try:
                for line in response.iter_lines():
                    if not line:
                        continue
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        decoded = decoded[6:]
                    if decoded.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(decoded)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            print(delta, end="", flush=True)
                            full_response += delta
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"\n   ⚠️ Parse error: {e}")
                print()
            except requests.exceptions.ChunkedEncodingError:
                print(f"\n   ⚠️ Stream interrupted.")
                if full_response:
                    print(f"   ℹ️ Partial: {len(full_response):,} chars")
            except Exception as e:
                print(f"\n   ⚠️ Stream error: {e}")
        else:
            try:
                full_response = response.json()["choices"][0]["message"]["content"]
                print(full_response)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"   ❌ Parse error: {e}")
                if attempt < MAX_RETRIES:
                    continue
                return None

        # ── Clean thinking tags ──
        if "<think>" in full_response:
            thinking_match = re.search(r"<think>(.*?)</think>", full_response, flags=re.DOTALL)
            if thinking_match:
                print(f"   💭 Removed thinking ({len(thinking_match.group(1)):,} chars)")
            full_response = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()

        if not full_response.strip():
            print(f"   ❌ Empty after cleaning!")
            if attempt < MAX_RETRIES:
                continue
            return None

        print(f"   ✅ Got {len(full_response):,} chars")
        return full_response

    print(f"   ❌ All {MAX_RETRIES} attempts failed.")
    return None


# ═══════════════════════════════════════════════
# ✂️  SPLIT TEXT INTO CHUNKS
# ═══════════════════════════════════════════════
def split_text_into_chunks(text, chunk_size_chars):
    """Split text into chunks at paragraph boundaries."""
    chunks = []
    while len(text) > chunk_size_chars:
        break_point = text.rfind("\n\n", 0, chunk_size_chars)
        if break_point == -1:
            break_point = text.rfind("\n", 0, chunk_size_chars)
        if break_point == -1:
            break_point = text.rfind(" ", 0, chunk_size_chars)
        if break_point == -1:
            break_point = chunk_size_chars
        chunks.append(text[:break_point].strip())
        text = text[break_point:].strip()
    if text.strip():
        chunks.append(text.strip())
    return chunks


# ═══════════════════════════════════════════════
# 🚀  MAIN LOGIC
# ═══════════════════════════════════════════════
def analyze_text(extracted_text: str) -> str:
    global ACTIVE_MODEL
    if not ACTIVE_MODEL:
        ACTIVE_MODEL = find_working_model()

    if not ACTIVE_MODEL:
        print("\n❌ No working model found!")
        return "Error: No working model found"

    total_chars = len(extracted_text)
    estimated_tokens = total_chars // 4
    chunk_size_chars = CHUNK_TOKEN_SIZE * 4

    if estimated_tokens <= SAFE_INPUT_LIMIT // 4:
        # ── SMALL FILE: Single call ──
        print(f"\n📦 Input fits in one call.")
        print(f"{'═' * 60}\n")

        user_prompt = (
            f"{FINAL_INSTRUCTION}\n\n"
            f"Here is the full Annual Report:\n\n---\n{extracted_text}\n---"
        )
        system_prompt = "You are a senior equity research analyst who explains financial reports in simple, clear language."
        full_response = call_nvidia_api(system_prompt, user_prompt)

    else:
        # ── LARGE FILE: Chunked processing ──
        chunks = split_text_into_chunks(extracted_text, chunk_size_chars)
        num_chunks = len(chunks)

        print(f"\n⚠️  Input too large for single call!")
        print(f"📦 Splitting into {num_chunks} chunks (~{CHUNK_TOKEN_SIZE:,} tokens each)")
        print(f"{'═' * 60}")

        chunk_analyses = []
        failed_chunks = []

        for i, chunk in enumerate(chunks):
            chunk_chars = len(chunk)
            chunk_tokens = chunk_chars // 4

            print(f"\n{'━' * 60}")
            print(f"📄 CHUNK {i + 1}/{num_chunks} ({chunk_chars:,} chars, ~{chunk_tokens:,} tokens)")
            print(f"{'━' * 60}\n")

            user_prompt = (
                f"{CHUNK_INSTRUCTION}\n\n"
                f"This is PART {i + 1} of {num_chunks} of the Annual Report:\n\n"
                f"---\n{chunk}\n---"
            )
            system_prompt = "You are a senior equity research analyst. Extract all key financial and business information."

            result = call_nvidia_api(system_prompt, user_prompt, max_tokens=8192)

            if result:
                chunk_analyses.append(f"### Analysis of Part {i + 1}/{num_chunks}\n\n{result}")
                print(f"\n   ✅ Chunk {i + 1}/{num_chunks} complete")
            else:
                failed_chunks.append(i + 1)
                print(f"\n   ❌ Chunk {i + 1}/{num_chunks} failed!")

            if i < num_chunks - 1:
                print(f"\n   ⏳ Waiting 5s before next chunk...")
                time.sleep(5)

        print(f"\n{'═' * 60}")
        print(f"📊 CHUNK PROCESSING SUMMARY")
        print(f"   ✅ Succeeded: {len(chunk_analyses)}/{num_chunks}")
        if failed_chunks:
            print(f"   ❌ Failed: chunks {failed_chunks}")
        print(f"{'═' * 60}")

        if not chunk_analyses:
            return "Error: All chunks failed to process."

        combined = "\n\n---\n\n".join(chunk_analyses)
        combined_tokens = len(combined) // 4

        print(f"\n🔗 Combining {len(chunk_analyses)} analyses ({combined_tokens:,} tokens)...")

        if combined_tokens > SAFE_INPUT_LIMIT // 4:
            print(f"⚠️  Combined too large for merge. Saving raw analyses.")
            full_response = combined
        else:
            print(f"{'═' * 60}\n")
            print(f"📄 FINAL MERGE")
            print(f"{'═' * 60}\n")

            user_prompt = (
                f"{FINAL_INSTRUCTION}\n\n"
                f"Here are the analyses from different sections:\n\n"
                f"---\n{combined}\n---"
            )
            system_prompt = "You are a senior equity research analyst. Combine these into one comprehensive report."
            full_response = call_nvidia_api(system_prompt, user_prompt)

            if not full_response:
                print("\n⚠️  Final merge failed. Saving individual chunk analyses instead.")
                full_response = combined

    return full_response
