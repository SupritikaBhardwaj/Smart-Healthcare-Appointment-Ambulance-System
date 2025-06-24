import numpy as np
from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
from sklearn.cluster import KMeans
import heapq
import math
from collections import defaultdict
import os
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Constants
AVG_AMBULANCE_SPEED_KMH = 40  # Average speed in urban areas
TRAFFIC_FACTORS = {
    'delhi': 1.7,
    'mumbai': 1.6,
    'bangalore': 1.5,
    'chennai': 1.4,
    'kolkata': 1.4,
    'hyderabad': 1.3,
    'default': 1.2
}

# Master list of all medical specialties
ALL_SPECIALTIES = [
    'cardiology', 'neurology', 'oncology', 'orthopedics', 'pediatrics',
    'trauma', 'psychiatry', 'neurosurgery', 'transplant', 'bariatric',
    'fertility', 'dermatology', 'ophthalmology', 'ent', 'urology',
    'nephrology', 'gastroenterology', 'pulmonology', 'endocrinology',
    'hematology', 'rheumatology', 'infectious-diseases', 'general-surgery'
]




def haversine(coord1, coord2):
    try:
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        radius = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
            math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return radius * c
    except Exception as e:
        app.logger.error(f"Error in haversine: {str(e)}")
        return 0

# Now define your data structures that use haversine
hospitals = {
    # Delhi Hospitals (3)
    1: {"name": "AIIMS Delhi", "city": "Delhi", "location": (28.5676, 77.2107),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 1500, "current_patients": 1200},
    2: {"name": "Sir Ganga Ram Hospital", "city": "Delhi", "location": (28.6345, 77.2128),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 800, "current_patients": 700},
    3: {"name": "Max Super Specialty", "city": "Delhi", "location": (28.5240, 77.2209),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 700, "current_patients": 600},
    
    # Mumbai Hospitals (3)
    4: {"name": "KEM Hospital", "city": "Mumbai", "location": (18.9750, 72.8258),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 1200, "current_patients": 1100},
    5: {"name": "Lilavati Hospital", "city": "Mumbai", "location": (19.0760, 72.8345),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 900, "current_patients": 800},
    6: {"name": "Kokilaben Hospital", "city": "Mumbai", "location": (19.1200, 72.8367),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 750, "current_patients": 650},
    
    # Bangalore Hospitals (3)
    7: {"name": "NIMHANS", "city": "Bangalore", "location": (12.9436, 77.5937),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 1000, "current_patients": 900},
    8: {"name": "Manipal Hospital", "city": "Bangalore", "location": (12.9716, 77.5946),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 850, "current_patients": 750},
    9: {"name": "Fortis Hospital", "city": "Bangalore", "location": (12.9345, 77.6267),
        "specialties": ALL_SPECIALTIES, "bed_capacity": 700, "current_patients": 600},
    
    # Chennai Hospitals (3)
    10: {"name": "Apollo Chennai", "city": "Chennai", "location": (13.0396, 80.2437),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 900, "current_patients": 800},
    11: {"name": "MIOT International", "city": "Chennai", "location": (13.0827, 80.2707),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 750, "current_patients": 650},
    12: {"name": "Global Hospitals", "city": "Chennai", "location": (13.0127, 80.2307),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 600, "current_patients": 500},
    
    # Other Major Cities (2 each)
    # Kolkata
    13: {"name": "AMRI Hospital", "city": "Kolkata", "location": (22.5726, 88.3639),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 950, "current_patients": 850},
    14: {"name": "Ruby General", "city": "Kolkata", "location": (22.5926, 88.3839),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 700, "current_patients": 600},
    
    # Hyderabad
    15: {"name": "Yashoda Hospitals", "city": "Hyderabad", "location": (17.3850, 78.4867),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 850, "current_patients": 750},
    16: {"name": "Continental Hospitals", "city": "Hyderabad", "location": (17.4250, 78.4467),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 700, "current_patients": 600},
    
    # Chandigarh
    17: {"name": "PGI Chandigarh", "city": "Chandigarh", "location": (30.7046, 76.7179),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 1000, "current_patients": 900},
    18: {"name": "Fortis Mohali", "city": "Chandigarh", "location": (30.7346, 76.7879),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 750, "current_patients": 650},
    
    # Pune
    19: {"name": "Ruby Hall Clinic", "city": "Pune", "location": (18.5204, 73.8567),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 800, "current_patients": 700},
    20: {"name": "Sahyadri Hospital", "city": "Pune", "location": (18.5404, 73.8767),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 650, "current_patients": 550},
    
    # Ahmedabad
    21: {"name": "CIMS Hospital", "city": "Ahmedabad", "location": (23.0225, 72.5714),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 750, "current_patients": 650},
    22: {"name": "Zydus Hospitals", "city": "Ahmedabad", "location": (23.0425, 72.5514),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 600, "current_patients": 500},
    
    # Jaipur
    23: {"name": "Sawai Man Singh", "city": "Jaipur", "location": (26.9124, 75.7873),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 900, "current_patients": 800},
    24: {"name": "Fortis Jaipur", "city": "Jaipur", "location": (26.9324, 75.8073),
         "specialties": ALL_SPECIALTIES, "bed_capacity": 700, "current_patients": 600}
}

