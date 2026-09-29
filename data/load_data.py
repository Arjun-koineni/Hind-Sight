import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from hindsight_client import Hindsight

BANK_ID = "buyer1"
BANK_MISSION = "Procurement assistant. Track vendor reliability, price behavior, delivery delays, quality issues, and the buyer's priorities."

EVENTS = [
    # Month 1 - April 2026
    {
        "id": "order-001",
        "date": datetime(2026, 4, 3, 9, 30, tzinfo=timezone.utc),
        "vendor": "Apex Industrial Supplies",
        "content": "On April 3, 2026, ordered 1,000 meters of mild steel conduit from Apex Industrial Supplies at $2.10 per meter (the cheapest quote received). Promised delivery date was April 12, 2026, but actual delivery was April 22, 2026. The shipment arrived 10 days late, although material quality was acceptable and price was significantly below market."
    },
    {
        "id": "order-002",
        "date": datetime(2026, 4, 8, 11, 0, tzinfo=timezone.utc),
        "vendor": "Bharat Polymers",
        "content": "On April 8, 2026, ordered 500 kg of polypropylene granules from Bharat Polymers at $1.85 per kg. Promised delivery date was April 15, 2026, and actual delivery occurred on April 15, 2026 on time. Note: Contact person Priya Patel confirmed the dispatch exclusively via WhatsApp at +91-98200-12345; she did not answer email inquiries."
    },
    {
        "id": "order-003",
        "date": datetime(2026, 4, 12, 14, 15, tzinfo=timezone.utc),
        "vendor": "Metro Steel & Wire",
        "content": "On April 12, 2026, ordered 800 kg of galvanized steel wire from Metro Steel & Wire at $3.20 per kg. Promised delivery date was April 20, 2026, and actual delivery arrived on April 19, 2026. The shipment was on time with standard quality and consistent pricing."
    },
    {
        "id": "order-004",
        "date": datetime(2026, 4, 17, 10, 0, tzinfo=timezone.utc),
        "vendor": "Titan Fasteners",
        "content": "On April 17, 2026, ordered a small batch of 1,500 units of M8 stainless hex bolts from Titan Fasteners at $0.40 per unit. Promised delivery date was April 21, 2026, and actual delivery arrived on April 20, 2026. Fast 3-day turnaround with flawless fulfillment for this small order quantity."
    },
    {
        "id": "order-005",
        "date": datetime(2026, 4, 22, 15, 30, tzinfo=timezone.utc),
        "vendor": "Pioneer Plastics",
        "content": "On April 22, 2026, ordered 300 kg of HDPE sheets from Pioneer Plastics at $4.10 per kg. Promised delivery date was April 30, 2026, and actual delivery arrived on April 29, 2026. Material arrived on schedule with standard commercial-grade quality."
    },
    {
        "id": "order-006",
        "date": datetime(2026, 4, 27, 13, 0, tzinfo=timezone.utc),
        "vendor": "Delta Packaging",
        "content": "On April 27, 2026, ordered 2,000 corrugated shipping cartons from Delta Packaging. Initial quote was $45.00 per hundred cartons, but after we presented a competing quote from Star Pack at $42.00, Delta Packaging dropped their price by 8% to $41.40 per hundred. Promised delivery was May 4, 2026, and actual delivery was May 4, 2026 on time."
    },
    {
        "id": "order-007",
        "date": datetime(2026, 4, 29, 16, 0, tzinfo=timezone.utc),
        "vendor": "Summit Chemicals",
        "content": "On April 29, 2026, ordered 200 liters of industrial degreaser from Summit Chemicals at $6.50 per liter. Promised delivery date was May 6, 2026, and actual delivery was May 5, 2026. Delivered on time with standard safety data sheet documentation."
    },

    # Month 2 - May 2026
    {
        "id": "order-008",
        "date": datetime(2026, 5, 4, 10, 30, tzinfo=timezone.utc),
        "vendor": "Zenith Castings",
        "content": "On May 4, 2026, ordered 300 custom aluminum valve bodies from Zenith Castings at $28.00 per unit. Promised delivery date was May 18, 2026, and actual delivery was May 17, 2026. Quality Issue: The entire batch showed severe porosity defects upon inspection causing leakage during hydrostatic pressure tests; batch was rejected and vendor was notified for urgent resolution."
    },
    {
        "id": "order-009",
        "date": datetime(2026, 5, 9, 11, 45, tzinfo=timezone.utc),
        "vendor": "Apex Industrial Supplies",
        "content": "On May 9, 2026, ordered 2,500 meters of structural tubing from Apex Industrial Supplies at $3.40 per meter (15% cheaper than any competitor). Promised delivery date was May 18, 2026, but actual delivery arrived on May 30, 2026. The shipment was 12 days late due to warehouse dispatch backlog, although the low price was unmatched."
    },
    {
        "id": "order-010",
        "date": datetime(2026, 5, 13, 14, 0, tzinfo=timezone.utc),
        "vendor": "Coastal Timber & Pallets",
        "content": "On May 13, 2026, ordered 150 standard heat-treated euro pallets from Coastal Timber & Pallets at $18.00 per pallet. Promised delivery date was May 20, 2026, and actual delivery arrived May 20, 2026 on time with solid pine construction."
    },
    {
        "id": "order-011",
        "date": datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc),
        "vendor": "Bharat Polymers",
        "content": "On May 16, 2026, ordered 1,200 kg of LDPE film rolls from Bharat Polymers at $2.20 per kg. Promised delivery date was May 25, 2026, and actual delivery arrived May 24, 2026. Note: Contact person Priya Patel responded within 10 minutes on WhatsApp at +91-98200-12345 with truck tracking details, emphasizing that WhatsApp is the only channel she checks for orders."
    },
    {
        "id": "order-012",
        "date": datetime(2026, 5, 20, 16, 30, tzinfo=timezone.utc),
        "vendor": "Orion Precision Alloys",
        "content": "On May 20, 2026, ordered 400 kg of brass hex rods from Orion Precision Alloys at $8.90 per kg. Promised delivery date was May 28, 2026, and actual delivery arrived May 27, 2026. High precision tolerances and delivered on schedule."
    },
    {
        "id": "order-013",
        "date": datetime(2026, 5, 24, 10, 0, tzinfo=timezone.utc),
        "vendor": "Zenith Castings",
        "content": "On May 24, 2026, Zenith Castings delivered a free replacement batch of 300 aluminum valve bodies to resolve the porous batch from earlier this month. Promised delivery date was June 2, 2026, and actual delivery was June 1, 2026. Quality Resolution: Pressure testing showed a 100% pass rate with zero porosity; vendor confirmed they recalibrated their foundry mold temperatures."
    },
    {
        "id": "order-014",
        "date": datetime(2026, 5, 29, 13, 15, tzinfo=timezone.utc),
        "vendor": "Vanguard Tooling",
        "content": "On May 29, 2026, ordered 50 solid carbide end mills from Vanguard Tooling at $32.00 per unit. Promised delivery date was June 5, 2026, and actual delivery arrived June 4, 2026. Tools arrived on schedule with high durability."
    },

    # Month 3 - June 2026
    {
        "id": "order-015",
        "date": datetime(2026, 6, 3, 11, 0, tzinfo=timezone.utc),
        "vendor": "Titan Fasteners",
        "content": "On June 3, 2026, placed a large bulk order of 20,000 units of M6 zinc-plated flange nuts with Titan Fasteners at $0.15 per unit. Promised delivery date was June 15, 2026, but actual delivery was July 6, 2026. The shipment was 21 days late because Titan Fasteners struggled with machinery capacity for large order volumes, causing assembly line downtime."
    },
    {
        "id": "order-016",
        "date": datetime(2026, 6, 7, 14, 30, tzinfo=timezone.utc),
        "vendor": "Swift Electricals",
        "content": "On June 7, 2026, ordered 500 meters of 4-core copper cabling from Swift Electricals at $5.20 per meter. Promised delivery date was June 16, 2026, and actual delivery arrived June 15, 2026 on time with standard insulation ratings."
    },
    {
        "id": "order-017",
        "date": datetime(2026, 6, 11, 10, 0, tzinfo=timezone.utc),
        "vendor": "Metro Steel & Wire",
        "content": "On June 11, 2026, ordered 1,200 kg of binding wire from Metro Steel & Wire at $2.85 per kg. Promised delivery date was June 19, 2026, and actual delivery arrived June 19, 2026 on schedule with consistent tensile strength."
    },
    {
        "id": "order-018",
        "date": datetime(2026, 6, 15, 15, 0, tzinfo=timezone.utc),
        "vendor": "Delta Packaging",
        "content": "On June 15, 2026, ordered 5,000 custom printed shipping cartons from Delta Packaging. Initial quote was $58.00 per hundred units. When informed that competitor BoxCraft offered $53.00, Delta Packaging immediately dropped their price by 10% to $52.20 per hundred. Promised delivery was June 26, 2026, and actual delivery was June 26, 2026 on time."
    },
    {
        "id": "order-019",
        "date": datetime(2026, 6, 19, 12, 0, tzinfo=timezone.utc),
        "vendor": "Apex Industrial Supplies",
        "content": "On June 19, 2026, ordered 800 steel angle bars from Apex Industrial Supplies at $14.50 per bar (lowest available price). Promised delivery date was June 28, 2026, but actual delivery arrived July 7, 2026. Delivered 9 days late, continuing their recurring pattern of delivery delays despite cheap pricing."
    },
    {
        "id": "order-020",
        "date": datetime(2026, 6, 23, 9, 30, tzinfo=timezone.utc),
        "vendor": "Pioneer Plastics",
        "content": "On June 23, 2026, ordered 450 kg of rigid PVC profiles from Pioneer Plastics at $3.75 per kg. Promised delivery date was July 1, 2026, and actual delivery arrived July 1, 2026 on schedule with dimensional tolerances verified."
    },
    {
        "id": "order-021",
        "date": datetime(2026, 6, 27, 16, 0, tzinfo=timezone.utc),
        "vendor": "Summit Chemicals",
        "content": "On June 27, 2026, ordered 50 drums of cooling lubricant from Summit Chemicals at $110.00 per drum. Promised delivery date was July 5, 2026, and actual delivery arrived July 4, 2026 on time with standard quality certifications."
    },

    # Month 4 - July 2026
    {
        "id": "order-022",
        "date": datetime(2026, 7, 2, 10, 15, tzinfo=timezone.utc),
        "vendor": "Titan Fasteners",
        "content": "On July 2, 2026, ordered a small quantity of 800 high-tensile socket head cap screws from Titan Fasteners at $0.75 per unit. Promised delivery date was July 6, 2026, and actual delivery arrived July 5, 2026. This small order was fulfilled in just 3 days without issues, confirming Titan is reliable for small orders."
    },
    {
        "id": "order-023",
        "date": datetime(2026, 7, 7, 13, 30, tzinfo=timezone.utc),
        "vendor": "Bharat Polymers",
        "content": "On July 7, 2026, ordered 800 kg of ABS thermoplastic granules from Bharat Polymers at $2.60 per kg. Promised delivery date was July 16, 2026, and actual delivery arrived July 15, 2026. Note: Delivery coordination was done strictly over WhatsApp chat with Priya Patel (+91-98200-12345); email order confirmations were left unread for 5 days."
    },
    {
        "id": "order-024",
        "date": datetime(2026, 7, 11, 11, 0, tzinfo=timezone.utc),
        "vendor": "Zenith Castings",
        "content": "On July 11, 2026, ordered 450 cast iron mounting brackets from Zenith Castings at $19.50 per unit. Promised delivery date was July 24, 2026, and actual delivery arrived July 23, 2026 on time. Material inspection confirmed flawless castings with zero porosity, showing that the May quality incident was completely resolved."
    },
    {
        "id": "order-025",
        "date": datetime(2026, 7, 16, 14, 0, tzinfo=timezone.utc),
        "vendor": "Coastal Timber & Pallets",
        "content": "On July 16, 2026, ordered 200 heavy-duty warehouse skids from Coastal Timber & Pallets at $24.00 per skid. Promised delivery date was July 25, 2026, and actual delivery arrived July 25, 2026 on time with robust construction."
    },
    {
        "id": "order-026",
        "date": datetime(2026, 7, 20, 10, 45, tzinfo=timezone.utc),
        "vendor": "Orion Precision Alloys",
        "content": "On July 20, 2026, ordered 600 kg of aerospace-grade aluminum 7075 round bars from Orion Precision Alloys at $12.50 per kg. Promised delivery date was July 30, 2026, and actual delivery arrived July 29, 2026 on time with mill test certifications."
    },
    {
        "id": "order-027",
        "date": datetime(2026, 7, 25, 15, 0, tzinfo=timezone.utc),
        "vendor": "Apex Industrial Supplies",
        "content": "On July 25, 2026, ordered 1,500 meters of square hollow steel section from Apex Industrial Supplies at $4.20 per meter (lowest quote). Promised delivery date was August 4, 2026, but actual delivery arrived August 18, 2026. The shipment was 14 days late; delays appear to be worsening over recent orders."
    },
    {
        "id": "order-028",
        "date": datetime(2026, 7, 29, 12, 15, tzinfo=timezone.utc),
        "vendor": "Vanguard Tooling",
        "content": "On July 29, 2026, ordered 100 indexable milling inserts from Vanguard Tooling at $18.00 per unit. Promised delivery date was August 6, 2026, and actual delivery arrived August 5, 2026 on time with solid wear resistance."
    },

    # Month 5 - August 2026
    {
        "id": "order-029",
        "date": datetime(2026, 8, 3, 9, 30, tzinfo=timezone.utc),
        "vendor": "Delta Packaging",
        "content": "On August 3, 2026, ordered 3,000 reinforced cardboard mailing tubes from Delta Packaging. Initial quote was $72.00 per hundred units. After presenting a competing quote from PackPros at $66.00, Delta Packaging dropped their price by 9% to $65.50 per hundred. Promised delivery was August 12, 2026, and actual delivery arrived August 12, 2026 on schedule."
    },
    {
        "id": "order-030",
        "date": datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        "vendor": "Titan Fasteners",
        "content": "On August 7, 2026, placed a large bulk order for 35,000 galvanized self-tapping screws with Titan Fasteners at $0.08 per unit. Promised delivery date was August 20, 2026, but actual delivery arrived September 14, 2026. The order was 25 days late due to severe production bottlenecks, proving that Titan Fasteners repeatedly fails on large volume orders."
    },
    {
        "id": "order-031",
        "date": datetime(2026, 8, 11, 14, 30, tzinfo=timezone.utc),
        "vendor": "Swift Electricals",
        "content": "On August 11, 2026, ordered 300 industrial circuit breakers from Swift Electricals at $15.50 per unit. Promised delivery date was August 20, 2026, and actual delivery arrived August 19, 2026 on time with standard electrical compliance certifications."
    },
    {
        "id": "order-032",
        "date": datetime(2026, 8, 16, 11, 0, tzinfo=timezone.utc),
        "vendor": "Zenith Castings",
        "content": "On August 16, 2026, ordered 600 machined ductile iron pulleys from Zenith Castings at $22.00 per unit. Promised delivery date was August 29, 2026, and actual delivery arrived August 28, 2026 on schedule. Flawless surface finish and zero defects, providing further evidence of consistent quality since their process fix."
    },
    {
        "id": "order-033",
        "date": datetime(2026, 8, 20, 16, 0, tzinfo=timezone.utc),
        "vendor": "Metro Steel & Wire",
        "content": "On August 20, 2026, ordered 1,500 kg of rebar tie wire from Metro Steel & Wire at $2.90 per kg. Promised delivery date was August 28, 2026, and actual delivery arrived August 28, 2026 on schedule at steady market pricing."
    },
    {
        "id": "order-034",
        "date": datetime(2026, 8, 24, 13, 45, tzinfo=timezone.utc),
        "vendor": "Bharat Polymers",
        "content": "On August 24, 2026, ordered 1,000 kg of nylon 6 granules from Bharat Polymers at $3.80 per kg. Promised delivery date was September 2, 2026, and actual delivery arrived September 1, 2026. Note: Contact person Priya Patel was contacted directly on WhatsApp (+91-98200-12345) and confirmed the truck dispatch in minutes; she did not check the order email."
    },
    {
        "id": "order-035",
        "date": datetime(2026, 8, 28, 15, 30, tzinfo=timezone.utc),
        "vendor": "Pioneer Plastics",
        "content": "On August 28, 2026, ordered 500 meters of extruded acrylic tubing from Pioneer Plastics at $6.80 per meter. Promised delivery date was September 5, 2026, and actual delivery arrived September 5, 2026 on time with clear optical quality."
    },

    # Month 6 - September 2026
    {
        "id": "order-036",
        "date": datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc),
        "vendor": "Apex Industrial Supplies",
        "content": "On September 2, 2026, ordered 2,000 meters of black iron pipe from Apex Industrial Supplies at $5.10 per meter (competitors were quoting $6.20). Promised delivery date was September 12, 2026, but actual delivery arrived September 27, 2026. The shipment was 15 days late. Apex remains the cheapest option by a wide margin, but their delivery delays have worsened and are now completely unreliable for tight production deadlines."
    },
    {
        "id": "order-037",
        "date": datetime(2026, 9, 6, 11, 15, tzinfo=timezone.utc),
        "vendor": "Titan Fasteners",
        "content": "On September 6, 2026, ordered a small batch of 500 units of custom nylon locking nuts from Titan Fasteners at $0.65 per unit. Promised delivery date was September 10, 2026, and actual delivery arrived September 9, 2026. Fast 3-day turnaround with excellent quality for this small batch order."
    },
    {
        "id": "order-038",
        "date": datetime(2026, 9, 10, 14, 0, tzinfo=timezone.utc),
        "vendor": "Summit Chemicals",
        "content": "On September 10, 2026, ordered 300 liters of anti-corrosion coating from Summit Chemicals at $14.00 per liter. Promised delivery date was September 18, 2026, and actual delivery arrived September 17, 2026 on time with standard quality certifications."
    },
    {
        "id": "order-039",
        "date": datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
        "vendor": "Coastal Timber & Pallets",
        "content": "On September 14, 2026, ordered 100 heavy machinery export crates from Coastal Timber & Pallets at $65.00 per crate. Promised delivery date was September 23, 2026, and actual delivery arrived September 23, 2026 on time with ISPM-15 phytosanitary certification."
    },
    {
        "id": "order-040",
        "date": datetime(2026, 9, 18, 15, 30, tzinfo=timezone.utc),
        "vendor": "Delta Packaging",
        "content": "On September 18, 2026, ordered 4,000 heavy-duty corrugated cartons from Delta Packaging. Initial price quote was $48.00 per hundred units. When the buyer cited a competing rate from Apex Pack of $43.50, Delta Packaging promptly dropped their price to $43.20 per hundred (10% drop). Promised delivery was September 26, 2026, and actual delivery arrived September 26, 2026 on schedule."
    },
    {
        "id": "order-041",
        "date": datetime(2026, 9, 22, 10, 30, tzinfo=timezone.utc),
        "vendor": "Orion Precision Alloys",
        "content": "On September 22, 2026, ordered 350 kg of phosphor bronze bushings from Orion Precision Alloys at $16.00 per kg. Promised delivery date was September 29, 2026, and actual delivery arrived September 29, 2026 on time with precision micro-finish."
    },
    {
        "id": "order-042",
        "date": datetime(2026, 9, 25, 16, 0, tzinfo=timezone.utc),
        "vendor": "Vanguard Tooling",
        "content": "On September 25, 2026, ordered 80 solid carbide drills from Vanguard Tooling at $25.00 per unit. Promised delivery date was September 30, 2026, and actual delivery arrived September 30, 2026 on time with standard cutting life."
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
    print(" SourceMind: Seed Data Ingestion into Hindsight Cloud")
    print("=" * 65)
    print(f"Bank ID  : {BANK_ID}")
    print(f"Base URL : {base_url}")
    print(f"Total Events to Ingest: {len(EVENTS)}")

    client = Hindsight(base_url=base_url, api_key=api_key)

    try:
        # 1. Configure bank mission
        print(f"\n[1] Setting Bank Mission...")
        mission_res = client.set_mission(bank_id=BANK_ID, mission=BANK_MISSION)
        print(f"    Mission configured: \"{BANK_MISSION}\"")

        # 2. Retain events
        print(f"\n[2] Retaining {len(EVENTS)} chronological order events...")
        vendor_counts = {}
        for idx, event in enumerate(EVENTS, start=1):
            vendor = event["vendor"]
            vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

            client.retain(
                bank_id=BANK_ID,
                content=event["content"],
                document_id=event["id"],
                timestamp=event["date"]
            )
            date_str = event["date"].strftime("%Y-%m-%d")
            print(f"    [{idx:02d}/{len(EVENTS):02d}] {event['id']} ({date_str}) | {vendor}")

        # 3. Summary
        print("\n" + "=" * 65)
        print(" INGESTION SUMMARY")
        print("=" * 65)
        print(f"Total Events Stored : {len(EVENTS)}")
        print(f"Total Vendors Covered: {len(vendor_counts)}")
        print("\nVendors & Event Breakdown:")
        for vendor, count in sorted(vendor_counts.items(), key=lambda x: x[0]):
            print(f"  - {vendor:<28}: {count} event(s)")

        print("\n[+] All events successfully retained into Hindsight Cloud.")

    except Exception as e:
        print(f"\n[-] Ingestion error: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
