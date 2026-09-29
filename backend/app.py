import os
import re
import json
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SourceMind")

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
BANK_ID = "buyer1"
BANK_MISSION = "Procurement assistant. Track vendor reliability, price behavior, delivery delays, quality issues, and the buyer's priorities."

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Clients
groq_client = None

def get_hindsight_client():
    if not HINDSIGHT_API_KEY:
        raise ValueError("HINDSIGHT_API_KEY is not set in environment.")
    return Hindsight(base_url=HINDSIGHT_BASE_URL, api_key=HINDSIGHT_API_KEY)

def get_groq_client():
    global groq_client
    if groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")
        groq_client = Groq(api_key=GROQ_API_KEY)
    return groq_client

def init_bank_mission():
    try:
        client = get_hindsight_client()
        try:
            try:
                client.create_bank(bank_id=BANK_ID, name=BANK_ID)
            except Exception:
                pass
            client.set_mission(bank_id=BANK_ID, mission=BANK_MISSION)
            logger.info(f"Bank mission confirmed for '{BANK_ID}'")
        finally:
            client.close()
    except Exception as e:
        logger.warning(f"Could not initialize bank mission on startup: {e}")

# Defensive JSON extractor
def extract_json(raw_text: str) -> dict:
    if not raw_text:
        raise ValueError("Empty response received from LLM")
    
    cleaned = raw_text.strip()
    # Strip markdown code blocks ```json ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to find the first '{' and last '}'
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            substring = cleaned[start:end+1]
            return json.loads(substring)
        raise

# LLM call with retry and fallback
def call_llm_with_fallback(system_prompt: str, user_prompt: str) -> dict:
    client = get_groq_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    primary_model = "openai/gpt-oss-120b"
    fallback_models = ["qwen/qwen3-32b", "qwen/qwen3.8-27b"]

    # 1. Try primary model (up to 2 attempts: 1 try + 1 retry)
    for attempt in range(1, 3):
        try:
            logger.info(f"Calling primary model '{primary_model}' (attempt {attempt}/2)...")
            res = client.chat.completions.create(
                model=primary_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_completion_tokens=2048
            )
            raw = res.choices[0].message.content
            parsed = extract_json(raw)
            return {"data": parsed, "model_used": primary_model}
        except Exception as e:
            logger.warning(f"Primary model '{primary_model}' attempt {attempt} failed: {e}")

    # 2. Try fallback models
    for fb_model in fallback_models:
        try:
            logger.info(f"Trying fallback model '{fb_model}'...")
            res = client.chat.completions.create(
                model=fb_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                max_completion_tokens=2048
            )
            raw = res.choices[0].message.content
            parsed = extract_json(raw)
            return {"data": parsed, "model_used": fb_model}
        except Exception as e:
            logger.warning(f"Fallback model '{fb_model}' failed: {e}")

    raise RuntimeError("All LLM attempts (primary with retry and fallbacks) failed to return valid JSON.")

# Health check
@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "SourceMind Backend",
        "bank_id": BANK_ID,
        "hindsight_base_url": HINDSIGHT_BASE_URL
    })


