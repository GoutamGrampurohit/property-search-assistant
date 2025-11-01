import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.df = None
        
    def load_and_merge(self):
        """Load all CSV files and merge them into a single dataframe"""
        
        # Load individual CSVs
        projects = pd.read_csv(os.path.join(self.data_dir, 'project.csv'))
        configs = pd.read_csv(os.path.join(self.data_dir, 'ProjectConfiguration.csv'))
        variants = pd.read_csv(os.path.join(self.data_dir, 'ProjectConfigurationVariant.csv'))
        addresses = pd.read_csv(os.path.join(self.data_dir, 'ProjectAddress.csv'))
        
        # Merge configs with variants
        config_variants = pd.merge(
            configs, 
            variants, 
            left_on='id', 
            right_on='configurationId',
            how='inner',
            suffixes=('_config', '_variant')
        )
        
        # Merge with projects
        full_data = pd.merge(
            config_variants,
            projects,
            left_on='projectId',
            right_on='id',
            how='inner',
            suffixes=('', '_project')
        )
        
        # Merge with addresses
        full_data = pd.merge(
            full_data,
            addresses,
            left_on='projectId',
            right_on='projectId',
            how='left',
            suffixes=('', '_address')
        )
        
        # Clean and transform data
        full_data = self._clean_data(full_data)
        
        self.df = full_data
        return self.df
    
    def _clean_data(self, df):
        """Clean and standardize the data"""
        
        print(f"[DataLoader] Cleaning {len(df)} rows...")
        
        # Convert price to numeric (handle millions)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['price_cr'] = df['price'] / 10000000  # Convert to Crores
        
        # Extract BHK from type field
        df['bhk'] = df['type'].str.extract(r'(\d+)')[0]
        df['bhk'] = pd.to_numeric(df['bhk'], errors='coerce')
        
        # Handle bathrooms as BHK proxy if bhk is missing
        df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
        df['bhk'] = df['bhk'].fillna(df['bathrooms'])
        
        # Standardize status
        df['status'] = df['status'].str.replace('_', ' ').str.title()
        
        # Extract city from fullAddress - IMPROVED LOGIC
        def extract_city(address):
            if pd.isna(address):
                return None
            address_lower = str(address).lower()
            
            # Check for city names (order matters - check specific first)
            if 'mumbai' in address_lower:
                return 'Mumbai'
            elif 'pune' in address_lower:
                return 'Pune'
            elif 'delhi' in address_lower:
                return 'Delhi'
            elif 'bangalore' in address_lower or 'bengaluru' in address_lower:
                return 'Bangalore'
            
            # If no city found, check common Pune areas
            pune_areas = ['pimpri', 'chinchwad', 'wakad', 'baner', 'kharadi', 
                         'hinjewadi', 'ravet', 'mundhwa', 'hadapsar', 'viman nagar',
                         'shivajinagar', 'camp', 'kothrud', 'aundh', 'mamurdi']
            if any(area in address_lower for area in pune_areas):
                return 'Pune'
            
            # Check common Mumbai areas
            mumbai_areas = ['chembur', 'andheri', 'bandra', 'goregaon', 'borivali',
                          'mulund', 'thane', 'powai', 'ghatkopar', 'kurla', 'dadar',
                          'worli', 'colaba', 'marine drive', 'lower parel']
            if any(area in address_lower for area in mumbai_areas):
                return 'Mumbai'
            
            return None
        
        df['city'] = df['fullAddress'].apply(extract_city)
        
        # For rows still without city, try to extract from other columns
        if 'landmark' in df.columns:
            mask = df['city'].isna()
            df.loc[mask, 'city'] = df.loc[mask, 'landmark'].apply(extract_city)
        
        # Carpet area
        df['carpetArea'] = pd.to_numeric(df['carpetArea'], errors='coerce')
        
        # Furnishing type
        df['furnishing'] = df['furnishedType'].fillna('Unfurnished')
        
        # Fill missing fullAddress with empty string for searching
        df['fullAddress'] = df['fullAddress'].fillna('')
        df['landmark'] = df['landmark'].fillna('')
        
        # Drop rows with critical missing data
        df = df.dropna(subset=['price', 'projectName'])
        
        print(f"[DataLoader] After cleaning: {len(df)} rows")
        print(f"[DataLoader] Cities found: {df['city'].value_counts().to_dict()}")
        print(f"[DataLoader] Properties without city: {df['city'].isna().sum()}")
        print(f"[DataLoader] BHK distribution: {df['bhk'].value_counts().head().to_dict()}")
        
        return df
    
    def get_data(self):
        """Return the merged dataframe"""
        if self.df is None:
            self.load_and_merge()
        return self.df