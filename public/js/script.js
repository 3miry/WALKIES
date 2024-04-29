var map, infoWindow, autocomplete;
var directionsService, directionsRenderer;
var lastSearchedLocation;


function initMap() {
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();

    // Define our dark theme styles
    const darkThemeStyles = [
        {
            "featureType": "all",
            "elementType": "all",
            "stylers": [
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                },
                {
                    "saturation": "-100"
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "saturation": 36
                },
                {
                    "color": "#000000"
                },
                {
                    "lightness": 40
                },
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "visibility": "off"
                },
                {
                    "color": "#000000"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 17
                },
                {
                    "weight": 1.2
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#4d6059"
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#4d6059"
                }
            ]
        },
        {
            "featureType": "landscape.natural",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#4d6059"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [
                {
                    "lightness": 21
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#4d6059"
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#4d6059"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "road",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#7f8d89"
                },
                {
                    "lightness": 17
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#7f8d89"
                },
                {
                    "lightness": 29
                },
                {
                    "weight": 0.2
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 18
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#7f8d89"
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#000000"
                },
                {
                    "lightness": 19
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "all",
            "stylers": [
                {
                    "color": "#2b3638"
                },
                {
                    "visibility": "on"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#2b3638"
                },
                {
                    "lightness": 17
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#24282b"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#24282b"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        }
    ];

    // Initialize the map with the dark theme styles
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: { lat: 54.574227, lng: -1.234956 }, // Default center; update as needed
        styles: darkThemeStyles // Apply the dark theme styles here
    });

    directionsRenderer.setMap(map);
    infoWindow = new google.maps.InfoWindow();


    // Setup autocomplete
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('autocomplete'),
        {types: ['geocode']}
    );
    autocomplete.addListener('place_changed', onPlaceChanged);

    // Event listener for auto-locate button
    document.getElementById('locateMe').addEventListener('click', function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                lastSearchedLocation = pos; // Update last searched location
                map.setCenter(pos);
                infoWindow.setPosition(pos);
                infoWindow.setContent('Location found.');
                infoWindow.open(map);
            }, function() {
                handleLocationError(true, map.getCenter());
            });
        } else {
            // Browser doesn't support Geolocation
            handleLocationError(false, map.getCenter());
        }
    });

    // Event listener for the generate route button
    document.getElementById('generateRoute').addEventListener('click', function() {
        if (lastSearchedLocation) {
            fetchAndDisplayRoute(lastSearchedLocation);
        } else {
            alert("Please enter or detect a location first.");
        }
    });
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();
    if (!place.geometry) {
        window.alert("No details available for input: '" + place.name + "'");
        return;
    }
    lastSearchedLocation = place.geometry.location; // Store the last searched location
    map.setCenter(lastSearchedLocation);
    map.setZoom(17);
}

function fetchAndDisplayRoute(startLocation) {
    const userPreferences = getUserPreferences();
    const routeLength = getSelectedRouteLength();
    fetch('/api/generate-route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ startLocation: startLocation, userPreferences: userPreferences, routeLength: routeLength}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error from server:', data.error);
            alert('Failed to fetch route. Please try again.');
        } else if (!data.route) {
            console.error('Invalid response from server:', data);
            alert('Failed to fetch route. Please try again.');
        } else {
            displayRoute(data.route);
            displayPOIs(data.pois);
        }
    })
    .catch(error => {
        console.error('Error fetching route:', error);
        alert('Failed to fetch route. Please try again.');
    });
}


function getSelectedRouteLength() {
    const routeLengthSelect = document.getElementById('distanceSelect');
    return routeLengthSelect.value;
}

function displayRoute(route) {
    const googleRoute = {
        request: {
            travelMode: 'WALKING',
            origin: new google.maps.LatLng(route.start.lat, route.start.lng),
            destination: new google.maps.LatLng(route.end.lat, route.end.lng),
            waypoints: route.waypoints.map(wp => ({
                location: new google.maps.LatLng(wp.location.lat, wp.location.lng),
                stopover: wp.stopover
            })),
            optimizeWaypoints: true,
            avoidFerries: true,
            avoidHighways: true,
            avoidTolls: true
        }
    };

    
    directionsService.route(googleRoute.request, function(response, status) {
        if (status === 'OK') {
            // Check if a shorter footpath is available between waypoints
            const legs = response.routes[0].legs;
            for (let i = 0; i < legs.length - 1; i++) {
                const startPoint = legs[i].end_location;
                const endPoint = legs[i + 1].start_location;
                const shortestPath = getShortestFootpath(startPoint, endPoint);

                if (shortestPath) {
                    // Replace the leg with the shortest footpath
                    legs[i].steps = shortestPath.steps;
                    legs[i].end_location = shortestPath.end_location;
                    legs[i + 1].start_location = shortestPath.end_location;
                }
            }

            // Render the optimized directions
            directionsRenderer.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}



function getShortestFootpath(startPoint, endPoint) {
    // Implement the logic to find the shortest footpath between two points
    // You can use the Google Maps API or other data sources to calculate distances and durations
    // Return the shortest footpath if found, otherwise return null
    // Example implementation:
    const footpathRequest = {
        origin: startPoint,
        destination: endPoint,
        travelMode: 'WALKING'
    };

    directionsService.route(footpathRequest, function(response, status) {
        if (status === 'OK') {
            const footpath = response.routes[0].legs[0];
            const footpathDistance = footpath.distance.value;
            const originalDistance = google.maps.geometry.spherical.computeDistanceBetween(startPoint, endPoint);

            if (footpathDistance < originalDistance) {
                return footpath;
            }
        }
        return null;
    });
}

function displayPOIs(pois) {
    const featureList = document.getElementById('featureList');
    featureList.innerHTML = ''; // Clear existing POI listings

    pois.forEach(poi => {
        // Create a marker for each POI on the map
        const marker = new google.maps.Marker({
            position: new google.maps.LatLng(poi.location.lat, poi.location.lng),
            map: map,
            title: poi.name
        });

        // Create a list item for each POI in the sidebar
        const listItem = document.createElement('li');
        listItem.textContent = poi.name + ' (' + poi.type + ')';
        featureList.appendChild(listItem);

        // Add click listener to the marker
        marker.addListener('click', () => {
            map.setCenter(marker.getPosition());
            // Optionally, display an info window on marker click
            const infoWindow = new google.maps.InfoWindow({
                content: `<h3>${poi.name}</h3><p>Type: ${poi.type}</p>`
            });
            infoWindow.open(map, marker);
        });

        // Add click listener to the list item to focus map on POI
        listItem.addEventListener('click', () => {
            map.setCenter(marker.getPosition());
            map.setZoom(17); // Adjust zoom level as needed
            // Trigger the marker's click event to open the info window
            google.maps.event.trigger(marker, 'click');
        });
    });
}


function handleLocationError(browserHasGeolocation, pos) {
    console.error(browserHasGeolocation ?
                  'Error: The Geolocation service failed.' :
                  'Error: Your browser doesn\'t support geolocation.');
    map.setCenter(pos);
}

function getUserPreferences() {
    const preferences = [];
    const checkboxes = document.querySelectorAll('input[name="preference"]:checked');
    checkboxes.forEach(checkbox => {
        preferences.push(checkbox.value);
    });
    return preferences;
}

const sidebar = document.getElementById('sidebar');
const toggleButton = document.getElementById('toggleSidebar');

toggleButton.addEventListener('click', function() {
    sidebar.classList.toggle('open');
});