# 1. POST /request  {request_text, memory_on}
@app.route("/request", methods=["POST"])
@app.route("/api/request", methods=["POST"])
def procurement_request():
    data = request.get_json(force=True, silent=True) or {}
    request_text = data.get("request_text", "").strip()
    memory_on = bool(data.get("memory_on", False))

    if not request_text:
        return jsonify({"error": "request_text is required."}), 400

    memories_used = []

    # Recall from Hindsight if memory_on is enabled
    if memory_on:
        client = get_hindsight_client()
        try:
            recall_resp = client.recall(bank_id=BANK_ID, query=request_text)
            results = getattr(recall_resp, "results", []) or []
            for r in results:
                text = getattr(r, "text", "")
                if text:
                    memories_used.append(text)
            logger.info(f"Memory ON: Recalled {len(memories_used)} items for query: '{request_text}'")
        except Exception as e:
            logger.error(f"Failed to recall memories from Hindsight: {e}")
            memories_used = [f"[Error recalling memories: {e}]"]
        finally:
            client.close()

    # Construct Prompt
    system_prompt = (
        "You are SourceMind, an expert procurement intelligence agent assisting small manufacturers and traders.\n"
        "Your goal is to recommend and rank material vendors tailored to the buyer's request.\n"
        "Output strict JSON only, with no surrounding markdown or explanation."
    )

    if memory_on and memories_used:
        memory_section = "PAST VENDOR INTERACTION MEMORIES & AUDIT HISTORY:\n" + "\n".join(f"- {m}" for m in memories_used[:30])
        memory_instruction = (
            "CRITICAL: Base your recommendations directly on the past memories above! Specifically consider:\n"
            "- Delivery reliability and past delay track records (e.g. if a vendor is cheap but consistently late).\n"
            "- Preferred communication channels (e.g. WhatsApp vs email for specific contacts).\n"
            "- Resolved quality issues (e.g. past defect followed by confirmed resolution and zero defect track record).\n"
            "- Price negotiation patterns (e.g. vendors willing to drop prices when competing quotes are cited).\n"
            "- Order size constraints (vendors suitable for small batches vs large bulk volumes)."
        )
    else:
        memory_section = "MEMORY STATUS: Memory is OFF. No past interaction records are available. Use standard procurement general knowledge only."
        memory_instruction = "Evaluate based purely on general industry heuristics as a baseline."

    user_prompt = f"""BUYER'S PROCUREMENT REQUEST:
"{request_text}"

{memory_section}

{memory_instruction}

RETURN STRICT JSON WITH THIS SCHEMA:
{{
  "vendors": [
    {{
      "rank": 1,
      "name": "Vendor Name",
      "reason": "Clear explanation of why this vendor is ranked here based on past performance and suitability.",
      "drafted_message": "A realistic, ready-to-send outreach message tailored to this specific vendor (e.g. mentioning WhatsApp, competitor quotes, or batch size constraints).",
      "price_assessment": "Short price assessment (e.g. Lowest Price, Negotiable, Standard Market, Premium)",
      "risk_assessment": "Short risk notes (e.g. High delivery risk, Low risk, Capacity warning for bulk)"
    }}
  ],
  "analysis": "A concise executive summary comparing the options and advising the buyer on the best next step."
}}"""

    try:
        llm_result = call_llm_with_fallback(system_prompt, user_prompt)
        parsed_data = llm_result["data"]
        model_used = llm_result["model_used"]

        return jsonify({
            "success": True,
            "memory_on": memory_on,
            "memories_used": memories_used,
            "model_used": model_used,
            "vendors": parsed_data.get("vendors", []),
            "analysis": parsed_data.get("analysis", "")
        })
    except Exception as e:
        logger.error(f"Error processing procurement request: {e}")
        return jsonify({"error": str(e)}), 500