ambulances = {
    # Delhi ambulances
    1: {"location": (28.5676, 77.3107), "status": "available", "city": "Delhi"},
    2: {"location": (28.6345, 77.3128), "status": "available", "city": "Delhi"},
    3: {"location": (28.5240, 77.3209), "status": "available", "city": "Delhi"},
    
    # Mumbai ambulances
    4: {"location": (18.9750, 72.9258), "status": "available", "city": "Mumbai"},
    5: {"location": (19.0760, 72.9345), "status": "available", "city": "Mumbai"},
    6: {"location": (19.1136, 72.8697), "status": "available", "city": "Mumbai"},
    
    # Bangalore ambulances
    7: {"location": (12.9436, 77.6937), "status": "available", "city": "Bangalore"},
    8: {"location": (12.9716, 77.6846), "status": "available", "city": "Bangalore"},
    9: {"location": (12.9345, 77.7167), "status": "available", "city": "Bangalore"},
    
    # Other cities (2 ambulances each)
    10: {"location": (13.0313, 80.2775), "status": "available", "city": "Chennai"},
    11: {"location": (12.9972, 80.2277), "status": "available", "city": "Chennai"},
    12: {"location": (22.5726, 88.3739), "status": "available", "city": "Kolkata"},
    13: {"location": (22.5926, 88.3939), "status": "available", "city": "Kolkata"},
    14: {"location": (17.3850, 78.4967), "status": "available", "city": "Hyderabad"},
    15: {"location": (17.4250, 78.4567), "status": "available", "city": "Hyderabad"},
    16: {"location": (30.7046, 76.8179), "status": "available", "city": "Chandigarh"},
    17: {"location": (30.7346, 76.7979), "status": "available", "city": "Chandigarh"},
    18: {"location": (18.5204, 73.8667), "status": "available", "city": "Pune"},
    19: {"location": (18.5598, 73.7998), "status": "available", "city": "Pune"},
    20: {"location": (23.0225, 72.5814), "status": "available", "city": "Ahmedabad"},
    21: {"location": (23.0425, 72.5614), "status": "available", "city": "Ahmedabad"},
    22: {"location": (26.9124, 75.7973), "status": "available", "city": "Jaipur"},
    23: {"location": (26.9324, 75.8173), "status": "available", "city": "Jaipur"}
}

