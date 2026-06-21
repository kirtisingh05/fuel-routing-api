# routing/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.apps import apps  # We import the apps registry here
from .utils import get_coordinates, get_route_osrm, calculate_optimal_stops, haversine
from routing.apps import latlon_to_3d 
import time

@require_GET
def get_route(request):
    start_time = time.time()
    start_loc = request.GET.get('start')
    finish_loc = request.GET.get('finish')
    
    if not start_loc or not finish_loc:
        return JsonResponse({"error": "Missing start or finish"}, status=400)
        
    start_coords = get_coordinates(start_loc)
    finish_coords = get_coordinates(finish_loc)
    route_data = get_route_osrm(start_coords, finish_coords) if start_coords[0] else None
    
    if not route_data:
        return JsonResponse({"error": "Failed routing"}, status=400)
        
    route_points, route_distance = route_data
    
    # Grab the active, running instance of your app that has the RAM loaded
    routing_config = apps.get_app_config('routing')
    
    # 1. Map stations to route using KDTree
    cum_dist = [0.0]
    route_3d = [latlon_to_3d(*route_points[0])]
    for i in range(1, len(route_points)):
        cum_dist.append(cum_dist[-1] + haversine(*route_points[i-1], *route_points[i]))
        route_3d.append(latlon_to_3d(*route_points[i]))
        
    # Search the tree using the active instance
    indices_list = routing_config.kdtree.query_ball_point(route_3d, r=5.0) 
    station_dist_map = {}
    for r_idx, s_indices in enumerate(indices_list):
        for s_idx in s_indices:
            if s_idx not in station_dist_map:
                station_dist_map[s_idx] = cum_dist[r_idx]
                
    route_stations = []
    for s_idx, dist_along in station_dist_map.items():
        row = routing_config.stations_df.iloc[s_idx]
        route_stations.append({**row.to_dict(), 'distance': dist_along})
        
    # 2. Run Greedy Optimization
    result, error = calculate_optimal_stops(route_stations, route_distance)
    if error: 
        return JsonResponse({"error": error}, status=400)
    end_time = time.time()
    processing_time_ms = round((end_time - start_time) * 1000, 2)  
    return JsonResponse({
        "distance_miles": round(route_distance, 2),
        "total_fuel_cost": f"${result['total_cost']}",
        "processing_time_ms": f"{processing_time_ms} ms",
        "fuel_stops": result['stops'],
        "route_map": route_points 
    })
