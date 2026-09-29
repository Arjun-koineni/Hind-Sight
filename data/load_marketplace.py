import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from hindsight_client import Hindsight

BANK_ID = "marketplace"
BANK_MISSION = "Procurement marketplace. Aggregate buyer reviews, vendor reliability, delivery speeds, pricing, and material quality across different cities and manufacturers."

REVIEWS = [
    {
        "id": "mkt-001",
        "date": datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc),
        "vendor": "Kaveri Metals & Tubes",
        "content": "Review by Ramesh Sharma (Plant Manager, Shanti Engineering, Pune): Ordered 1,500 meters of seamless structural steel tubing from Kaveri Metals & Tubes. Delivered in 4 days with exact millimeter tolerances. Highly responsive sales team on phone and email, pricing was 8% below regional market averages."
    },
    {
        "id": "mkt-002",
        "date": datetime(2026, 5, 22, 14, 30, tzinfo=timezone.utc),
        "vendor": "Sterling Castings Ltd",
        "content": "Review by Anita Desai (Procurement Lead, Precision Valves Ltd, Vadodara): Placed an order for 500 ductile iron valve bodies with Sterling Castings Ltd. All castings passed 100% hydrostatic pressure and X-ray porosity testing with zero defects. Delivery was 2 days ahead of schedule with complete metallurgical test reports."
    },
    {
        "id": "mkt-003",
        "date": datetime(2026, 6, 5, 11, 15, tzinfo=timezone.utc),
        "vendor": "Nordic Fasteners Corp",
        "content": "Review by Vikram Mehta (Operations Director, Apex Auto Components, Chennai): Ordered 50,000 bulk M8 flange bolts from Nordic Fasteners Corp. Unlike other suppliers that bottleneck on volume, Nordic delivered the entire bulk batch in 6 days with zero defects. Highly recommended for large volume manufacturing, though prices are slightly above budget options."
    },
    {
        "id": "mkt-004",
        "date": datetime(2026, 6, 18, 16, 0, tzinfo=timezone.utc),
        "vendor": "EcoBox Logistics Packaging",
        "content": "Review by Deepak Patel (Supply Chain Head, Western Pack Innovations, Ahmedabad): Ordered 10,000 double-wall corrugated shipping cartons from EcoBox Logistics Packaging. Extremely competitive volume pricing, delivered on time. Box bursting strength tested at 250 PSI, meeting export standards."
    },
    {
        "id": "mkt-005",
        "date": datetime(2026, 6, 28, 9, 30, tzinfo=timezone.utc),
        "vendor": "Solventex Industrial Solutions",
        "content": "Review by Kavita Reddy (Procurement Manager, Deccan Chem Industries, Hyderabad): Sourced 80 drums of metalworking cutting fluid and degreaser from Solventex Industrial Solutions. Arrived strictly on promised dispatch schedule with complete SDS safety documentation. Consistent chemical purity across all batches."
    },
    {
        "id": "mkt-006",
        "date": datetime(2026, 7, 8, 13, 0, tzinfo=timezone.utc),
        "vendor": "Global Polymer Dynamics",
        "content": "Review by Pooja Malhotra (Materials Director, Northern Polymers, Noida): Ordered 2,000 kg of engineering-grade polyoxymethylene (POM) resin from Global Polymer Dynamics. Resin quality and tensile strength were superb, but vendor requires strict 1,000 kg minimum order quantities and their payment terms are 100% advance for new buyers."
    },
    {
        "id": "mkt-007",
        "date": datetime(2026, 7, 19, 15, 45, tzinfo=timezone.utc),
        "vendor": "Kaveri Metals & Tubes",
        "content": "Review by Sunil Kulkarni (Factory Owner, Deccan FabTech, Coimbatore): Procured 3,000 meters of square carbon steel tubing from Kaveri Metals & Tubes for a factory expansion project. Arrived on time with zero bends or surface rust. They offer 5% credit discount on prompt payment."
    },
    {
        "id": "mkt-008",
        "date": datetime(2026, 7, 30, 10, 30, tzinfo=timezone.utc),
        "vendor": "Sterling Castings Ltd",
        "content": "Review by Meera Joshi (Quality Auditor, Western Industrial Castings, Rajkot): Ordered 350 cast steel pump casings from Sterling Castings Ltd. Flawless surface finish and excellent dimensional accuracy. The foundry provided automated coordinate measuring machine (CMM) inspection data for every single part."
    },
    {
        "id": "mkt-009",
        "date": datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc),
        "vendor": "Nordic Fasteners Corp",
        "content": "Review by Siddharth Rao (Production Lead, Bangalore AeroTech, Bangalore): Ordered 12,000 high-tensile grade 10.9 socket screws from Nordic Fasteners Corp. Fast 3-day turnaround, certified zinc-nickel anti-corrosion coating. Excellent vendor for deadline-driven assembly lines."
    },
    {
        "id": "mkt-010",
        "date": datetime(2026, 8, 20, 14, 15, tzinfo=timezone.utc),
        "vendor": "EcoBox Logistics Packaging",
        "content": "Review by Naveen Singhal (Buyer, Jaipur Machinery Works, Jaipur): Purchased 5,000 custom printed shipping cartons from EcoBox Logistics Packaging. They matched a lower quote from a local vendor and gave us free palletization. Delivered in 5 business days."
    },
    {
        "id": "mkt-011",
        "date": datetime(2026, 8, 28, 11, 0, tzinfo=timezone.utc),
        "vendor": "Solventex Industrial Solutions",
        "content": "Review by Arun Nair (Operations Manager, Malabar Metal Works, Kochi): Ordered 40 barrels of anti-rust rust-inhibiting wash from Solventex Industrial Solutions. Shipment arrived on time via dedicated tanker lorry, very easy to work with their logistics dispatch team."
    },
    {
        "id": "mkt-012",
        "date": datetime(2026, 9, 5, 16, 30, tzinfo=timezone.utc),
        "vendor": "Global Polymer Dynamics",
        "content": "Review by Farhan Khan (Manufacturing Head, Delhi Precision Tools, Gurgaon): Procured 1,500 kg of glass-fiber reinforced nylon granules from Global Polymer Dynamics. High heat deflection temperature and consistent melt flow index. Delivery took 8 days instead of the promised 6 days due to interstate transport delays."
    },
    {
        "id": "mkt-013",
        "date": datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc),
        "vendor": "Kaveri Metals & Tubes",
        "content": "Review by Rajesh Verma (Plant Head, Bharat Steel Structures, Indore): Ordered 1,200 meters of heavy-gauge circular steel hollow sections from Kaveri Metals & Tubes. Arrived 1 day ahead of schedule. Excellent weldability and clean mill test certificates provided."
    },
    {
        "id": "mkt-014",
        "date": datetime(2026, 9, 21, 13, 45, tzinfo=timezone.utc),
        "vendor": "Nordic Fasteners Corp",
        "content": "Review by Harish Gupta (General Manager, Sterling Assembly Line, Chennai): We regularly order 40,000+ units of industrial fasteners from Nordic Fasteners Corp. They maintain a buffer stock in their warehouse specifically for contracted buyers, eliminating supply chain risk."
    },
    {
        "id": "mkt-015",
        "date": datetime(2026, 9, 26, 15, 0, tzinfo=timezone.utc),
        "vendor": "Sterling Castings Ltd",
        "content": "Review by Geeta Swaminathan (Logistics Lead, South Coast Fab, Madurai): Purchased 400 custom aluminum mounting brackets from Sterling Castings Ltd. All castings had zero porosity and passed ultrasonic inspection without failure. Very reliable partner for critical equipment."
    }
]

