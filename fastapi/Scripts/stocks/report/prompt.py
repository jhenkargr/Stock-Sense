import os
import re
import json
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────

NVIDIA_API_KEY   = os.getenv("NVIDIA_API_KEY")
COHERE_API_KEY   = os.getenv("COHERE_API_KEY")
API_URL          = "https://integrate.api.nvidia.com/v1/chat/completions"
COHERE_API_URL   = "https://api.cohere.com/v2/chat"
MAX_TOKENS       = 16384
TEMPERATURE      = 0.60
TOP_P            = 0.95
MAX_CONTEXT      = 128000
SAFE_INPUT_LIMIT = MAX_CONTEXT - MAX_TOKENS - 2000
CHUNK_SIZE_CHARS = 40000 * 4    # ~40k tokens per chunk

# ── Rate limit settings (tuned for 40 RPM) ──────────────────────────────────
# 40 RPM = 1 request every 1.5s theoretically.
# We stay conservative at 1 request per 2s to leave headroom.
# Parallel chunks: 2 workers × 1 req each, staggered by MIN_GAP_S.
# This keeps burst rate well under 40 RPM even on retries.
RPM_LIMIT        = 40
MIN_GAP_S        = 60 / RPM_LIMIT   # 1.5s minimum between any two requests
PARALLEL_CHUNKS  = 2                # safe for 40 RPM; drop to 1 if you hit limits often
CHUNK_STAGGER_S  = 3                # extra stagger between chunk launches (beyond MIN_GAP_S)
MAX_RETRIES      = 3
RETRY_DELAY      = 15               # base delay; doubles on each 429

# Models tried in order — first available one wins
MODEL_CANDIDATES = [
    "qwen/qwen3.5-122b-a10b",
    "moonshotai/kimi-k2",
    "deepseek-ai/deepseek-v3",
    "meta/llama-3.1-405b-instruct",
    "minimaxai/minimax-m2.7",
    "google/gemma-4-31b-it",
    "mistralai/mistral-small-4-119b-2603",
    "meta/llama-3.3-70b-instruct",
    "meta/llama-3.1-70b-instruct",
    "meta/llama-3.1-8b-instruct",
]

if not NVIDIA_API_KEY:
    print("❌ NVIDIA_API_KEY not found in .env!")
if not COHERE_API_KEY:
    print("⚠️  COHERE_API_KEY not found in .env — final formatting step will be skipped.")


# ─────────────────────────────────────────────
#  Global rate limiter
#  Ensures no two requests fire closer than MIN_GAP_S apart,
#  regardless of how many threads are running.
# ─────────────────────────────────────────────

_rate_lock      = threading.Lock()
_last_call_time = 0.0


def _rate_limited_post(url: str, headers: dict, payload: dict, timeout: int) -> requests.Response:
    """
    Drop-in wrapper around requests.post that enforces MIN_GAP_S between calls.
    All threads share the same lock, so parallel workers self-throttle automatically.
    """
    global _last_call_time
    with _rate_lock:
        now     = time.time()
        elapsed = now - _last_call_time
        if elapsed < MIN_GAP_S:
            time.sleep(MIN_GAP_S - elapsed)
        _last_call_time = time.time()
    # HTTP call happens outside the lock so other threads can queue up
    return requests.post(url, headers=headers, json=payload, timeout=timeout)


# ─────────────────────────────────────────────
#  Prompts
# ─────────────────────────────────────────────

CHUNK_INSTRUCTION = """
You are a senior equity research analyst. Analyze this PARTIAL section of a company's Annual Report.

Extract ALL relevant information under these exact categories:

1. COMPANY OVERVIEW
   - Business model, segment names, geographies

2. FINANCIAL PERFORMANCE
   - Revenue / Net Profit / EBITDA with amounts and YoY % change
   - Segment EBITDA margins, Net Profit Margin %, EPS
   - Gross Debt, Net Debt, Net Gearing, Debt-to-Equity
   - Cash flow from operations
   - Any red flags (exact % decline and reason)

3. CAPITAL ALLOCATION
   - CapEx total and focus areas
   - Acquisitions (name, date, reason)
   - R&D spend and headcount
   - New plants/projects (name, location, scale)
   - Investments in subsidiaries/JVs

4. FUTURE OUTLOOK & GROWTH STRATEGY
   - Numerical guidance or strategic goals
   - New products/platforms being launched
   - Expansion targets with numbers
   - Projects under development with timelines

5. RISKS & CONCERNS
   - Regulatory, competitive, macro risks
   - Legal disputes (name, amount, status)
   - Contingent liabilities total

6. DIVIDENDS & SHAREHOLDER RETURNS
   - Dividend per share, total payout, record date
   - Buybacks and bonus shares

7. MANAGEMENT & GOVERNANCE
   - Key leadership names and roles
   - Promoter holding %
   - Governance concerns and related party transactions

8. COMPETITIVE POSITION
   - Market rankings and share by segment
   - Named competitors
   - Moat factors

Be thorough. Include exact numbers. This is ONE PART — do not summarize.
"""