indian_cities = {
    city.lower(): hospitals[next(k for k,v in hospitals.items() if v["city"].lower() == city.lower())]["location"]
    for city in ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", 
                "Hyderabad", "Chandigarh", "Pune", "Ahmedabad", "Jaipur"]
}
CITY_LOCALITIES = {
    "delhi": {
        "connaught_place": (28.6328, 77.2197),
        "chanakyapuri": (28.5925, 77.1856),
        "karol_bagh": (28.6516, 77.1907),
        "saket": (28.5245, 77.2069),
        "rohini": (28.7400, 77.0850)
    },
    "mumbai": {
        "colaba": (18.9061, 72.8106),
        "bandra": (19.0552, 72.8402),
        "andheri": (19.1197, 72.8464),
        "dadar": (19.0176, 72.8428),
        "powai": (19.1197, 72.9056)
    },
    "bangalore": {
        "mg_road": (12.9716, 77.5946),
        "indiranagar": (12.9784, 77.6408),
        "koramangala": (12.9279, 77.6271),
        "whitefield": (12.9698, 77.7499),
        "jayanagar": (12.9308, 77.5838)
    },
     "chennai": {
        "kodambakkam": (13.0481, 80.2214),
        "valasaravakkam": (13.0485, 80.1775),
        "villivakkam": (13.1063, 80.2049),
        "besant_nagar": (13.0111, 80.2744),
        "mylapore": (13.0313, 80.2775),
        "anna_nagar": (13.0783, 80.2167),
        "t_nagar": (13.0377, 80.2296)
    },
    "pune": {
        "kothrud": (18.5074, 73.8077),
        "hadapsar": (18.5089, 73.9257),
        "shivaji_nagar": (18.5308, 73.8474),
        "baner": (18.5590, 73.7861),
        "viman_nagar": (18.5679, 73.9143)
    },
    "kolkata": {
        "salt_lake": (22.5867, 88.4172),
        "howrah": (22.5958, 88.2636),
        "park_street": (22.5525, 88.3524),
        "behala": (22.5015, 88.3141),
        "dum_dum": (22.6224, 88.4240)
    },
    "hyderabad": {
        "banjara_hills": (17.4160, 78.4483),
        "gachibowli": (17.4435, 78.3498),
        "begumpet": (17.4432, 78.4604),
        "kukatpally": (17.4933, 78.3995),
        "madhapur": (17.4490, 78.3910)
    },
    "chandigarh": {
        "sector_17": (30.7415, 76.7681),
        "sector_22": (30.7352, 76.7735),
        "manimajra": (30.7136, 76.8189),
        "sector_49": (30.6904, 76.7473),
        "sector_15": (30.7595, 76.7693)
    },
    "ahmedabad": {
        "navrangpura": (23.0422, 72.5609),
        "maninagar": (22.9914, 72.6034),
        "bopal": (23.0306, 72.4702),
        "satellite": (23.0225, 72.5296),
        "vastrapur": (23.0386, 72.5260)
    },
    "jaipur": {
        "malviya_nagar": (26.8497, 75.8007),
        "vaishali_nagar": (26.9116, 75.7480),
        "mansarovar": (26.8540, 75.7615),
        "bani_park": (26.9331, 75.8004),
        "c_scheme": (26.9111, 75.8123)
    }

}
emergency_queue = []

# Road network with realistic connections
highway_connections = [
    # Delhi connections
    ((28.5676, 77.2107), (30.7046, 76.7179), 250),  # Chandigarh
    ((28.5676, 77.2107), (26.9124, 75.7873), 260),  # Jaipur
    ((28.5676, 77.2107), (23.0225, 72.5714), 800),  # Ahmedabad
    ((28.5676, 77.2107), (18.9750, 72.8258), 1400), # Mumbai
    
    # Mumbai connections
    ((18.9750, 72.8258), (12.9436, 77.5937), 1000), # Bangalore
    ((18.9750, 72.8258), (18.5204, 73.8567), 150),  # Pune
    
    # Southern corridor
    ((12.9436, 77.5937), (13.0396, 80.2437), 350),  # Chennai
    ((12.9436, 77.5937), (17.3850, 78.4867), 500),  # Hyderabad
    
    # Eastern connections
    ((22.5726, 88.3639), (17.3850, 78.4867), 800),  # Kolkata-Hyderabad
]

# Build road graph
road_graph = defaultdict(dict)
for start, end, dist in highway_connections:
    road_graph[start][end] = dist
    road_graph[end][start] = dist

# Add intra-city connections
for city, coord in indian_cities.items():
    city_hospitals = [h for h in hospitals.values() if h["city"].lower() == city]
    for hospital in city_hospitals:
        dist = haversine(coord, hospital["location"])
        road_graph[coord][hospital["location"]] = dist
        road_graph[hospital["location"]][coord] = dist

# Add ambulance connections
for amb_id, ambulance in ambulances.items():
    nearest_hospital = min(
        [h["location"] for h in hospitals.values() if h["city"].lower() == ambulance["city"].lower()],
        key=lambda x: haversine(ambulance["location"], x)
    )
    dist = haversine(ambulance["location"], nearest_hospital)
    road_graph[ambulance["location"]][nearest_hospital] = dist
    road_graph[nearest_hospital][ambulance["location"]] = dist