# 2. POST /outcome  {vendor, material, price, delay_days, quality, verdict, region}
@app.route("/outcome", methods=["POST"])
@app.route("/api/outcome", methods=["POST"])
def record_outcome():
    data = request.get_json(force=True, silent=True) or {}
    vendor = data.get("vendor", "").strip()
    material = data.get("material", "").strip()
    price = str(data.get("price", "")).strip()
    delay_days = data.get("delay_days", 0)
    quality = data.get("quality", "").strip()
    verdict = data.get("verdict", "").strip()
    region = data.get("region", "").strip()

    if not vendor or not material:
        return jsonify({"error": "vendor and material are required fields."}), 400

    now_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    region_str = f" in {region}" if region else ""
    delay_str = f"{delay_days} days late" if delay_days and int(delay_days) > 0 else "on time"
    price_str = f" at {price}" if price else ""
    quality_str = f" with {quality} quality" if quality else ""
    verdict_str = f" Buyer verdict: {verdict}." if verdict else ""

    plain_sentence = (
        f"On {now_str}, completed an order of {material} from {vendor}{region_str}{price_str}. "
        f"The shipment arrived {delay_str}{quality_str}.{verdict_str}"
    )

    client = get_hindsight_client()
    try:
        client.retain(bank_id=BANK_ID, content=plain_sentence)
        logger.info(f"Retained new outcome memory: {plain_sentence}")
        return jsonify({
            "success": True,
            "message": "Outcome recorded to Hindsight memory.",
            "retained_sentence": plain_sentence
        })
    except Exception as e:
        logger.error(f"Error retaining outcome to Hindsight: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# 3. POST /feedback  {text}
@app.route("/feedback", methods=["POST"])
@app.route("/api/feedback", methods=["POST"])
def record_feedback():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Feedback 'text' is required."}), 400

    sentence = f"Buyer priority and operational feedback: {text}"

    client = get_hindsight_client()
    try:
        client.retain(bank_id=BANK_ID, content=sentence)
        logger.info(f"Retained buyer feedback: {sentence}")
        return jsonify({
            "success": True,
            "message": "Buyer feedback stored to Hindsight memory.",
            "retained_feedback": sentence
        })
    except Exception as e:
        logger.error(f"Error retaining feedback to Hindsight: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# 4. GET /insights
@app.route("/insights", methods=["GET"])
@app.route("/api/insights", methods=["GET"])
def get_insights():
    query = "What patterns do you see in vendor performance and in this buyer's priorities?"
    client = get_hindsight_client()
    try:
        logger.info(f"Calling client.reflect() for insights query: '{query}'...")
        reflect_resp = client.reflect(bank_id=BANK_ID, query=query)
        insights_text = getattr(reflect_resp, "text", "") or ""
        return jsonify({
            "success": True,
            "query": query,
            "insights": insights_text
        })
    except Exception as e:
        logger.error(f"Error reflecting insights from Hindsight: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

MARKETPLACE_BANK_ID = "marketplace"
KNOWN_BUYER1_VENDORS = [
    "Apex Industrial Supplies",
    "Apex Steel",
    "Bharat Polymers",
    "Coastal Timber & Pallets",
    "Delta Packaging",
    "Metro Steel & Wire",
    "Orion Precision Alloys",
    "Pioneer Plastics",
    "Summit Chemicals",
    "Swift Electricals",
    "Titan Fasteners",
    "Vanguard Tooling",
    "Zenith Castings"
]

# 5. POST /discover  {request_text} (Marketplace layer)
@app.route("/discover", methods=["POST"])
@app.route("/api/discover", methods=["POST"])
def discover_marketplace_vendors():
    data = request.get_json(force=True, silent=True) or {}
    request_text = data.get("request_text", "").strip()

    if not request_text:
        return jsonify({"error": "request_text is required for marketplace discovery."}), 400

    marketplace_memories = []
    client = get_hindsight_client()
    try:
        recall_resp = client.recall(bank_id=MARKETPLACE_BANK_ID, query=request_text)
        results = getattr(recall_resp, "results", []) or []
        for r in results:
            text = getattr(r, "text", "")
            if text:
                marketplace_memories.append(text)
        logger.info(f"Marketplace recall found {len(marketplace_memories)} reviews for '{request_text}'")
    except Exception as e:
        logger.error(f"Error querying marketplace bank in Hindsight: {e}")
        return jsonify({"error": f"Failed to query marketplace memory: {e}"}), 500
    finally:
        client.close()

    system_prompt = (
        "You are SourceMind Marketplace Discovery Agent.\n"
        "Your task is to recommend up to 3 NEW, high-quality vendors from shared marketplace reviews that match the buyer's material request.\n"
        "CRITICAL CONSTRAINT: Do NOT suggest any vendors that are already in the buyer's private history.\n"
        "Base your recommendations entirely on the real reviews from other buyers and cite their reviews as evidence.\n"
        "Output strict JSON only with no surrounding text."
    )

    reviews_text = "\n".join(f"- {m}" for m in marketplace_memories) if marketplace_memories else "No specific marketplace reviews matched."
    excluded_vendors_text = ", ".join(KNOWN_BUYER1_VENDORS)

    user_prompt = f"""BUYER PROCUREMENT REQUEST:
"{request_text}"

BUYER'S EXISTING VENDORS (DO NOT RECOMMEND ANY OF THESE):
{excluded_vendors_text}

SHARED MARKETPLACE REVIEWS FROM OTHER BUYERS:
{reviews_text}

INSTRUCTIONS:
1. Select up to 3 NEW vendors from the marketplace reviews that provide relevant materials.
2. For each new vendor:
   - name: Vendor name
   - location: City or region noted in the reviews
   - reason_worth_trying: Why this vendor is a strong candidate based on other buyers' feedback.
   - evidence: 1 or 2 specific quotes or review summaries from other buyers.
   - key_strengths: Delivery speed, volume capacity, pricing, or quality advantages.
   - potential_cautions: Any limitations (e.g. high MOQ, strict payment terms, slightly higher price).
3. Provide a brief marketplace summary explaining how these alternative vendors compare to the buyer's usual options.

RETURN STRICT JSON WITH THIS SCHEMA:
{{
  "suggestions": [
    {{
      "name": "Vendor Name",
      "location": "City / Region",
      "reason_worth_trying": "Why to try this vendor...",
      "evidence": [
        "Quote or finding from other buyer review..."
      ],
      "key_strengths": "Strengths noted...",
      "potential_cautions": "Cautions noted..."
    }}
  ],
  "marketplace_analysis": "Executive marketplace overview..."
}}"""

    try:
        llm_result = call_llm_with_fallback(system_prompt, user_prompt)
        parsed_data = llm_result["data"]
        model_used = llm_result["model_used"]

        return jsonify({
            "success": True,
            "request_text": request_text,
            "marketplace_memories_used": marketplace_memories,
            "model_used": model_used,
            "suggestions": parsed_data.get("suggestions", []),
            "marketplace_analysis": parsed_data.get("marketplace_analysis", "")
        })
    except Exception as e:
        logger.error(f"Error in marketplace discovery: {e}")
        return jsonify({"error": str(e)}), 500

# 6. Static SPA frontend serving
dist_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    # Never hijack /api routes
    if path.startswith("api/") or path == "api":
        return jsonify({"error": f"API endpoint '/{path}' not found."}), 404

    if os.path.exists(dist_folder):
        file_path = os.path.join(dist_folder, path)
        if path and os.path.exists(file_path) and not os.path.isdir(file_path):
            return send_from_directory(dist_folder, path)
        index_file = os.path.join(dist_folder, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(dist_folder, "index.html")

    return jsonify({
        "status": "ok",
        "service": "SourceMind Full-Stack",
        "message": "Frontend static assets not found. Run 'npm run build'."
    })

# Initialize mission on module load
init_bank_mission()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting SourceMind Backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
