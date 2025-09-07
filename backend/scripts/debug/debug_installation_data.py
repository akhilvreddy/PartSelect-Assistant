#!/usr/bin/env python3
"""
Debug installation data quality and ChromaDB ingestion issues
"""

import json
import os
from pathlib import Path

def analyze_installation_data():
    """Analyze the installation.json data quality"""
    
    # Load installation data
    data_path = Path("data/installation.json")
    with open(data_path, 'r') as f:
        installation_data = json.load(f)
    
    print(f"🔍 INSTALLATION DATA ANALYSIS")
    print(f"Total records: {len(installation_data)}")
    print("=" * 50)
    
    # Analyze text content
    empty_text = 0
    short_text = 0
    good_text = 0
    text_lengths = []
    
    # Analyze metadata completeness
    missing_difficulty = 0
    missing_time = 0
    missing_tools = 0
    
    sample_records = []
    
    for i, record in enumerate(installation_data):
        # Text analysis
        text = record.get("text", "")
        text_length = len(text.strip())
        text_lengths.append(text_length)
        
        if text_length == 0:
            empty_text += 1
        elif text_length < 50:
            short_text += 1
        else:
            good_text += 1
            
        # Metadata analysis
        if not record.get("difficulty", "").strip():
            missing_difficulty += 1
        if not record.get("time_required", "").strip():
            missing_time += 1
        if not record.get("tools") or len(record.get("tools", [])) == 0:
            missing_tools += 1
            
        # Collect samples
        if i < 5:
            sample_records.append({
                "id": record.get("id", "N/A"),
                "part_number": record.get("part_number", "N/A"),
                "title": record.get("title", "N/A"),
                "text_length": text_length,
                "difficulty": record.get("difficulty", ""),
                "time_required": record.get("time_required", ""),
                "tools": record.get("tools", [])
            })
    
    # Text quality stats
    print(f"📝 TEXT CONTENT ANALYSIS:")
    print(f"   Empty text: {empty_text} ({empty_text/len(installation_data)*100:.1f}%)")
    print(f"   Short text (<50 chars): {short_text} ({short_text/len(installation_data)*100:.1f}%)")
    print(f"   Good text (>=50 chars): {good_text} ({good_text/len(installation_data)*100:.1f}%)")
    print(f"   Average text length: {sum(text_lengths)/len(text_lengths):.1f} chars")
    print(f"   Min text length: {min(text_lengths)} chars")
    print(f"   Max text length: {max(text_lengths)} chars")
    print()
    
    # Metadata completeness
    print(f"📊 METADATA COMPLETENESS:")
    print(f"   Missing difficulty: {missing_difficulty} ({missing_difficulty/len(installation_data)*100:.1f}%)")
    print(f"   Missing time_required: {missing_time} ({missing_time/len(installation_data)*100:.1f}%)")
    print(f"   Missing tools: {missing_tools} ({missing_tools/len(installation_data)*100:.1f}%)")
    print()
    
    # Sample records
    print(f"📋 SAMPLE RECORDS:")
    for record in sample_records:
        print(f"   ID: {record['id']}")
        print(f"   Part: {record['part_number']}")
        print(f"   Title: {record['title']}")
        print(f"   Text length: {record['text_length']} chars")
        print(f"   Difficulty: '{record['difficulty']}'")
        print(f"   Time: '{record['time_required']}'")
        print(f"   Tools: {record['tools']}")
        print(f"   ---")
    
    # Find the specific part we tested
    print(f"🎯 SPECIFIC PART ANALYSIS (PS11752991):")
    for record in installation_data:
        if record.get("part_number") == "PS11752991":
            print(f"   Found: {record['id']}")
            print(f"   Title: {record['title']}")
            print(f"   Text length: {len(record.get('text', ''))} chars")
            print(f"   Text preview: {record.get('text', '')[:200]}...")
            break
    else:
        print(f"   ❌ PS11752991 not found in installation data!")

if __name__ == "__main__":
    analyze_installation_data()
