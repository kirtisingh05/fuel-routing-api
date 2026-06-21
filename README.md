# Optimal Fuel Routing API

A high-performance Django REST API that calculates the most cost-effective fuel stops along a driving route in the USA. 

This project was built to solve a classic spatial and algorithmic optimization problem: given a vehicle with a 500-mile range and a fuel efficiency of 10 MPG, how do we traverse a route while spending the absolute minimum amount of money on gas?

## 🚀 Key Features

* **Lightning-Fast Spatial Queries:** Uses an in-memory **SciPy KD-Tree** instead of a traditional SQL database to find gas stations along a 3,000-mile route in sub-milliseconds.
* **Greedy Algorithmic Optimization:** Calculates the absolute mathematically cheapest way to reach the destination based on varying fuel prices.
* **Minimal External API Calls:** Uses Nominatim (OpenStreetMap) for geocoding and OSRM for polyline routing, keeping network latency to an absolute minimum.
* **Server-Side Caching:** Implements Django caching to instantly return data for frequently searched routes.

## 🧠 The Architecture (Why it's fast)

Iterating 8,000 gas stations over a 3,000-point route polyline using standard Haversine math requires massive `O(N * M)` time complexity. Relying on a relational database (like PostgreSQL/PostGIS) for this specific read-heavy, static dataset introduces unnecessary disk I/O and network latency.

**The Solution:** On server startup, the application loads the geocoded CSV of fuel prices directly into the server's RAM and constructs a 3D Cartesian KD-Tree. When a route is requested, the API queries the KD-Tree, reducing the spatial search complexity to `O(M log N)`. 

The optimization step uses a **Greedy Algorithm**. At every stop, the algorithm looks ahead up to 500 miles:
1. If a **cheaper** station is reachable, it buys exactly enough fuel to reach it.
2. If all upcoming stations are **more expensive**, it fills the tank to maximum capacity (50 gallons) to carry the cheaper fuel forward.

## 🛠️ Installation & Setup

**Prerequisites:** Python 3.10+

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/fuel-routing-api.git](https://github.com/yourusername/fuel-routing-api.git)
   cd fuel-routing-api

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
