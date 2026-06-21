# routing/utils.py
import requests
import math
import polyline

def get_coordinates(location_name):
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
    resp = requests.get(url, headers={'User-Agent': 'FuelRouting/1.0'}).json()
    return (float(resp[0]['lat']), float(resp[0]['lon'])) if resp else (None, None)

def get_route_osrm(start_coords, end_coords):
    start_str = f"{start_coords[1]},{start_coords[0]}" # OSRM expects lon, lat
    end_str = f"{end_coords[1]},{end_coords[0]}"
    url = f"http://router.project-osrm.org/route/v1/driving/{start_str};{end_str}?overview=full"
    
    resp = requests.get(url).json()
    if resp.get('code') != 'Ok':
        return None
        
    route = resp['routes'][0]
    distance_miles = route['distance'] * 0.000621371
    return polyline.decode(route['geometry']), distance_miles

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def calculate_optimal_stops(stations, route_distance, max_range=500, mpg=10):
    stations = sorted(stations, key=lambda x: x['distance'])
    stations = [s for s in stations if s['distance'] <= route_distance]
    
    dest = {'Truckstop Name': 'Destination', 'Address': 'Finish', 'Retail Price': 0.0, 'distance': route_distance}
    stations.append(dest)
    
    current_fuel = max_range
    current_pos = 0
    total_cost = 0.0
    stops = []
    
    reachable_from_start = [s for s in stations if 0 < s['distance'] <= max_range]
    if not reachable_from_start:
        return None, "Gap exceeds max range."
        
    current_station = min(reachable_from_start, key=lambda x: x['Retail Price'])
    current_fuel -= current_station['distance']
    current_pos = current_station['distance']
    current_idx = stations.index(current_station)
    
    while current_pos < route_distance:
        if current_pos == route_distance: break
        current_station = stations[current_idx]
        
        reachable = [s for s in stations[current_idx+1:] if s['distance'] <= current_pos + max_range]
        if not reachable: return None, "Unreachable gap detected."
            
        first_cheaper = dest if dest in reachable else next((s for s in reachable if s['Retail Price'] < current_station['Retail Price']), None)
            
        if first_cheaper:
            fuel_needed = first_cheaper['distance'] - current_pos
            if current_fuel < fuel_needed:
                buy_amount = fuel_needed - current_fuel
                cost = (buy_amount / mpg) * current_station['Retail Price']
                total_cost += cost
                stops.append({
                    'station': current_station['Truckstop Name'],
                    'address': current_station['Address'],
                    'price': current_station['Retail Price'],
                    'gallons': round(buy_amount / mpg, 2),
                    'cost': round(cost, 2)
                })
                current_fuel += buy_amount
            current_fuel -= fuel_needed
            current_pos = first_cheaper['distance']
            current_idx = stations.index(first_cheaper)
        else:
            buy_amount = max_range - current_fuel
            cost = (buy_amount / mpg) * current_station['Retail Price']
            total_cost += cost
            stops.append({
                    'station': current_station['Truckstop Name'],
                    'address': current_station['Address'],
                    # Wrap this in float() to fix the JSON crash
                    'price': float(current_station['Retail Price']), 
                    'gallons': round(buy_amount / mpg, 2),
                    'cost': round(cost, 2)
                })
            current_fuel = max_range
            cheapest_reachable = min(reachable, key=lambda x: x['Retail Price'])
            current_fuel -= (cheapest_reachable['distance'] - current_pos)
            current_pos = cheapest_reachable['distance']
            current_idx = stations.index(cheapest_reachable)
            
    return {'stops': stops, 'total_cost': round(total_cost, 2)}, None