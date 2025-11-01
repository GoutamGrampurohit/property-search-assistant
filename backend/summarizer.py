import pandas as pd

class Summarizer:
    """Generate natural language summaries from search results"""
    
    def generate_summary(self, results, filters, stats, expanded=None):
        """
        Generate a summary based on search results
        
        Args:
            results (pd.DataFrame): Search results
            filters (dict): Applied filters
            stats (dict): Statistics about results
            expanded (str): Which filter was relaxed, if any
            
        Returns:
            str: Natural language summary
        """
        if stats['count'] == 0:
            return self._no_results_summary(filters)
        
        if expanded:
            return self._expanded_search_summary(results, filters, stats, expanded)
        
        return self._standard_summary(results, filters, stats)
    
    def _standard_summary(self, results, filters, stats):
        """Generate standard summary when results are found"""
        summary_parts = []
        
        # Opening
        summary_parts.append(f"Found {stats['count']} propert{'y' if stats['count'] == 1 else 'ies'}")
        
        # Add filter context
        context_parts = []
        if filters.get('bhk'):
            context_parts.append(f"{int(filters['bhk'])}BHK")
        if filters.get('city'):
            context_parts.append(f"in {filters['city']}")
        if filters.get('locality'):
            context_parts.append(f"near {filters['locality']}")
        if filters.get('budget_max'):
            context_parts.append(f"under ₹{filters['budget_max']:.2f} Cr")
        if filters.get('status'):
            context_parts.append(f"({filters['status']})")
        
        if context_parts:
            summary_parts.append(" ".join(context_parts))
        
        summary = " ".join(summary_parts) + "."
        
        # Price range
        if stats['count'] > 1:
            summary += f" Prices range from ₹{stats['min_price']:.2f} Cr to ₹{stats['max_price']:.2f} Cr."
        else:
            summary += f" Priced at ₹{stats['min_price']:.2f} Cr."
        
        # Localities
        if stats['localities']:
            localities_str = ", ".join(stats['localities'][:3])
            summary += f" Located in {localities_str}."
        
        # Status distribution
        if len(stats['statuses']) > 1:
            summary += f" Includes both ready-to-move and under-construction properties."
        elif stats['statuses']:
            status = stats['statuses'][0].lower()
            summary += f" All properties are {status}."
        
        return summary
    
    def _expanded_search_summary(self, results, filters, stats, expanded):
        """Generate summary when search was expanded"""
        summary = f"No exact matches found. "
        
        if expanded == 'locality':
            summary += f"Showing {stats['count']} properties in nearby areas"
        elif expanded == 'status':
            summary += f"Showing {stats['count']} properties with different possession status"
        elif expanded == 'budget':
            summary += f"Showing {stats['count']} properties slightly above your budget"
        elif expanded == 'bhk':
            summary += f"Showing {stats['count']} properties with different configurations"
        
        # Add context
        context_parts = []
        if filters.get('city'):
            context_parts.append(f"in {filters['city']}")
        if filters.get('bhk') and expanded != 'bhk':
            context_parts.append(f"{int(filters['bhk'])}BHK")
        
        if context_parts:
            summary += " " + " ".join(context_parts)
        
        summary += "."
        
        # Price range
        if stats['count'] > 0:
            summary += f" Prices range from ₹{stats['min_price']:.2f} Cr to ₹{stats['max_price']:.2f} Cr."
        
        return summary
    
    def _no_results_summary(self, filters):
        """Generate summary when no results found"""
        summary = "No properties found matching your criteria"
        
        criteria = []
        if filters.get('bhk'):
            criteria.append(f"{int(filters['bhk'])}BHK")
        if filters.get('budget_max'):
            criteria.append(f"under ₹{filters['budget_max']:.2f} Cr")
        if filters.get('city'):
            criteria.append(f"in {filters['city']}")
        if filters.get('locality'):
            criteria.append(f"near {filters['locality']}")
        if filters.get('status'):
            criteria.append(filters['status'])
        
        if criteria:
            summary += f" ({', '.join(criteria)})"
        
        summary += ". Try adjusting your budget, location, or BHK requirements to see more options."
        
        return summary
    
    def format_property_card(self, row):
        """
        Format a single property as a card dictionary
        
        Returns:
            dict: Property card data
        """
        # Format price
        price_cr = row['price_cr']
        if price_cr >= 1:
            price_str = f"₹{price_cr:.2f} Cr"
        else:
            price_lakh = price_cr * 100
            price_str = f"₹{price_lakh:.2f} L"
        
        # Extract BHK type
        bhk_str = row.get('type', 'N/A')
        if pd.isna(bhk_str):
            bhk_str = f"{int(row['bhk'])}BHK" if not pd.isna(row['bhk']) else 'N/A'
        
        # Get locality from address
        locality = "Mumbai" if "Mumbai" in str(row.get('fullAddress', '')) else "Pune"
        
        # Extract amenities from available fields
        amenities = []
        if row.get('furnishing') and row['furnishing'] != 'Unfurnished':
            amenities.append(row['furnishing'])
        if not pd.isna(row.get('carpetArea')):
            amenities.append(f"{int(row['carpetArea'])} sq.ft")
        if not pd.isna(row.get('balcony')) and int(row.get('balcony', 0)) > 0:
            amenities.append(f"{int(row['balcony'])} Balcony")
        
        # Build slug URL
        slug = row.get('slug', '')
        url = f"/project/{slug}" if slug else "#"
        
        return {
            'title': row.get('projectName', 'Unknown Project'),
            'location': f"{locality}",
            'bhk': bhk_str,
            'price': price_str,
            'status': row.get('status', 'N/A'),
            'amenities': amenities[:3],  # Top 3
            'carpet_area': row.get('carpetArea', 'N/A'),
            'url': url,
            'project_category': row.get('projectCategory', 'Residential')
        }