def main():
    load_dotenv()
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

    if not api_key:
        print("[-] Error: HINDSIGHT_API_KEY environment variable is not set.")
        sys.exit(1)

    print("=" * 65)
    print(" SourceMind: Ingesting Marketplace Reviews into Hindsight Cloud")
    print("=" * 65)
    print(f"Bank ID  : {BANK_ID}")
    print(f"Base URL : {base_url}")
    print(f"Reviews  : {len(REVIEWS)}")

    client = Hindsight(base_url=base_url, api_key=api_key)

    try:
        # 1. Create marketplace bank and mission
        print(f"\n[1] Creating bank '{BANK_ID}' and setting mission...")
        try:
            client.create_bank(bank_id=BANK_ID, name=BANK_ID)
        except Exception as e:
            print(f"    Note: bank already exists or created ({e})")

        try:
            client.set_mission(bank_id=BANK_ID, mission=BANK_MISSION)
            print(f"    Marketplace mission set: \"{BANK_MISSION}\"")
        except Exception as e:
            print(f"    Mission note: {e}")

        # 2. Retain reviews
        print(f"\n[2] Retaining {len(REVIEWS)} marketplace buyer reviews...")
        vendor_counts = {}
        for idx, rev in enumerate(REVIEWS, start=1):
            vendor = rev["vendor"]
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

            client.retain(
                bank_id=BANK_ID,
                content=rev["content"],
                document_id=rev["id"],
                timestamp=rev["date"]
            )
            print(f"    [{idx:02d}/{len(REVIEWS):02d}] {rev['id']} | {vendor}")

        # 3. Summary
        print("\n" + "=" * 65)
        print(" MARKETPLACE INGESTION SUMMARY")
        print("=" * 65)
        print(f"Total Reviews Stored : {len(REVIEWS)}")
        print(f"Marketplace Vendors Covered: {len(vendor_counts)}")
        for vendor, count in sorted(vendor_counts.items()):
            print(f"  - {vendor:<30}: {count} review(s)")

        print("\n[+] Marketplace data successfully retained into Hindsight Cloud.")

    except Exception as e:
        print(f"\n[-] Marketplace ingestion error: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
