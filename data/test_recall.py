import os
import sys
from dotenv import load_dotenv
from hindsight_client import Hindsight

BANK_ID = "buyer1"

TEST_QUERIES = [
    {
        "pattern": "Pattern A: Cheapest but consistently late",
        "query": "Which vendor is cheapest but unreliable on delivery?"
    },
    {
        "pattern": "Pattern B: WhatsApp communication only",
        "query": "How should I contact Bharat Polymers or who is the contact person?"
    },
    {
        "pattern": "Pattern C: Quality defect resolved later",
        "query": "Which vendor had a quality issue and was it resolved?"
    },
    {
        "pattern": "Pattern D: Price drop when competitor quote mentioned",
        "query": "Which vendor lowered its price and why?"
    },
    {
        "pattern": "Pattern E: Small orders vs large bulk orders",
        "query": "Which vendors should I use for large orders vs small ones?"
    }
]

def main():
    load_dotenv()
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

    if not api_key:
        print("[-] Error: HINDSIGHT_API_KEY is not set.")
        sys.exit(1)

    print("=" * 70)
    print(" SourceMind: Verification of Planted Memory Patterns in Hindsight")
    print("=" * 70)
    print(f"Bank ID  : {BANK_ID}")
    print(f"Base URL : {base_url}\n")

    client = Hindsight(base_url=base_url, api_key=api_key)

    try:
        for idx, item in enumerate(TEST_QUERIES, start=1):
            pattern_title = item["pattern"]
            query = item["query"]

            print("-" * 70)
            print(f"Test {idx}: {pattern_title}")
            print(f"Query : \"{query}\"")
            print("-" * 70)

            recall_resp = client.recall(bank_id=BANK_ID, query=query)
            results = getattr(recall_resp, "results", [])

            if not results:
                print("  [!] No recalled memories found for this query yet.")
            else:
                for r_idx, r in enumerate(results[:4], start=1):
                    text = getattr(r, "text", str(r))
                    print(f"  [{r_idx}] {text}")
            print()

        print("=" * 70)
        print("[+] Pattern recall tests completed.")
        print("=" * 70)

    except Exception as e:
        print(f"\n[-] Recall error: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