FINAL_INSTRUCTION = """
You are a senior equity research analyst. Write ONE comprehensive analysis of this company's Annual Report.

Use this exact format. Every sub-bullet is required.
If data is unavailable, write: "Not mentioned in this report."
Use simple language. Always include exact amounts, %, and ratios.
Remove duplicates — keep the most complete version of each fact.

─────────────────────────────────────────────────────────

## 🏢 1. Company Overview
*   **What the company does:** [Plain English — what they make/sell/operate]
*   **Key segments / divisions:**
    *   **[Segment name]:** [What it does]
*   **Markets & geographies:** [Countries, exports, international subsidiaries]

## 💰 2. Financial Performance (FY [YEAR])
*   **Revenue, Net Profit, EBITDA:**
    *   **Consolidated Revenue:** ₹[X] Crore ([+/-X%] YoY)
    *   **Consolidated EBITDA:** ₹[X] Crore ([+/-X%] YoY)
    *   **Consolidated Net Profit (PAT):** ₹[X] Crore ([+/-X%] YoY)
    *   **Net Profit Attributable to Owners:** ₹[X] Crore
*   **Profit margins:**
    *   **[Segment] Margin:** [X%] (EBITDA ₹[X] Cr)
    *   **Net Profit Margin:** [X%]
*   **Earnings Per Share (EPS):** ₹[X] (Basic & Diluted)
*   **Debt:**
    *   **Gross Debt:** ₹[X] Crore
    *   **Net Debt:** ₹[X] Crore
    *   **Net Gearing:** [X] (vs [X] prior year)
    *   **Debt-to-Equity:** [X]
*   **Cash flow from operations:** ₹[X] Crore
*   **Red flags:**
    *   [Specific concern with numbers, or "None identified"]

## 📈 3. Capital Allocation
*   **CapEx:** ₹[X] Crore in FY [YEAR]. Focus: [list]
*   **Acquisitions:**
    *   **[Deal name]:** [What, when, why]
*   **R&D:** [₹X Crore / headcount / breakdown]
*   **New plants / projects:**
    *   **[Project name]:** [Location, size, purpose]
*   **Subsidiary / JV investments:**
    *   [₹X Crore to [entity] for [purpose]]

## 🔮 4. Future Outlook & Growth Strategy
*   **Management guidance:** [Specific targets or "No numerical guidance"]
*   **New products / markets:**
    *   **[Name]:** [What it is and why it matters]
*   **Expansion plans:**
    *   **[Area]:** [Specific target]
*   **Key projects under development:**
    *   **[Project]:** [Status and timeline]
*   **Tailwinds / opportunities:**
    *   [Specific data point]

## ⚠️ 5. Risks & Concerns
*   **Key risks:**
    *   **Regulatory:** [Specific laws/rules]
    *   **Competition:** [Who and how]
    *   **Macroeconomic:** [Commodities, FX, demand — with numbers]
*   **Legal issues:**
    *   **[Case name]:** [Amount, status, response]
*   **Contingent Liabilities:** ₹[X] Crore

## 🧾 6. Dividends & Shareholder Returns
*   **Dividend:** ₹[X] per share (Face Value ₹[X]) — Total payout ₹[X] Crore — Record date: [date]
*   **Buybacks:** [Details or "None mentioned"]
*   **Bonus shares / splits:** [Ratio, impact, or "None"]

## 👔 7. Management & Governance
*   **Key leadership:**
    *   **[Role]:** [Name]
*   **Promoter holding:**
    *   **[Family/Group]:** [X%] (via [entity])
    *   **Total Promoter Holding:** [X%]
*   **Governance concerns:** [Specific issue or "None noted"]
*   **Related party transactions:**
    *   **Material RPTs:** [₹X Crore to [entity] for [purpose]]

## 🏆 8. Competitive Position
*   **Market ranking / share:**
    *   **[Segment]:** [Ranking or share]
*   **Key competitors:**
    *   **[Segment]:** [Names]
*   **Competitive advantages:**
    *   **[Advantage]:** [Specific detail]

## 📌 9. Key Takeaways
*   **Top 5 positives:**
    1.  **[Title]:** [One sentence with numbers]
    2.  **[Title]:** [One sentence with numbers]
    3.  **[Title]:** [One sentence with numbers]
    4.  **[Title]:** [One sentence with numbers]
    5.  **[Title]:** [One sentence with numbers]
*   **Top 3 concerns:**
    1.  **[Title]:** [One sentence with specifics]
    2.  **[Title]:** [One sentence with specifics]
    3.  **[Title]:** [One sentence with specifics]
*   **Overall sentiment:** **[Bullish / Cautiously Bullish / Neutral / Cautious / Bearish]**
    *   *Reason:* [2-3 sentences]

─────────────────────────────────────────────────────────
"""


