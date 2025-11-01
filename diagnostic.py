"""
Diagnostic script to check your CSV data
Run with: python diagnose_data.py
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.data_loader import DataLoader
from backend.query_parser import QueryParser
from backend.search_engine import SearchEngine

def diagnose_data():
    """Run diagnostics on the loaded data"""
    
    print("=" * 60)
    print("PROPERTY DATA DIAGNOSTICS")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading Data...")
    loader = DataLoader(data_dir='data')
    df = loader.load_and_merge()
    
    print(f"\n✅ Loaded {len(df)} properties")
    
    # Check cities
    print("\n2. Cities Available:")
    cities = df['city'].value_counts()
    for city, count in cities.items():
        print(f"   - {city}: {count} properties")
    
    if df['city'].isna().sum() > 0:
        print(f"   ⚠️  WARNING: {df['city'].isna().sum()} properties have no city!")
    
    # Check BHK distribution
    print("\n3. BHK Distribution:")
    bhk_dist = df['bhk'].value_counts().sort_index()
    for bhk, count in bhk_dist.items():
        if not pd.isna(bhk):
            print(f"   - {int(bhk)}BHK: {count} properties")
    
    if df['bhk'].isna().sum() > 0:
        print(f"   ⚠️  WARNING: {df['bhk'].isna().sum()} properties have no BHK!")
    
    # Check price range
    print("\n4. Price Range:")
    print(f"   - Min: ₹{df['price_cr'].min():.2f} Cr")
    print(f"   - Max: ₹{df['price_cr'].max():.2f} Cr")
    print(f"   - Avg: ₹{df['price_cr'].mean():.2f} Cr")
    print(f"   - Median: ₹{df['price_cr'].median():.2f} Cr")
    
    # Check status
    print("\n5. Possession Status:")
    status_dist = df['status'].value_counts()
    for status, count in status_dist.items():
        print(f"   - {status}: {count} properties")
    
    # Check localities (from addresses)
    print("\n6. Top 10 Localities (from addresses):")
    # Extract common locality words
    import re
    all_addresses = ' '.join(df['fullAddress'].dropna().astype(str))
    localities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', all_addresses)
    from collections import Counter
    top_localities = Counter(localities).most_common(10)
    for locality, count in top_localities:
        print(f"   - {locality}: {count} mentions")
    
    # Sample records
    print("\n7. Sample Records:")
    sample = df[['projectName', 'city', 'bhk', 'price_cr', 'status', 'fullAddress']].head(3)
    print(sample.to_string(index=False))
    
    # Test some queries
    print("\n" + "=" * 60)
    print("TESTING SAMPLE QUERIES")
    print("=" * 60)
    
    parser = QueryParser()
    search_engine = SearchEngine(df)
    
    test_queries = [
        "Show me 3BHK in Mumbai",
        "2BHK under 1.5 Cr in Pune", 
        "Properties near Chembur",
        "Ready to move apartments",
        "3BHK apartments",  # No city
        "Properties under 2 Cr",  # Just budget
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        filters = parser.parse(query)
        print(f"Parsed filters: {filters}")
        results = search_engine.search(filters, top_n=5)
        print(f"Results: {len(results)} properties found")
        if len(results) > 0:
            print(f"✅ Sample: {results.iloc[0]['projectName']} - ₹{results.iloc[0]['price_cr']:.2f} Cr")
        else:
            print("❌ No results found")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    
    if df['city'].isna().sum() > 0:
        print("   ⚠️  Add city information to addresses")
    
    if df['bhk'].isna().sum() > 0:
        print("   ⚠️  Ensure all configurations have BHK or bathroom count")
    
    if len(df) < 10:
        print("   ⚠️  Very few properties! Add more data for better results")
    
    if len(cities) == 1:
        print("   💡 Consider adding properties from multiple cities")
    
    print("\n✅ Data looks good! Ready to run: streamlit run app.py")

if __name__ == '__main__':
    import pandas as pd
    diagnose_data()