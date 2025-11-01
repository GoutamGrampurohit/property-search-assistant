import re
import pandas as pd

class QueryParser:
    """Extract structured filters from natural language queries"""
    
    def __init__(self):
        # Predefined patterns
        self.city_patterns = [
            r'\b(mumbai|pune|delhi|bangalore|bengaluru)\b',
        ]
        
        self.bhk_patterns = [
            r'\b(\d+)\s*bhk\b',
            r'\b(\d+)\s*bedroom\b',
            r'\b(\d+)bhk\b',
        ]
        
        self.budget_patterns = [
            r'(?:under|below|less than|max|maximum|up to)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|l)\b',
            r'(?:rs\.?|₹)\s*(\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|l)\b',
            r'\b(\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|l)\b',
        ]
        
        self.status_patterns = {
            'ready': r'\b(ready|ready to move|immediate possession|ready for possession)\b',
            'under_construction': r'\b(under construction|upcoming|new launch|pre launch)\b',
        }
        
        # Common localities (expanded list - case insensitive matching)
        self.localities = [
            'chembur', 'wakad', 'baner', 'kharadi', 'hinjewadi', 'whitefield',
            'marathahalli', 'electronic city', 'ravet', 'mundhwa', 'andheri',
            'mulund', 'thane', 'goregaon', 'borivali', 'powai', 'ghatkopar',
            'shivajinagar', 'camp', 'punawale', 'mamurdi', 'pimpri', 'chinchwad',
            'viman nagar', 'koregaon park', 'hadapsar', 'wagholi', 'undri',
            'bavdhan', 'pashan', 'aundh', 'pimple saudagar', 'pimple nilakh',
            'dhanori', 'sus', 'thergaon', 'dehu road', 'talegaon'
        ]
    
    def parse(self, query):
        """
        Parse user query and extract structured filters
        
        Returns:
            dict: {
                'city': str or None,
                'bhk': int or None,
                'budget_max': float (in crores) or None,
                'status': str or None,
                'locality': str or None,
                'project_name': str or None (if mentioned)
            }
        """
        query_lower = query.lower()
        filters = {
            'city': None,
            'bhk': None,
            'budget_max': None,
            'status': None,
            'locality': None,
            'project_name': None
        }
        
        # Extract city
        for pattern in self.city_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filters['city'] = match.group(1).title()
                break
        
        # Extract BHK
        for pattern in self.bhk_patterns:
            match = re.search(pattern, query_lower)
            if match:
                filters['bhk'] = int(match.group(1))
                break
        
        # Extract budget
        for pattern in self.budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to crores
                if 'lakh' in unit or unit == 'l':
                    filters['budget_max'] = amount / 100
                else:  # crores
                    filters['budget_max'] = amount
                break
        
        # Extract status
        for status, pattern in self.status_patterns.items():
            if re.search(pattern, query_lower):
                filters['status'] = status.replace('_', ' ').title()
                break
        
        # Extract locality
        for locality in self.localities:
            if locality in query_lower:
                filters['locality'] = locality.title()
                break
        
        # Try to extract project name - IMPROVED LOGIC
        # Only extract if it looks like a real project name (not common query words)
        common_words = {
            'show', 'find', 'search', 'looking', 'want', 'need', 'properties', 
            'apartments', 'houses', 'homes', 'bhk', 'bedroom', 'ready', 'move',
            'construction', 'near', 'under', 'above', 'below', 'crore', 'lakh',
            'mumbai', 'pune', 'delhi', 'bangalore', 'city', 'area', 'locality'
        }
        
        words = query.split()
        capitalized = [w for w in words if w and w[0].isupper() and len(w) > 3]
        
        # Filter out common words
        capitalized = [w for w in capitalized if w.lower() not in common_words]
        
        # Only set project name if we have 1-3 real capitalized words
        if capitalized and len(capitalized) <= 3:
            filters['project_name'] = ' '.join(capitalized)
        
        return filters
    
    def extract_intent(self, query):
        """Determine user intent"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['show', 'find', 'search', 'looking', 'want', 'need']):
            return 'search'
        elif any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus']):
            return 'compare'
        elif any(word in query_lower for word in ['tell me about', 'details', 'info', 'information']):
            return 'info'
        else:
            return 'search'  # default