# ─────────────────────────────────────────────
#  Model selection
#  Sequential probing to avoid wasting RPM budget.
# ─────────────────────────────────────────────

_model_lock       = threading.Lock()
_cached_model     = None
_model_checked_at = 0.0
MODEL_CACHE_TTL   = 300   # re-probe after 5 min


def find_working_model() -> str | None:
    """
    Try models one by one and return the first that responds.

    Why sequential instead of parallel:
      Parallel probing fires N requests at once — burning your RPM budget
      before the actual analysis even starts. With 10 candidates and 40 RPM,
      parallel probing alone could consume 25% of your per-minute budget in
      a single burst. Sequential stops as soon as one model works (usually
      1-2 probes) and spaces requests via the shared rate limiter.
    """
    print("\n🔍 Finding available NVIDIA model…")
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Accept": "application/json"}
    for model in MODEL_CANDIDATES:
        print(f"   Testing {model}…", end=" ", flush=True)
        try:
            resp = _rate_limited_post(
                API_URL,
                headers=headers,
                payload={"model": model, "messages": [{"role": "user", "content": "Hi"}],
                         "max_tokens": 5, "stream": False},
                timeout=8,
            )
            if resp.status_code == 200:
                print("✅")
                return model
            print("❌")
        except Exception:
            print("❌")
    return None


def get_active_model() -> str | None:
    """Thread-safe cached model accessor. Re-probes after MODEL_CACHE_TTL seconds."""
    global _cached_model, _model_checked_at
    now = time.time()
    if _cached_model and (now - _model_checked_at) < MODEL_CACHE_TTL:
        return _cached_model
    with _model_lock:
        now = time.time()
        if _cached_model and (now - _model_checked_at) < MODEL_CACHE_TTL:
            return _cached_model
        _cached_model     = find_working_model()
        _model_checked_at = time.time()
    return _cached_model


# ─────────────────────────────────────────────
#  NVIDIA API call
# ─────────────────────────────────────────────