def cluster_hospitals_by_specialty(emergency):
    try:
        specialty_hospitals = [
            hid for hid, hospital in hospitals.items() 
            if emergency["emergency_type"] in hospital.get("specialties", [])
        ]
        return specialty_hospitals if specialty_hospitals else list(hospitals.keys())
    except Exception as e:
        app.logger.error(f"Error in cluster_hospitals_by_specialty: {str(e)}")
        return list(hospitals.keys())

def assign_hospital(emergency, hospitals_in_cluster):
    try:
        patient_location = emergency["location"]
        
        # If we have hospitals in cluster (with matching specialty), find nearest among them
        if hospitals_in_cluster:
            return min(hospitals_in_cluster, 
                      key=lambda hid: haversine(patient_location, hospitals[hid]["location"]))
        
        # Otherwise find nearest hospital regardless of specialty
        return min(hospitals.keys(),
                 key=lambda hid: haversine(patient_location, hospitals[hid]["location"]))
    
    except Exception as e:
        app.logger.error(f"Error in assign_hospital: {str(e)}")
        # Fallback: return hospital with ID 1 if something goes wrong
        return 1

def calculate_time_estimate(route, city):
    """Calculate time estimate considering distance and traffic"""
    total_distance = sum(haversine(route[i], route[i+1]) for i in range(len(route)-1))
    
    # Adjust speed based on distance (highway vs urban)
    avg_speed = 60 if total_distance > 50 else 40  # km/h
    
    # Get traffic factor
    traffic_factor = TRAFFIC_FACTORS.get(city.lower(), TRAFFIC_FACTORS["default"])
    
    # Calculate time in minutes
    time_minutes = (total_distance / avg_speed) * 60 * traffic_factor
    
    # Ensure minimum time of 5 minutes
    return max(5, round(time_minutes))
def process_emergency(emergency_id):
    try:
        # Get the emergency object by ID
        emergency = next(e for e in emergency_queue if e["id"] == emergency_id)
        app.logger.info(f"Processing emergency in {emergency['city']} at {emergency['location']}")

        # Step 1: Cluster hospitals by specialty
        hospitals_in_cluster = cluster_hospitals_by_specialty(emergency)
        app.logger.info(f"Eligible hospitals: {hospitals_in_cluster}")

        # Step 2: Find best hospital
        hospital_id = assign_hospital(emergency, hospitals_in_cluster)
        hospital = hospitals[hospital_id]
        app.logger.info(f"Selected hospital: {hospital['name']} at {hospital['location']}")

        # Step 3: Dispatch nearest ambulance
        ambulance_id, path = dispatch_ambulance(emergency["location"], hospital_id)

        # Step 4: Get optimal route
        optimal_route = calculate_optimal_route(path)

        # Step 5: Calculate time and distance
        estimated_time = calculate_time_estimate(optimal_route, emergency["city"])
        total_distance = sum(haversine(optimal_route[i], optimal_route[i+1]) 
                             for i in range(len(optimal_route)-1))

        # Return all required data
        return {
            "emergency_id": emergency_id,
            "assigned_hospital": hospital["name"],
            "ambulance_dispatched": ambulance_id,
            "optimal_route": optimal_route,
            "estimated_time": estimated_time,
            "distance_km": round(total_distance, 2),
            "hospital_location": hospital["location"],
            "city": emergency["city"],
            "locality": emergency.get("locality", "")
        }

    except Exception as e:
        app.logger.error(f"Error in process_emergency: {str(e)}")
        raise


def dispatch_ambulance(patient_location, hospital_id):
    try:
        hospital_location = hospitals[hospital_id]["location"]
        
        # Find available ambulances within reasonable distance
        available_ambulances = []
        for aid, amb in ambulances.items():
            if amb["status"] == "available":
                distance = haversine(amb["location"], patient_location)
                if distance < 100:  # Within 100km
                    available_ambulances.append((aid, distance))
        
        # If no ambulances nearby, use the closest one
        if not available_ambulances:
            closest = min(ambulances.items(), 
                         key=lambda item: haversine(item[1]["location"], patient_location))
            available_ambulances = [(closest[0], haversine(closest[1]["location"], patient_location))]
        
        # Select best ambulance (closest with A* path finding)
        best_ambulance = None
        best_path = None
        min_time = float('inf')
        
        for aid, distance in available_ambulances:
            amb_loc = ambulances[aid]["location"]
            # Path should be: ambulance -> patient -> hospital
            path_to_patient = a_star_algorithm(amb_loc, patient_location)
            path_to_hospital = a_star_algorithm(patient_location, hospital_location)
            full_path = path_to_patient + path_to_hospital[1:]  # Skip duplicate patient point
            time_estimate = calculate_time_estimate(full_path, ambulances[aid]["city"])
            
            if time_estimate < min_time:
                min_time = time_estimate
                best_ambulance = aid
                best_path = full_path
        
        # Mark ambulance as dispatched
        ambulances[best_ambulance]["status"] = "dispatched"
        
        return best_ambulance, best_path
    except Exception as e:
        app.logger.error(f"Error in dispatch_ambulance: {str(e)}")
        return 1, [ambulances[1]["location"], patient_location, hospitals[hospital_id]["location"]]

