# SourceMind ⚡
> **Adaptive Material Procurement Agent for Small Manufacturers & Traders**  
> Powered by **Hindsight Cloud Memory** and **Groq LLM** (`openai/gpt-oss-120b`).

---

## 🎯 What is SourceMind?
Small manufacturers and traders constantly struggle with vendor selection:
- A vendor might quote the lowest price, but consistently delay deliveries by weeks.
- Another vendor might be reachable strictly on WhatsApp.
- Certain vendors excel at small batches but fail on large bulk orders.
- Some vendors drop prices by 8–10% when competitor quotes are mentioned.

**SourceMind** acts as an AI procurement copilot that **remembers every vendor interaction, quality issue, delivery delay, and price negotiation over time**. By using **Hindsight Cloud**, memory is central, persistent, and directly visible in every decision.

---

## 🧠 Two Hindsight Memory Banks (Judges' Guide)

1. **`bank_id: "buyer1"` (Private History)**:
   - Tracks the buyer's private interaction history, outcomes, quality resolutions, delays, and custom rules.
   - Initialized with **42 chronological order events across 12 vendors**.
   - Mission: *"Procurement assistant. Track vendor reliability, price behavior, delivery delays, quality issues, and the buyer's priorities."*
2. **`bank_id: "marketplace"` (Shared Peer Reviews)**:
   - Aggregates reviews from other verified buyers and manufacturers in different cities.
   - Initialized with **15 synthetic reviews covering 6 new vendors** never used by `buyer1` (Kaveri Metals & Tubes, Sterling Castings Ltd, Nordic Fasteners Corp, EcoBox Logistics Packaging, Solventex Industrial Solutions, Global Polymer Dynamics).
   - Mission: *"Procurement marketplace. Aggregate buyer reviews, vendor reliability, delivery speeds, pricing, and material quality across different cities and manufacturers."*

---

## ⚡ Core Features & Endpoints

1. **Context-Aware Recall (`client.recall`)**:
   - `POST /request`: When **Memory ON**, SourceMind recalls private memories from `buyer1` and feeds them into Groq (`openai/gpt-oss-120b`). Output cards show ranked vendors, reasons, and tailored messages, plus a **Memories Used** inspector.
   - When **Memory OFF**, runs baseline mode without memory grounding for judge comparison.
2. **Marketplace Discovery (`POST /discover`)**:
   - Recalls shared reviews from the `marketplace` bank for relevant materials while strictly excluding any vendor the buyer has already used.
   - Returns up to 3 new vendors worth trying with peer review evidence quotes.
   - Clicking *"⚡ Log Outcome → Add to My History"* allows the buyer to record a new transaction for that vendor into `buyer1`, seamlessly adopting them into their own private memory!
3. **Synthesis & Reflection (`client.reflect`)**:
   - `GET /insights`: Synthesizes high-level mental models of vendor patterns and buyer priorities via `client.reflect()`.
4. **Continuous Learning (`client.retain`)**:
   - `POST /outcome`: Logs completed transactions into `buyer1` memory.
   - `POST /feedback`: Saves persistent buyer rules into `buyer1` memory.

---

## 🛠️ Architecture & Tech Stack

- **Memory**: [Hindsight Cloud](https://hindsight.vectorize.io) (`hindsight-client`, Bank ID: `buyer1`)
- **LLM**: Groq API (`openai/gpt-oss-120b`, fallback `qwen/qwen3.8-27b`) with strict JSON enforcement and defensive parsing
- **Backend**: Python, Flask, `flask-cors`, `python-dotenv` (in `/backend`)
- **Frontend**: React + Vite single-page application with modern dark theme (in `/frontend`)
- **Data**: Chronological 6-month seed data (42 events across 12 vendors) in `/data/load_data.py`

---

## 🚀 Quickstart & Running Locally

### 1. Environment Setup
Make sure your `.env` file exists in the project root:
```env
GROQ_API_KEY=your_groq_api_key
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
```

### 2. Start the Backend Server (Terminal 1)
```powershell
.\.venv\Scripts\python -m backend.app
```
*Backend will run at `http://127.0.0.1:5000`.*

### 3. Start the Frontend Application (Terminal 2)
```powershell
cd frontend
npm run dev
```
*Open `http://127.0.0.1:5173` in your browser.*

---

## 🧪 Testing & Verification Scripts

- **Test Hindsight Connection**:
  ```powershell
  .\.venv\Scripts\python test_hindsight.py
  ```
- **Re-Seed Chronological Memory**:
  ```powershell
  .\.venv\Scripts\python data/load_data.py
  ```
- **Test Planted Pattern Recalls**:
  ```powershell
  .\.venv\Scripts\python data/test_recall.py
  ```
- **Test All 5 Backend Endpoints**:
  ```powershell
  .\.venv\Scripts\python -m backend.test_backend
  ```

---

## 💡 Planted Demo Scenarios to Try in UI

1. **Tight Deadline Steel Tubing** (Tests Pattern A):
   - *Prompt*: *"I need 2,000 meters of structural steel tubing on a tight budget, but I cannot tolerate delivery delays for line 2."*
   - *Result*: With Memory ON, SourceMind alerts that **Apex Industrial Supplies** is the cheapest but has a severe track record of 10–15 day delays, and ranks reliable vendors first with a warning.
2. **Bulk Fasteners Order** (Tests Pattern E):
   - *Prompt*: *"I need 25,000 units of M6 zinc-plated flange nuts urgently for full-scale production."*
   - *Result*: Warns that **Titan Fasteners** is great for small batches (<2,000 units in 3 days) but failed repeatedly on bulk orders (>20,000 units delayed 3–4 weeks).
3. **Aluminum Valve Bodies** (Tests Pattern C):
   - *Prompt*: *"Looking for 300 custom aluminum valve bodies. Hydrostatic pressure pass rate and zero porosity is critical."*
   - *Result*: Notes that **Zenith Castings** had a porous batch in May, but successfully audited their foundry temperature and has delivered zero-defect batches since.
4. **Memory ON vs. Memory OFF Comparison**:
   - Toggle the switch to **OFF** and run the same query: notice how standard LLMs without memory recommend the cheapest vendor blindly without knowing they will halt your production line!