def call_nvidia_api(
    system_prompt: str,
    user_prompt: str,
    model_name: str,
    max_tokens: int = MAX_TOKENS,
) -> str | None:
    input_tokens = (len(system_prompt) + len(user_prompt)) // 4
    print(f"   📤 ~{input_tokens:,} tokens in | {max_tokens:,} out | {model_name}")

    if input_tokens + max_tokens > MAX_CONTEXT:
        max_tokens = MAX_CONTEXT - input_tokens - 2000
        if max_tokens < 500:
            print("   ❌ Input too large — skipping.")
            return None
        print(f"   ⚠️  Adjusted max_tokens → {max_tokens:,}")

    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Accept": "application/json"}
    payload = {
        "model":       model_name,
        "messages":    [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_tokens":  max_tokens,
        "temperature": TEMPERATURE,
        "top_p":       TOP_P,
        "stream":      False,
    }
    if "qwen" in model_name.lower():
        payload["chat_template_kwargs"] = {"enable_thinking": True}

    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            wait = RETRY_DELAY * (2 ** (attempt - 1))   # 15s → 30s → 60s
            print(f"\n   🔄 Retry {attempt}/{MAX_RETRIES} — waiting {wait}s…")
            time.sleep(wait)

        try:
            response = _rate_limited_post(API_URL, headers=headers, payload=payload, timeout=300)
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error (attempt {attempt}): {e}")
            continue

        if response.status_code == 429:
            # Server-side rate limit — back off more aggressively than our local limiter
            wait = RETRY_DELAY * (2 ** attempt)
            print(f"   ⏳ 429 Rate limited — backing off {wait}s…")
            time.sleep(wait)
            continue

        if response.status_code != 200:
            err = response.text[:300]
            print(f"   ❌ HTTP {response.status_code}: {err[:200]}")
            if "DEGRADED" in err.upper():
                global _model_checked_at
                _model_checked_at = 0.0   # force re-probe on next call
                return None
            continue

        try:
            full_response = response.json()["choices"][0]["message"]["content"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"   ❌ Parse error: {e}")
            continue

        # Strip <think> blocks (Qwen / DeepSeek / Kimi)
        if "<think>" in full_response:
            m = re.search(r"<think>(.*?)</think>", full_response, re.DOTALL)
            if m:
                print(f"   💭 Removed thinking block ({len(m.group(1)):,} chars)")
            full_response = re.sub(r"<think>.*?</think>", "", full_response, flags=re.DOTALL).strip()

        if not full_response.strip():
            print("   ❌ Empty response.")
            continue

        print(f"   ✅ {len(full_response):,} chars received.")
        return full_response

    print(f"   ❌ All {MAX_RETRIES} attempts failed.")
    return None


# ─────────────────────────────────────────────
#  Text chunking
# ─────────────────────────────────────────────

def split_into_chunks(text: str, chunk_size: int) -> list[str]:
    """Split at paragraph boundaries to keep context coherent."""
    chunks = []
    while len(text) > chunk_size:
        bp = text.rfind("\n\n", 0, chunk_size)
        if bp == -1:
            bp = text.rfind("\n", 0, chunk_size)
        if bp == -1:
            bp = text.rfind(" ", 0, chunk_size)
        if bp == -1:
            bp = chunk_size
        chunks.append(text[:bp].strip())
        text = text[bp:].strip()
    if text.strip():
        chunks.append(text.strip())
    return chunks


# ─────────────────────────────────────────────
#  Parallel chunk worker
# ─────────────────────────────────────────────

def _analyze_chunk(args: tuple) -> tuple[int, str | None]:
    """Worker for one chunk. Returns (index, result_text | None)."""
    i, chunk, num_chunks, model = args
    print(f"\n{'━'*55}")
    print(f"📄 CHUNK {i+1}/{num_chunks}  ({len(chunk):,} chars  ~{len(chunk)//4:,} tokens)")
    print(f"{'━'*55}")
    result = call_nvidia_api(
        system_prompt="You are a senior equity research analyst. Extract all key financial and business information.",
        user_prompt=(
            f"{CHUNK_INSTRUCTION}\n\n"
            f"This is PART {i+1} of {num_chunks} of the Annual Report:\n\n---\n{chunk}\n---"
        ),
        model_name=model,
        max_tokens=8192,
    )
    return i, result


# ─────────────────────────────────────────────
#  Hierarchical merge
#  Handles cases where chunk analyses are too large
#  to fit into a single final merge call.
#
#  Strategy:
#    Round 1 — Compress each chunk analysis into a
#              dense summary (~2k tokens each).
#    Round 2 — Combine all summaries into one final
#              structured report using FINAL_INSTRUCTION.
#    Fallback — If round 2 is still too large, merge
#              in pairs until it fits.
# ─────────────────────────────────────────────

COMPRESS_INSTRUCTION = """
You are a senior equity research analyst. 
Compress the following section analysis into a DENSE SUMMARY.

Rules:
- Keep ALL numbers, percentages, ₹ amounts, and named entities.
- Remove filler words and repeated headings.
- Use bullet points only — no prose paragraphs.
- Target: under 800 words. Do NOT exceed 1000 words.
- Do NOT add any new information or conclusions.
"""


def _compress_chunk(args: tuple) -> tuple[int, str | None]:
    """Compress one chunk analysis into a dense summary."""
    i, analysis, total, model = args
    print(f"   🗜️  Compressing chunk {i+1}/{total}…")
    result = call_nvidia_api(
        system_prompt="You are a financial analyst. Compress text while keeping all numbers and facts.",
        user_prompt=f"{COMPRESS_INSTRUCTION}\n\nSection analysis:\n\n---\n{analysis}\n---",
        model_name=model,
        max_tokens=2048,
    )
    return i, result


def hierarchical_merge(chunk_analyses: list[str], model: str) -> str:
    """
    Merge chunk analyses into a final report regardless of total size.

    Flow:
      1. Try direct merge if it fits.
      2. Compress each chunk analysis in parallel, then try again.
      3. If still too large, merge in pairs until it fits.
      4. Final pass applies FINAL_INSTRUCTION formatting.
    """
    combined        = "\n\n---\n\n".join(chunk_analyses)
    combined_tokens = len(combined) // 4
    num_chunks      = len(chunk_analyses)

    print(f"\n{'═'*55}")
    print(f"📄 MERGE  ({num_chunks} chunks | ~{combined_tokens:,} tokens combined)")

    # ── Step 1: Direct merge if it fits ──────────────────────────────────────
    if combined_tokens <= SAFE_INPUT_LIMIT // 4:
        print("   ✅ Fits in one call — merging directly.")
        result = call_nvidia_api(
            system_prompt="You are a senior equity research analyst. Combine these into one comprehensive report.",
            user_prompt=f"{FINAL_INSTRUCTION}\n\n---\n{combined}\n---",
            model_name=model,
        )
        if result:
            return result
        print("   ⚠️  Direct merge failed — falling back to compression.")

    # ── Step 2: Compress each chunk analysis in parallel ─────────────────────
    print(f"\n   🗜️  Compressing {num_chunks} chunk analyses in parallel…")
    compressed: dict[int, str] = {}

    with ThreadPoolExecutor(max_workers=PARALLEL_CHUNKS) as ex:
        futures = {}
        for i, analysis in enumerate(chunk_analyses):
            if i > 0:
                time.sleep(CHUNK_STAGGER_S)
            futures[ex.submit(_compress_chunk, (i, analysis, num_chunks, model))] = i
        for future in as_completed(futures):
            i, res = future.result()
            if res:
                compressed[i] = res
            else:
                # Keep original if compression fails — better than losing data
                compressed[i] = chunk_analyses[i]
                print(f"   ⚠️  Compression failed for chunk {i+1} — keeping original.")

    compressed_list = [compressed[i] for i in sorted(compressed)]
    combined        = "\n\n---\n\n".join(compressed_list)
    combined_tokens = len(combined) // 4
    print(f"   📦 After compression: ~{combined_tokens:,} tokens")

    # ── Step 3: Try final merge on compressed data ────────────────────────────
    if combined_tokens <= SAFE_INPUT_LIMIT // 4:
        print("   ✅ Compressed data fits — merging into final report.")
        result = call_nvidia_api(
            system_prompt="You are a senior equity research analyst. Combine these into one comprehensive report.",
            user_prompt=f"{FINAL_INSTRUCTION}\n\n---\n{combined}\n---",
            model_name=model,
        )
        if result:
            return result
        print("   ⚠️  Merge failed — trying pairwise merge.")

    # ── Step 4: Pairwise merge until it fits ─────────────────────────────────
    # Merge adjacent pairs: [A,B,C,D,E] → [AB,CD,E] → [ABCDE]
    print(f"\n   🔀 Pairwise merging…")
    current = compressed_list
    round_n = 1

    while len(current) > 1:
        print(f"   Round {round_n}: {len(current)} pieces → ", end="", flush=True)
        next_round = []
        for i in range(0, len(current), 2):
            if i + 1 < len(current):
                pair     = current[i] + "\n\n---\n\n" + current[i + 1]
                pair_tok = len(pair) // 4
                if pair_tok <= SAFE_INPUT_LIMIT // 4:
                    merged = call_nvidia_api(
                        system_prompt="You are a financial analyst. Merge these two section summaries into one, keeping all numbers.",
                        user_prompt=f"Merge these two summaries into one dense summary. Keep ALL numbers and facts:\n\n---\n{pair}\n---",
                        model_name=model,
                        max_tokens=4096,
                    )
                    next_round.append(merged if merged else pair)
                else:
                    # Pair itself too large — keep separately
                    next_round.extend([current[i], current[i + 1]])
            else:
                next_round.append(current[i])
        current = next_round
        round_n += 1
        print(f"{len(current)} pieces")

        # Check if we can now do the final merge
        combined = "\n\n---\n\n".join(current)
        if len(combined) // 4 <= SAFE_INPUT_LIMIT // 4:
            break

    # ── Final formatting pass ─────────────────────────────────────────────────
    combined = "\n\n---\n\n".join(current)
    print(f"\n   📄 Final formatting pass (~{len(combined)//4:,} tokens)…")
    result = call_nvidia_api(
        system_prompt="You are a senior equity research analyst. Format this into a comprehensive structured report.",
        user_prompt=f"{FINAL_INSTRUCTION}\n\n---\n{combined}\n---",
        model_name=model,
    )

    if result:
        return result

    # Absolute fallback — return whatever we have
    print("   ⚠️  Final formatting failed — returning merged summaries as-is.")
    return combined


# ─────────────────────────────────────────────
#  Supabase helper
# ─────────────────────────────────────────────

def get_supabase():
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
        return client
    except Exception as e:
        print(f"Supabase unavailable: {e}")
        return None


# ─────────────────────────────────────────────
#  Cohere formatter
#  Takes the raw NVIDIA output (which may be messy
#  chunk analyses or a partial report) and returns
#  a clean, structured markdown report in the exact
#  format shown in FINAL_INSTRUCTION.
# ─────────────────────────────────────────────

COHERE_FORMAT_PROMPT = """
You are a senior equity research analyst. 
You will receive raw analysis data extracted from a company's Annual Report.
Your job is to reformat and clean it into one polished, structured report.

STRICT RULES:
- Follow the exact section structure and emoji headers below.
- Every sub-bullet listed in the format must appear. Write "Not mentioned in this report." if data is missing.
- Deduplicate: if the same fact appears multiple times, keep the most complete version.
- Keep ALL ₹ amounts, percentages, ratios, and named entities exactly as given.
- Use simple, clear language. No filler. No repetition.
- Output ONLY the formatted report — no preamble, no explanation.

OUTPUT FORMAT:
---

## 🏢 1. Company Overview
*   **What the company does:** [Plain English]
*   **Key segments / divisions:**
    *   **[Segment name]:** [What it does]
*   **Markets & geographies:** [Countries, exports, international subsidiaries]

## 💰 2. Financial Performance (FY [YEAR])
*   **Revenue, Net Profit, EBITDA:**
    *   **Consolidated Revenue:** ₹[X] Crore ([+/-X%] YoY)
    *   **Consolidated EBITDA:** ₹[X] Crore ([+/-X%] YoY)
    *   **Consolidated Net Profit (PAT):** ₹[X] Crore ([+/-X%] YoY)
    *   **Net Profit Attributable to Owners:** ₹[X] Crore
*   **Profit margins:**
    *   **[Segment] Margin:** [X%] (EBITDA ₹[X] Cr)
    *   **Net Profit Margin:** [X%]
*   **Earnings Per Share (EPS):** ₹[X] (Basic & Diluted)
*   **Debt:**
    *   **Gross Debt:** ₹[X] Crore
    *   **Net Debt:** ₹[X] Crore
    *   **Net Gearing:** [X] (vs [X] prior year)
    *   **Debt-to-Equity:** [X]
*   **Cash flow from operations:** ₹[X] Crore
*   **Red flags:**
    *   [Specific concern with numbers, or "None identified"]

## 📈 3. Capital Allocation
*   **CapEx:** ₹[X] Crore in FY [YEAR]. Focus: [list]
*   **Acquisitions:**
    *   **[Deal name]:** [What, when, why]
*   **R&D:** [₹X Crore / headcount / breakdown]
*   **New plants / projects:**
    *   **[Project name]:** [Location, size, purpose]
*   **Subsidiary / JV investments:**
    *   [₹X Crore to [entity] for [purpose]]

## 🔮 4. Future Outlook & Growth Strategy
*   **Management guidance:** [Specific targets or "No numerical guidance"]
*   **New products / markets:**
    *   **[Name]:** [What it is and why it matters]
*   **Expansion plans:**
    *   **[Area]:** [Specific target]
*   **Key projects under development:**
    *   **[Project]:** [Status and timeline]
*   **Tailwinds / opportunities:**
    *   [Specific data point]

## ⚠️ 5. Risks & Concerns
*   **Key risks:**
    *   **Regulatory:** [Specific laws/rules]
    *   **Competition:** [Who and how]
    *   **Macroeconomic:** [Commodities, FX, demand — with numbers]
*   **Legal issues:**
    *   **[Case name]:** [Amount, status, response]
*   **Contingent Liabilities:** ₹[X] Crore

## 🧾 6. Dividends & Shareholder Returns
*   **Dividend:** ₹[X] per share (Face Value ₹[X]) — Total payout ₹[X] Crore — Record date: [date]
*   **Buybacks:** [Details or "None mentioned"]
*   **Bonus shares / splits:** [Ratio, impact, or "None"]

## 👔 7. Management & Governance
*   **Key leadership:**
    *   **[Role]:** [Name]
*   **Promoter holding:**
    *   **[Family/Group]:** [X%] (via [entity])
    *   **Total Promoter Holding:** [X%]
*   **Governance concerns:** [Specific issue or "None noted"]
*   **Related party transactions:**
    *   **Material RPTs:** [₹X Crore to [entity] for [purpose]]

## 🏆 8. Competitive Position
*   **Market ranking / share:**
    *   **[Segment]:** [Ranking or share]
*   **Key competitors:**
    *   **[Segment]:** [Names]
*   **Competitive advantages:**
    *   **[Advantage]:** [Specific detail]

## 📌 9. Key Takeaways
*   **Top 5 positives:**
    1.  **[Title]:** [One sentence with numbers]
    2.  **[Title]:** [One sentence with numbers]
    3.  **[Title]:** [One sentence with numbers]
    4.  **[Title]:** [One sentence with numbers]
    5.  **[Title]:** [One sentence with numbers]
*   **Top 3 concerns:**
    1.  **[Title]:** [One sentence with specifics]
    2.  **[Title]:** [One sentence with specifics]
    3.  **[Title]:** [One sentence with specifics]
*   **Overall sentiment:** **[Bullish / Cautiously Bullish / Neutral / Cautious / Bearish]**
    *   *Reason:* [2-3 sentences]

---
"""


def format_with_cohere(raw_analysis: str, symbol: str | None = None) -> str:
    """
    Send the raw NVIDIA analysis to Cohere and get back a clean,
    structured markdown report in the exact RELIANCE-style format.

    Falls back to the raw analysis if Cohere is unavailable.
    """
    if not COHERE_API_KEY:
        print("⚠️  Cohere key missing — skipping formatting step.")
        return raw_analysis

    company_hint = f" for {symbol.upper()}" if symbol else ""
    print(f"\n{'═'*55}")
    print(f"✨ COHERE FORMATTING PASS{company_hint}")
    print(f"{'═'*55}")
    print(f"   📤 Sending ~{len(raw_analysis)//4:,} tokens to Cohere…")

    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }
    payload = {
        "model": "command-a-03-2025",   # Cohere's best instruction-following model
        "messages": [
            {
                "role":    "system",
                "content": COHERE_FORMAT_PROMPT,
            },
            {
                "role":    "user",
                "content": (
                    f"Here is the raw annual report analysis{company_hint}. "
                    f"Reformat it into the exact structured report format:\n\n"
                    f"---\n{raw_analysis}\n---"
                ),
            },
        ],
        "max_tokens":  4096,
        "temperature": 0.3,   # Low temp — we want consistent formatting, not creativity
    }

    for attempt in range(1, 4):
        try:
            resp = requests.post(COHERE_API_URL, headers=headers, json=payload, timeout=120)
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Cohere request error (attempt {attempt}): {e}")
            if attempt < 3:
                time.sleep(10)
            continue

        if resp.status_code == 429:
            wait = 20 * attempt
            print(f"   ⏳ Cohere rate limited — waiting {wait}s…")
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            print(f"   ❌ Cohere HTTP {resp.status_code}: {resp.text[:200]}")
            if attempt < 3:
                time.sleep(10)
            continue

        try:
            data    = resp.json()
            content = None

            # Shape 1: v2 chat -> {"message": {"content": [{"type": "text", "text": "..."}]}}
            if "message" in data:
                for part in data["message"].get("content", []):
                    if isinstance(part, dict) and part.get("type") == "text":
                        content = part.get("text", "").strip()
                        break

            # Shape 2: v1 chat -> {"text": "..."}
            if not content:
                content = (data.get("text") or "").strip()

            # Shape 3: generate -> {"generations": [{"text": "..."}]}
            if not content and data.get("generations"):
                content = (data["generations"][0].get("text") or "").strip()

            # Shape 4: openai-compat -> {"choices": [{"message": {"content": "..."}}]}
            if not content and data.get("choices"):
                content = (data["choices"][0]["message"].get("content") or "").strip()

            if content:
                print(f"   ✅ Cohere returned {len(content):,} chars.")
                return content

            print(f"   ❌ Cohere empty. Raw: {str(data)[:400]}")

        except (KeyError, IndexError, ValueError) as e:
            print(f"   ❌ Cohere parse error: {e} | Raw: {resp.text[:400]}")
        if attempt < 3:
            time.sleep(10)

    print("   ⚠️  Cohere formatting failed — returning raw NVIDIA analysis.")
    return raw_analysis


