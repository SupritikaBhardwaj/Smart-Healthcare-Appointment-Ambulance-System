




let map;
let routeLayer;
let markersLayer;
// Initialize map
function initMap() {
    map = L.map('map').setView([20.5937, 78.9629], 5); // Center of India

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Initialize layers
    routeLayer = L.layerGroup().addTo(map);
    markersLayer = L.layerGroup().addTo(map);
}
// City and locality data
const LOCALITIES = {
    "delhi": [
        { name: "Connaught Place", value: "connaught_place" },
        { name: "Chanakyapuri", value: "chanakyapuri" },
        { name: "Karol Bagh", value: "karol_bagh" },
        { name: "Saket", value: "saket" },
        { name: "Rohini", value: "rohini" }
    ],
    "mumbai": [
        { name: "Colaba", value: "colaba" },
        { name: "Bandra", value: "bandra" },
        { name: "Andheri", value: "andheri" },
        { name: "Dadar", value: "dadar" },
        { name: "Powai", value: "powai" }
    ],
    "bangalore": [
        { name: "MG Road", value: "mg_road" },
        { name: "Indiranagar", value: "indiranagar" },
        { name: "Koramangala", value: "koramangala" },
        { name: "Whitefield", value: "whitefield" },
        { name: "Jayanagar", value: "jayanagar" }
    ],
    "chennai": [
        { name: "Kodambakkam", value: "kodambakkam" },
        { name: "Valasaravakkam", value: "valasaravakkam" },
        { name: "Villivakkam", value: "villivakkam" },
        { name: "Besant Nagar", value: "besant_nagar" },
        { name: "Mylapore", value: "mylapore" },
        { name: "Anna Nagar", value: "anna_nagar" },
        { name: "T. Nagar", value: "t_nagar" }
    ],
    "pune": [
        { name: "Kothrud", value: "kothrud" },
        { name: "Hadapsar", value: "hadapsar" },
        { name: "Shivaji Nagar", value: "shivaji_nagar" },
        { name: "Baner", value: "baner" },
        { name: "Viman Nagar", value: "viman_nagar" }
    ],
    "kolkata": [
        { name: "Salt Lake", value: "salt_lake" },
        { name: "Howrah", value: "howrah" },
        { name: "Park Street", value: "park_street" },
        { name: "Behala", value: "behala" },
        { name: "Dum Dum", value: "dum_dum" }
    ],
    "hyderabad": [
        { name: "Banjara Hills", value: "banjara_hills" },
        { name: "Gachibowli", value: "gachibowli" },
        { name: "Begumpet", value: "begumpet" },
        { name: "Kukatpally", value: "kukatpally" },
        { name: "Madhapur", value: "madhapur" }
    ],
    "chandigarh": [
        { name: "Sector 17", value: "sector_17" },
        { name: "Sector 22", value: "sector_22" },
        { name: "Manimajra", value: "manimajra" },
        { name: "Sector 49", value: "sector_49" },
        { name: "Sector 15", value: "sector_15" }
    ],
    "ahmedabad": [
        { name: "Navrangpura", value: "navrangpura" },
        { name: "Maninagar", value: "maninagar" },
        { name: "Bopal", value: "bopal" },
        { name: "Satellite", value: "satellite" },
        { name: "Vastrapur", value: "vastrapur" }
    ],
    "jaipur": [
        { name: "Malviya Nagar", value: "malviya_nagar" },
        { name: "Vaishali Nagar", value: "vaishali_nagar" },
        { name: "Mansarovar", value: "mansarovar" },
        { name: "Bani Park", value: "bani_park" },
        { name: "C Scheme", value: "c_scheme" }
    ]
};

// City to coordinate mapping
const cityCoordinates = {
    "delhi": [28.7041, 77.1025],
    "mumbai": [19.0760, 72.8777],
    "chennai": [13.0827, 80.2707],
    "bangalore": [12.9716, 77.5946],
    "hyderabad": [17.3850, 78.4867],
    "kolkata": [22.5726, 88.3639],
    "pune": [18.5204, 73.8567],
    "ahmedabad": [23.0225, 72.5714],
    "jaipur": [26.9124, 75.7873],
    "chandigarh": [30.7333, 76.7794]
};