def calculate_optimal_route(path):
    try:
        if len(path) <= 2:
            return path
        
        # For multi-point routes, use Dijkstra's between each segment
        optimized_path = [path[0]]
        for i in range(len(path)-1):
            segment = dijkstra_algorithm(path[i], path[i+1])
            optimized_path += segment[1:]  # Avoid duplicate points
        
        return optimized_path
    except Exception as e:
        app.logger.error(f"Error in calculate_optimal_route: {str(e)}")
        return path

def a_star_algorithm(start, goal):
    try:
        if start not in road_graph or goal not in road_graph:
            return [start, goal]
        
        open_set = [(0 + haversine(start, goal), 0, start, [start])]
        closed_set = set()
        
        while open_set:
            _, g, current, path = heapq.heappop(open_set)
            
            if current == goal:
                return path
            
            if current in closed_set:
                continue
                
            closed_set.add(current)
            
            for neighbor, weight in road_graph.get(current, {}).items():
                if neighbor not in closed_set:
                    new_g = g + weight
                    new_f = new_g + haversine(neighbor, goal)
                    heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))
        
        return dijkstra_algorithm(start, goal)  # Fallback to Dijkstra's
    except Exception as e:
        app.logger.error(f"Error in a_star_algorithm: {str(e)}")
        return [start, goal]

def dijkstra_algorithm(start, goal):
    try:
        if start not in road_graph:
            return [start, goal]
        
        distances = {node: float('infinity') for node in road_graph}
        distances[start] = 0
        previous_nodes = {node: None for node in road_graph}
        priority_queue = [(0, start)]
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            if current_node == goal:
                break
                
            if current_distance > distances[current_node]:
                continue
                
            for neighbor, weight in road_graph.get(current_node, {}).items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = previous_nodes.get(current)
        
        path.reverse()
        return path if path and path[0] == start else [start, goal]
    except Exception as e:
        app.logger.error(f"Error in dijkstra_algorithm: {str(e)}")
        return [start, goal]

@app.route('/')
def home():
    return render_template('index.html', cities=list(indian_cities.keys()))

@app.route('/request_ambulance', methods=['POST'])
def request_ambulance():
    try:
        data = request.form
        city = data.get('city', '').lower()
        locality = data.get('locality', '').lower()
        emergency_type = data.get('emergency_type', '').lower()
        severity = data.get('severity', '5')
        
        # Validate inputs
        if not all([city, locality, emergency_type]):
            return jsonify({"error": "City, locality and emergency type are required"}), 400
        
        if city not in indian_cities:
            return jsonify({"error": f"Service not available in {city}"}), 400
        
        try:
            severity = min(max(int(severity), 1), 10)
        except ValueError:
            severity = 5

        # Get exact location from locality
        if city in CITY_LOCALITIES and locality in CITY_LOCALITIES[city]:
            exact_location = CITY_LOCALITIES[city][locality]
        else:
            exact_location = indian_cities[city]  # Fallback to city center

        # Create emergency record
        emergency_id = len(emergency_queue) + 1
        emergency_queue.append({
            "id": emergency_id,
            "location": exact_location,
            "emergency_type": emergency_type,
            "severity": severity,
            "city": city,
            "locality": locality
        })
        
        result = process_emergency(emergency_id)
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    """Endpoint to get hospital data for visualization"""
    return jsonify({
        "hospitals": hospitals,
        "ambulances": ambulances,
        "road_graph": road_graph
    })
if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