# ─────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────

def analyze_text(extracted_text: str, symbol: str | None = None) -> str:
    t0       = time.time()
    supabase = get_supabase()

    # 1. Supabase cache — return Cohere report if already done
    if symbol and supabase:
        try:
            files = supabase.storage.from_("simplifier").list(f"documents/{symbol.upper()}")
            names = [f["name"] for f in files] if isinstance(files, list) else []

            cohere_file = f"{symbol.upper()}_cohere_analysis.md"
            nvidia_file = f"{symbol.upper()}_analysis.md"

            if cohere_file in names:
                print(f"✅ Returning cached Cohere report from Supabase.")
                return supabase.storage.from_("simplifier").download(
                    f"documents/{symbol.upper()}/{cohere_file}"
                ).decode("utf-8")

            if nvidia_file in names:
                # NVIDIA result exists but Cohere formatting was never saved —
                # re-run just the Cohere step instead of the full pipeline.
                print(f"⚠️  Found NVIDIA raw — re-running Cohere formatting step only.")
                nvidia_raw = supabase.storage.from_("simplifier").download(
                    f"documents/{symbol.upper()}/{nvidia_file}"
                ).decode("utf-8")
                cohere_result = format_with_cohere(nvidia_raw, symbol=symbol)
                supabase.storage.from_("simplifier").upload(
                    f"documents/{symbol.upper()}/{cohere_file}",
                    cohere_result.encode("utf-8"),
                    {"upsert": "true", "content-type": "text/markdown"},
                )
                print(f"✅ Uploaded Cohere formatted report.")
                return cohere_result

        except Exception as e:
            print(f"Supabase cache check failed: {e}")

    # 2. Model selection (sequential probe, cached for 5 min)
    model = get_active_model()
    if not model:
        return "Error: No working NVIDIA model found. Check your API key and try again."

    estimated_tokens = len(extracted_text) // 4
    result: str | None = None

    # 3a. Small file — single API call
    if estimated_tokens <= SAFE_INPUT_LIMIT // 4:
        print(f"\n📦 Single call (~{estimated_tokens:,} tokens).")
        result = call_nvidia_api(
            system_prompt="You are a senior equity research analyst who explains financial reports in simple, clear language.",
            user_prompt=f"{FINAL_INSTRUCTION}\n\nHere is the full Annual Report:\n\n---\n{extracted_text}\n---",
            model_name=model,
        )

    # 3b. Large file — parallel chunks, rate-limited
    else:
        chunks     = split_into_chunks(extracted_text, CHUNK_SIZE_CHARS)
        num_chunks = len(chunks)
        print(f"\n⚠️  Large input ({estimated_tokens:,} tokens) → {num_chunks} chunks, {PARALLEL_CHUNKS} workers")
        print(f"   Rate budget: {RPM_LIMIT} RPM | gap: {MIN_GAP_S:.1f}s | stagger: {CHUNK_STAGGER_S}s")

        chunk_results: dict[int, str] = {}
        failed: list[int] = []

        with ThreadPoolExecutor(max_workers=PARALLEL_CHUNKS) as ex:
            futures = {}
            for i, chunk in enumerate(chunks):
                if i > 0:
                    time.sleep(CHUNK_STAGGER_S)   # spread launches to avoid burst
                futures[ex.submit(_analyze_chunk, (i, chunk, num_chunks, model))] = i
            for future in as_completed(futures):
                i, res = future.result()
                if res:
                    chunk_results[i] = f"### Part {i+1}/{num_chunks}\n\n{res}"
                    print(f"   ✅ Chunk {i+1} done")
                else:
                    failed.append(i + 1)
                    print(f"   ❌ Chunk {i+1} failed")

        chunk_analyses = [chunk_results[i] for i in sorted(chunk_results)]
        print(f"\n{'═'*55}")
        print(f"📊 {len(chunk_analyses)}/{num_chunks} chunks OK" + (f"  |  ❌ Failed: {failed}" if failed else ""))

        if not chunk_analyses:
            return "Error: All chunks failed to process."

        result = hierarchical_merge(chunk_analyses, model)

    if not result:
        return "Error: Analysis failed."

    nvidia_result = result
    print(f"\n⏱️  NVIDIA done: {time.time() - t0:.1f}s")

    # 4. Format with Cohere into the clean structured report
    cohere_result = format_with_cohere(nvidia_result, symbol=symbol)

    print(f"\n⏱️  Total time: {time.time() - t0:.1f}s")

    # 5. Upload both responses to Supabase separately
    if symbol and supabase:
        uploads = [
            (
                f"documents/{symbol.upper()}/{symbol.upper()}_analysis.md",
                nvidia_result,
                "NVIDIA raw analysis",
            ),
            (
                f"documents/{symbol.upper()}/{symbol.upper()}_cohere_analysis.md",
                cohere_result,
                "Cohere formatted report",
            ),
        ]
        for path, text, label in uploads:
            try:
                supabase.storage.from_("simplifier").upload(
                    path,
                    text.encode("utf-8"),
                    {"upsert": "true", "content-type": "text/markdown"},
                )
                print(f"✅ Uploaded {label} → {path}")
            except Exception as e:
                print(f"Supabase upload failed ({label}): {e}")

    return cohere_result