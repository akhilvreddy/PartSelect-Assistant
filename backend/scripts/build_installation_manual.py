#!/usr/bin/env python3
"""
Build installation_manual.json from installation.json for direct part number lookup
"""

import json
from pathlib import Path

def build_installation_manual():
    """Convert installation.json to a part-number-keyed manual"""
    
    # Load installation data
    data_path = Path("data/installation.json")
    with open(data_path, 'r') as f:
        installation_data = json.load(f)
    
    print(f"🔧 BUILDING INSTALLATION MANUAL")
    print(f"Processing {len(installation_data)} installation records...")
    
    # Create part-number-keyed manual
    installation_manual = {}
    processed = 0
    skipped = 0
    
    for record in installation_data:
        part_number = record.get("part_number", "").strip()
        text = record.get("text", "").strip()
        
        # Skip records without part number or meaningful text
        if not part_number or len(text) < 20:
            skipped += 1
            continue
            
        # Create manual entry
        installation_manual[part_number] = {
            "part_number": part_number,
            "title": record.get("title", "").strip(),
            "installation_text": text,
            "url": record.get("url", "").strip(),
            "id": record.get("id", "").strip()
        }
        processed += 1
    
    # Save manual
    manual_path = Path("data/maps/installation_manual.json")
    manual_path.parent.mkdir(exist_ok=True)
    
    with open(manual_path, 'w') as f:
        json.dump(installation_manual, f, indent=2)
    
    print(f"✅ Installation manual created:")
    print(f"   📦 Processed: {processed} parts")
    print(f"   ⏭️  Skipped: {skipped} parts (no part number or short text)")
    print(f"   💾 Saved to: {manual_path}")
    
    # Show some examples
    print(f"\n📋 SAMPLE ENTRIES:")
    sample_parts = list(installation_manual.keys())[:3]
    for part_num in sample_parts:
        entry = installation_manual[part_num]
        print(f"   🔧 {part_num}: {entry['title']}")
        print(f"      Text length: {len(entry['installation_text'])} chars")
        print(f"      Preview: {entry['installation_text'][:100]}...")
        print()
    
    # Check if PS11752991 is included
    if "PS11752991" in installation_manual:
        print(f"🎯 TEST PART PS11752991: ✅ INCLUDED")
        test_entry = installation_manual["PS11752991"]
        print(f"   Title: {test_entry['title']}")
        print(f"   Text length: {len(test_entry['installation_text'])} chars")
    else:
        print(f"🎯 TEST PART PS11752991: ❌ NOT FOUND")
    
    return len(installation_manual)

if __name__ == "__main__":
    count = build_installation_manual()
    print(f"\n🎉 Installation manual built with {count} parts!")
