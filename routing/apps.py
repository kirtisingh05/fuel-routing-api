# routing/apps.py
from django.apps import AppConfig
from django.conf import settings
import pandas as pd
from scipy.spatial import cKDTree
import math
import os

def latlon_to_3d(lat, lon):
    """Convert lat/lon to 3D Cartesian coordinates for fast KDTree querying"""
    R = 3958.8 # Earth radius in miles
    lat_rad, lon_rad = math.radians(lat), math.radians(lon)
    return (
        R * math.cos(lat_rad) * math.cos(lon_rad),
        R * math.cos(lat_rad) * math.sin(lon_rad),
        R * math.sin(lat_rad)
    )

class RoutingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'routing'
    
    stations_df = None
    kdtree = None

    def ready(self):
        from django.conf import settings
        import os
        
        csv_path = os.path.join(settings.BASE_DIR, 'fuel_prices_geocoded.csv')
        
        # ADD THIS DEBUG LINE:
        print(f"DEBUG: I am looking for the CSV file exactly here: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            # Ensure proper types
            df['Retail Price'] = pd.to_numeric(df['Retail Price'], errors='coerce')
            df = df.dropna(subset=['Retail Price', 'lat', 'lon'])
            
            coords_3d = [latlon_to_3d(row['lat'], row['lon']) for _, row in df.iterrows()]
            self.kdtree = cKDTree(coords_3d)
            self.stations_df = df
            print(f"SUCCESS: Loaded {len(df)} stations into RAM KDTree!")
        except Exception as e:
            print("CRITICAL ERROR: Could not load fuel prices CSV.", e)