// Icons
// Custom icons
const ambulanceIcon = L.divIcon({
    html: '<div style="background: #3498db; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 3px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">🚑</div>',
    className: 'custom-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});

const hospitalIcon = L.divIcon({
    html: '<div style="background: #2ecc71; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 3px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">🏥</div>',
    className: 'custom-icon',
    iconSize: [35, 35],
    iconAnchor: [17, 17]
});

const patientIcon = L.divIcon({
    html: '<div style="background: #f39c12; color: white; width: 25px; height: 25px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; border: 3px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">📍</div>',
    className: 'custom-icon',
    iconSize: [25, 25],
    iconAnchor: [12, 12]
});

// Map Initialization
function initMap() {
    map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    routeLayer = L.layerGroup().addTo(map);
    markersLayer = L.layerGroup().addTo(map);
}

// Update localities when city changes
document.addEventListener('DOMContentLoaded', function () {
    initMap();
    console.log('Map initialized');

    const citySelect = document.getElementById('city');
    const localitySelect = document.getElementById('locality');

    citySelect.addEventListener('change', function () {
        const selectedCity = this.value.toLowerCase();
        localitySelect.innerHTML = '<option value="">Select locality</option>';
        localitySelect.disabled = !selectedCity;

        if (LOCALITIES[selectedCity]) {
            LOCALITIES[selectedCity].forEach(locality => {
                const opt = document.createElement('option');
                opt.value = locality.value;
                opt.textContent = locality.name;
                localitySelect.appendChild(opt);
            });
        }
    });
});

// Request ambulance
window.requestAmbulance = async function () {
    try {
        const city = document.getElementById('city')?.value?.trim();
        const locality = document.getElementById('locality')?.value?.trim();
        const emergencyType = document.getElementById('emergency_type')?.value?.trim();
        const severity = document.getElementById('severity')?.value?.trim();

        if (!city || !locality || !emergencyType || !severity) {
            throw new Error('Please fill all required fields');
        }

        const button = document.querySelector('.request-btn');
        if (button) {
            button.disabled = true;
            button.innerHTML = '<div class="loading">Processing Request</div>';
        }

        const response = await fetch('http://127.0.0.1:5000/request_ambulance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                city: city,
                locality: locality,
                emergency_type: emergencyType,
                severity: severity
            })
        });

        const responseText = await response.text();
        let data;
        try {
            data = JSON.parse(responseText);
        } catch {
            throw new Error('Invalid server response');
        }

        if (!response.ok) {
            throw new Error(data?.error || 'Request failed');
        }

        if (data) {
            // Update result panel fields
            document.getElementById('emergency_id').textContent = data.emergency_id || 'N/A';
            document.getElementById('hospital').textContent = data.assigned_hospital || 'N/A';
            document.getElementById('ambulance').textContent = data.ambulance_dispatched || 'N/A';
            document.getElementById('time').textContent = `${data.estimated_time || 'N/A'} minutes`;

            // Show the result panel
            const resultPanel = document.getElementById('result');
            resultPanel.classList.add('show');

            // Plot the route if available
            if (data.optimal_route && data.optimal_route.length > 0) {
                plotRoute(data.optimal_route, city, data.assigned_hospital, data.ambulance_dispatched);
            } else {
                // Fallback: show patient location
                const loc = cityCoordinates[city.toLowerCase()];
                if (loc) {
                    markersLayer.clearLayers();
                    L.marker(loc, { icon: patientIcon })
                        .bindPopup(`<b>📍 Emergency Location</b><br>City: ${city}`)
                        .addTo(markersLayer);
                    map.setView(loc, 12);
                }
            }

            showNotification('Emergency request submitted successfully!', 'success');
        }
    } catch (err) {
        console.error(err);
        showNotification(`Error: ${err.message}`, 'error');
    } finally {
        const button = document.querySelector('.request-btn');
        if (button) {
            button.disabled = false;
            button.innerHTML = '🚨 Request Emergency Ambulance';
        }
    }
};

// Plot route
function plotRoute(routeData, selectedCity, hospitalName, ambulanceId) {
    routeLayer.clearLayers();
    markersLayer.clearLayers();

    const patientLocation = cityCoordinates[selectedCity.toLowerCase()];
    const routeCoords = routeData.map(coord => [coord[0], coord[1]]);
    
    // Create the complete route line
    const routeLine = L.polyline(routeCoords, {
        color: '#e74c3c', 
        weight: 4, 
        opacity: 0.8, 
        dashArray: '10, 5'
    }).addTo(routeLayer);

    // Add markers for key points
    if (routeCoords.length > 0) {
        // Ambulance marker (start of route)
        L.marker(routeCoords[0], { icon: ambulanceIcon })
            .bindPopup(`<b>🚑 Ambulance ${ambulanceId}</b><br>Status: Dispatched`)
            .addTo(markersLayer);

        // Find patient point in route (closest to city center)
        const patientPoint = routeCoords.find(coord => 
            haversine(coord, patientLocation) < 1.0 // within 1km of city center
        ) || routeCoords[Math.floor(routeCoords.length/2)]; // fallback to midpoint

        // Patient marker
        L.marker(patientPoint, { icon: patientIcon })
            .bindPopup(`<b>📍 Patient Location</b><br>City: ${selectedCity}`)
            .addTo(markersLayer);
    }

    // Hospital marker (end of route)
    if (routeCoords.length > 1) {
        L.marker(routeCoords[routeCoords.length - 1], { icon: hospitalIcon })
            .bindPopup(`<b>🏥 ${hospitalName}</b><br>Status: Ready to receive`)
            .addTo(markersLayer);
    }

    // Fit map to show entire route
    const group = new L.featureGroup([routeLine, ...markersLayer.getLayers()]);
    map.fitBounds(group.getBounds().pad(0.1));

    animateRoute(routeLine);
}

// Helper function to calculate distance between coordinates
function haversine(coord1, coord2) {
    const [lat1, lon1] = coord1;
    const [lat2, lon2] = coord2;
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

// Animate route
function animateRoute(routeLine) {
    const originalLatLngs = routeLine.getLatLngs();
    const animatedLatLngs = [];
    let i = 0;

    function addNextPoint() {
        if (i < originalLatLngs.length) {
            animatedLatLngs.push(originalLatLngs[i]);
            routeLine.setLatLngs(animatedLatLngs);
            i++;
            setTimeout(addNextPoint, 100);
        }
    }

    routeLine.setLatLngs([]);
    addNextPoint();
}

// Notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        max-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;

    notification.style.background = type === 'success'
        ? 'linear-gradient(135deg, #00b894, #00a085)'
        : 'linear-gradient(135deg, #e74c3c, #c0392b)';

    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Notification animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
