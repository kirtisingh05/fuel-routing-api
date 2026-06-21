import pandas as pd
import numpy as np

# Load your original file
df = pd.read_csv('fuel-prices-for-be-assessment.csv')

# Generate mock coordinates covering the US (Roughly Lat: 30 to 45, Lon: -120 to -70)
np.random.seed(42)
df['lat'] = np.random.uniform(30.0, 45.0, len(df))
df['lon'] = np.random.uniform(-120.0, -70.0, len(df))

# Save the file that Django is looking for
df.to_csv('fuel_prices_geocoded.csv', index=False)
print("Mock geocoded CSV created! You can now run the Django server.")