import pandas as pd
import re

class SearchEngine:
    """Search and filter properties based on parsed query filters"""
    
    def __init__(self, dataframe):
        self.df = dataframe
        print(f"[SearchEngine] Initialized with {len(dataframe)} properties")
        print(f"[SearchEngine] Cities available: {dataframe['city'].unique().tolist()}")
        print(f"[SearchEngine] Price range: ₹{dataframe['price_cr'].min():.2f} Cr to ₹{dataframe['price_cr'].max():.2f} Cr")
    
    def search(self, filters, top_n=10):
        """
        Search properties based on filters
        
        Args:
            filters (dict): Extracted filters from query parser
            top_n (int): Maximum number of results to return
            
        Returns:
            pd.DataFrame: Filtered results
        """
        results = self.df.copy()
        initial_count = len(results)
        
        print(f"\n[Search] Starting with {initial_count} properties")
        print(f"[Search] Filters: {filters}")
        
        # Apply city filter - IMPROVED to handle missing cities
        if filters.get('city'):
            city_results = results[
                results['city'].str.contains(filters['city'], case=False, na=False)
            ]
            
            # If city filter returns nothing, try matching city in address
            if len(city_results) == 0:
                city_results = results[
                    results['fullAddress'].str.contains(filters['city'], case=False, na=False)
                ]
            
            results = city_results
            print(f"[Search] After city filter: {len(results)} properties")
        
        # Apply BHK filter (with tolerance)
        if filters.get('bhk'):
            bhk_value = filters['bhk']
            results = results[
                (results['bhk'] >= bhk_value - 0.5) & 
                (results['bhk'] <= bhk_value + 0.5)
            ]
            print(f"[Search] After BHK filter: {len(results)} properties")
        
        # Apply budget filter
        if filters.get('budget_max'):
            results = results[results['price_cr'] <= filters['budget_max']]
            print(f"[Search] After budget filter: {len(results)} properties")
        
        # Apply status filter - IMPROVED MATCHING
        if filters.get('status'):
            status_query = filters['status'].lower()
            # Match partial status
            if 'ready' in status_query:
                results = results[
                    results['status'].str.contains('Ready', case=False, na=False)
                ]
            elif 'construction' in status_query or 'under' in status_query:
                results = results[
                    results['status'].str.contains('Construction', case=False, na=False)
                ]
            print(f"[Search] After status filter: {len(results)} properties")
        
        # Apply locality filter - more flexible matching
        if filters.get('locality'):
            locality = filters['locality']
            # Try matching in fullAddress, landmark, and even projectName
            locality_mask = (
                results['fullAddress'].str.contains(locality, case=False, na=False) |
                results['landmark'].str.contains(locality, case=False, na=False)
            )
            results = results[locality_mask]
            print(f"[Search] After locality filter '{locality}': {len(results)} properties")
        
        # Apply project name filter
        if filters.get('project_name'):
            results = results[
                results['projectName'].str.contains(
                    filters['project_name'], 
                    case=False, 
                    na=False
                )
            ]
            print(f"[Search] After project name filter: {len(results)} properties")
        
        # Sort by price (ascending)
        results = results.sort_values('price_cr')
        
        # Remove duplicates based on project + configuration
        results = results.drop_duplicates(
            subset=['projectName', 'type', 'price_cr'],
            keep='first'
        )
        
        print(f"[Search] Final results (after dedup): {len(results)} properties")
        
        # Return top N results
        return results.head(top_n)
    
    def get_statistics(self, results, filters):
        """
        Generate statistics about search results
        
        Returns:
            dict: Statistics like count, avg price, localities, etc.
        """
        if results.empty:
            return {
                'count': 0,
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
                'localities': [],
                'statuses': [],
                'bhk_types': []
            }
        
        stats = {
            'count': len(results),
            'avg_price': results['price_cr'].mean(),
            'min_price': results['price_cr'].min(),
            'max_price': results['price_cr'].max(),
            'localities': results['fullAddress'].str.extract(
                r'(Chembur|Wakad|Baner|Kharadi|Ravet|Mundhwa|Andheri|Mulund|Shivajinagar|Punawale)', 
                flags=re.IGNORECASE
            )[0].dropna().unique().tolist(),
            'statuses': results['status'].unique().tolist(),
            'bhk_types': sorted(results['bhk'].dropna().unique().tolist())
        }
        
        return stats
    
    def expand_search(self, filters):
        """
        If no results found, try expanding search criteria
        
        Returns:
            pd.DataFrame: Results with relaxed filters
        """
        # Try removing least important filters one by one
        relaxed_filters = filters.copy()
        
        # Remove locality first
        if relaxed_filters.get('locality'):
            relaxed_filters['locality'] = None
            results = self.search(relaxed_filters)
            if not results.empty:
                return results, 'locality'
        
        # Remove status
        if relaxed_filters.get('status'):
            relaxed_filters['status'] = None
            results = self.search(relaxed_filters)
            if not results.empty:
                return results, 'status'
        
        # Increase budget by 20%
        if relaxed_filters.get('budget_max'):
            relaxed_filters['budget_max'] *= 1.2
            results = self.search(relaxed_filters)
            if not results.empty:
                return results, 'budget'
        
        # Remove BHK constraint
        if relaxed_filters.get('bhk'):
            relaxed_filters['bhk'] = None
            results = self.search(relaxed_filters)
            if not results.empty:
                return results, 'bhk'
        
        return pd.DataFrame(), None