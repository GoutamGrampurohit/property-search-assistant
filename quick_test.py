"""
Quick test to verify fixes
Run: python quick_test.py
"""

import sys
import pandas as pd
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.data_loader import DataLoader
from backend.query_parser import QueryParser
from backend.search_engine import SearchEngine

print("=" * 60)
print("QUICK TEST - Verifying Fixes")
print("=" * 60)

# Load data
print("\n1. Loading data...")
loader = DataLoader(data_dir='data')
df = loader.load_and_merge()

print(f"\n✅ Loaded {len(df)} properties")
print(f"   Cities: {df['city'].value_counts().to_dict()}")
print(f"   Missing city: {df['city'].isna().sum()} properties")

# Initialize components
parser = QueryParser()
search_engine = SearchEngine(df)

# Test queries
print("\n2. Testing Query Parsing...")
test_cases = [
    "Show me 3BHK in Mumbai",
    "2BHK under 1.5 Cr in Pune",
    "Ready to move apartments",
]

for query in test_cases:
    filters = parser.parse(query)
    print(f"\nQuery: '{query}'")
    print(f"  City: {filters.get('city')}")
    print(f"  BHK: {filters.get('bhk')}")
    print(f"  Budget: {filters.get('budget_max')}")
    print(f"  Status: {filters.get('status')}")
    print(f"  Project Name: {filters.get('project_name')}")  # Should be None!

# Test searches
print("\n3. Testing Searches...")

# Test 1: City + BHK
print("\n--- Test 1: '3BHK in Mumbai' ---")
filters = parser.parse("3BHK in Mumbai")
results = search_engine.search(filters, top_n=5)
print(f"Results: {len(results)} properties")
if len(results) > 0:
    print("✅ PASS - Found properties!")
    print(f"Sample: {results.iloc[0]['projectName']} - {results.iloc[0]['bhk']}BHK - ₹{results.iloc[0]['price_cr']:.2f} Cr")
else:
    print("❌ FAIL - No results")

# Test 2: BHK + Budget + City
print("\n--- Test 2: '2BHK under 1.5 Cr in Pune' ---")
filters = parser.parse("2BHK under 1.5 Cr in Pune")
results = search_engine.search(filters, top_n=5)
print(f"Results: {len(results)} properties")
if len(results) > 0:
    print("✅ PASS - Found properties!")
    print(f"Sample: {results.iloc[0]['projectName']} - ₹{results.iloc[0]['price_cr']:.2f} Cr")
else:
    print("❌ FAIL - No results")

# Test 3: Status only
print("\n--- Test 3: 'Ready to move apartments' ---")
filters = parser.parse("Ready to move apartments")
results = search_engine.search(filters, top_n=5)
print(f"Results: {len(results)} properties")
if len(results) > 0:
    print("✅ PASS - Found properties!")
    print(f"Sample: {results.iloc[0]['projectName']} - {results.iloc[0]['status']}")
else:
    print("❌ FAIL - No results")

# Test 4: Locality
print("\n--- Test 4: 'Properties near Chembur' ---")
filters = parser.parse("Properties near Chembur")
results = search_engine.search(filters, top_n=5)
print(f"Results: {len(results)} properties")
if len(results) > 0:
    print("✅ PASS - Found properties!")
    print(f"Sample: {results.iloc[0]['projectName']}")
else:
    print("❌ FAIL - No results")

# Test 5: Just BHK (should work even without city)
print("\n--- Test 5: '2BHK apartments' ---")
filters = parser.parse("2BHK apartments")
results = search_engine.search(filters, top_n=5)
print(f"Results: {len(results)} properties")
if len(results) > 0:
    print("✅ PASS - Found properties!")
    print(f"Sample: {results.iloc[0]['projectName']} - {results.iloc[0].get('city', 'No city')}")
else:
    print("❌ FAIL - No results")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

# Summary
total_tests = 5
passed = sum([
    len(search_engine.search(parser.parse("3BHK in Mumbai"), 5)) > 0,
    len(search_engine.search(parser.parse("2BHK under 1.5 Cr in Pune"), 5)) > 0,
    len(search_engine.search(parser.parse("Ready to move apartments"), 5)) > 0,
    len(search_engine.search(parser.parse("Properties near Chembur"), 5)) > 0,
    len(search_engine.search(parser.parse("2BHK apartments"), 5)) > 0,
])

print(f"\n📊 Summary: {passed}/{total_tests} tests passed")

if passed == total_tests:
    print("✅ All tests passed! Ready to use the app.")
    print("\nRun: streamlit run app.py")
else:
    print(f"⚠️  {total_tests - passed} test(s) failed. Check the output above.")
    if df['city'].isna().sum() > 20:
        print("\n💡 TIP: Many properties missing city. Update addresses to include city names.")
