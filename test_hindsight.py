import os
import sys
from dotenv import load_dotenv
from hindsight_client import Hindsight

def main():
    # Load environment variables from .env
    load_dotenv()

    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

    if not api_key or api_key == "your_hindsight_api_key_here":
        print("[-] Error: HINDSIGHT_API_KEY is not set.")
        print("    Please create a .env file (copied from .env.example) and add your actual Hindsight API key:")
        print("    HINDSIGHT_API_KEY=your_actual_key")
        print("    HINDSIGHT_BASE_URL=" + base_url)
        sys.exit(1)

    bank_id = "buyer1"
    print(f"[*] Initializing Hindsight client...")
    print(f"    Base URL : {base_url}")
    print(f"    Bank ID  : {bank_id}")

    try:
        client = Hindsight(base_url=base_url, api_key=api_key)

        test_content = "Vendor Apex Steel delivered 500 units of carbon steel on time with Grade A quality."
        print(f"\n[1] Retaining memory to bank '{bank_id}'...")
        print(f"    Content: \"{test_content}\"")
        retain_resp = client.retain(bank_id=bank_id, content=test_content)
        print(f"    Retain response: success={getattr(retain_resp, 'success', True)}")

        query = "How is Apex Steel quality and delivery?"
        print(f"\n[2] Recalling memory from bank '{bank_id}'...")
        print(f"    Query: \"{query}\"")
        recall_resp = client.recall(bank_id=bank_id, query=query)

        memories = getattr(recall_resp, "results", [])
        print(f"    Found {len(memories)} matching memory item(s):")
        for i, item in enumerate(memories, start=1):
            text = getattr(item, "text", str(item))
            print(f"    {i}. {text}")

        print("\n[+] Hindsight Cloud retain and recall test completed successfully!")

    except Exception as e:
        print(f"\n[-] Hindsight API call failed: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()
