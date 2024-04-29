const express = require('express');
const googleMaps = require('@google/maps').createClient({
    key: 'AIzaSyB3VHxQd2YagSkANqk_xmxBrEjl3DaDoBY',
    Promise: Promise
});


const app = express();
const path = require('path');
const PORT = 3000;
const axios = require('axios');

app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../index.html'));
});

const MINIMUM_SCORE_THRESHOLD = 5;


app.post('/api/generate-route', async (req, res) => {
    const { startLocation, userPreferences, routeLength } = req.body;

    const generatedRoutes = generateMultipleRoutes(startLocation, routeLength);
    const filteredRoutes = [];

    for (const route of generatedRoutes) {
        const score = await scoreRoute(route, userPreferences);
        if (score >= MINIMUM_SCORE_THRESHOLD) {
            filteredRoutes.push({ route, score });
            
        }
    }

    if (filteredRoutes.length === 0) {
        // Handle the case when no routes pass the filtering criteria
        return res.status(200).json({ error: 'No suitable routes found', routes: [] });
    }

    filteredRoutes.sort((a, b) => b.score - a.score);
    console.log('Filtered routes:', filteredRoutes);

    const bestRoute = filteredRoutes[0].route;
    console.log('Best route:', bestRoute);

    const userPreferencesArray = Array.isArray(userPreferences) ? userPreferences : [userPreferences];
    const pois = await fetchPOIs(bestRoute.waypoints, userPreferences);

    
    bestRoute.waypoints = bestRoute.waypoints.map(waypoint => ({
        location: {
            lat: waypoint.lat,
            lng: waypoint.lng
        },
        stopover: true
    }));

    console.log('Best route and POIs:', bestRoute);
    res.json({ route: bestRoute, pois: pois });
});

function generateMultipleRoutes(startLocation, routeLength) {
    const routes = [];

    // Define route length parameters
    const routeLengthParams = {
        short: { minPoints: 3, maxPoints: 5, minRadius: 200, maxRadius: 500 },
        medium: { minPoints: 5, maxPoints: 8, minRadius: 500, maxRadius: 1000 },
        long: { minPoints: 8, maxPoints: 12, minRadius: 1000, maxRadius: 2000 },
    };

    // Get the route length parameters based on user selection
    const { minPoints, maxPoints, minRadius, maxRadius } = routeLengthParams[routeLength];

    // Generate multiple routes with different waypoints and distances
    console.log('Generating routes...');
    for (let i = 0; i < 1; i++) {
        const numberOfPoints = Math.floor(Math.random() * (maxPoints - minPoints + 1)) + minPoints;
        const radius = Math.random() * (maxRadius - minRadius) + minRadius;

        const waypoints = [];
        for (let j = 0; j < numberOfPoints; j++) {
            const angle = Math.random() * 2 * Math.PI;
            const distance = Math.random() * radius;
            const dx = distance * Math.cos(angle);
            const dy = distance * Math.sin(angle);
            const lat = startLocation.lat + (dy / 111320);
            const lng = startLocation.lng + (dx / (40075000 * Math.cos(Math.PI * startLocation.lat / 180) / 360));

            waypoints.push({ lat, lng });
        }

        // Sort the waypoints based on their angle relative to the start location
        waypoints.sort((a, b) => {
            const angleA = Math.atan2(a.lat - startLocation.lat, a.lng - startLocation.lng);
            const angleB = Math.atan2(b.lat - startLocation.lat, b.lng - startLocation.lng);
            return angleA - angleB;
        });

        // Remove large gaps or sharp turns
        const smoothedWaypoints = [waypoints[0]];
        for (let j = 1; j < waypoints.length; j++) {
            const prev = smoothedWaypoints[smoothedWaypoints.length - 1];
            const current = waypoints[j];
            const distance = getDistance(prev, current);
            const angle = Math.atan2(current.lat - prev.lat, current.lng - prev.lng);

            if (distance > radius / 2 || Math.abs(angle) > Math.PI / 2) {
                // Insert intermediate waypoint
                const intermediateLat = (prev.lat + current.lat) / 2;
                const intermediateLng = (prev.lng + current.lng) / 2;
                smoothedWaypoints.push({ lat: intermediateLat, lng: intermediateLng });
            }

            smoothedWaypoints.push(current);
        }

        routes.push({
            start: startLocation,
            end: startLocation,
            waypoints: smoothedWaypoints,
        });
    }
    console.log('Generated routes:', routes);
    return routes;
}

async function scoreRoute(route, userPreferences) {
    console.log('Scoring route...');
    let score = 0;

    for (const preference of userPreferences) {
        if (await routeContainsPOI(route, preference)) {
            console.log(`Route contains POI "${preference}"`);
            score += 10;
        }
    }

    const busyRoads = await checkBusyRoads(route);
    if (busyRoads) {
        console.log('Busy roads found');
        score -= 5;
    }

    const highCrimeAreas = await checkHighCrimeAreas(route);
    if (highCrimeAreas) {
        console.log('High crime areas found');
        score -= 8;
    }


    const poiCount = await countPOIsAlongRoute(route);
    console.log('POI count:', poiCount);
    score += poiCount * 2;

    // Call Python backend for ML predictions
    try {
        // Predict density for each waypoint
        let aggregatePrediction = 0;
        for (const waypoint of route.waypoints) {
            const prediction = await getPrediction(waypoint);
            aggregatePrediction += prediction;
        }
        const averagePrediction = aggregatePrediction / route.waypoints.length;

        console.log('Average prediction density:', averagePrediction);
        // Penalize routes with high average prediction densities
        if (averagePrediction > 0.5) {
            score -= 20;  
        }

    } catch (error) {
        console.error('Error incorporating ML predictions:', error);
    }

    console.log('Final route score:', score);
    return score;
}

async function fetchPOIs(waypoints, userPreferences) {
    const pois = [];
    console.log('Fetching POIs...');

    try {
        const placeTypes = userPreferences.length > 0 ? userPreferences.join('|') : 'park|museum|cafe|restaurant|art_gallery|shopping_mall|tourist_attraction';

        const placesPromises = waypoints.map(waypoint =>
            googleMaps.placesNearby({
                location: [waypoint.lat, waypoint.lng],
                radius: 500,
                type: placeTypes,
            }).asPromise()
        );

        const placesResults = await Promise.all(placesPromises);
        placesResults.forEach(result => {
            if (result.json.results) {
                result.json.results.forEach(place => {
                    pois.push({
                        name: place.name,
                        type: place.types ? place.types[0] : 'unknown',
                        location: { lat: place.geometry.location.lat, lng: place.geometry.location.lng }
                    });
                });
            }
        });
    } catch (error) {
        console.error('Failed to fetch POIs:', error);
    }

    console.log('Fetched POIs:', pois);
    return pois;
}

async function routeContainsPOI(route, userPreferences) {
    console.log('Checking for POIs along route...');

    try {
        const placeTypes = userPreferences.length > 0 ? userPreferences.join('|') : 'park|museum|cafe|restaurant|art_gallery|shopping_mall|tourist_attraction';

        const response = await googleMaps.places({
            query: placeTypes,
            bounds: getBoundsFromRoute(route)
        }).asPromise();

        return response.json.results.length > 0;
    } catch (error) {
        console.error('Failed to check POIs along route:', error);
        return false;
    }
}

async function routeContainsPOI(route, poiType) {
    console.log(`Checking for POI "${poiType}" along route...`);
    try {
        const response = await googleMaps.places({
            query: poiType,
            bounds: getBoundsFromRoute(route)
        }).asPromise();

        return response.json.results.length > 0;
    } catch (error) {
        console.error(`Failed to check POI "${poiType}" along route:`, error);
        return false;
    }
}

async function checkBusyRoads(route) {
    console.log('Checking busy roads along route...');
    try {
        const response = await googleMaps.directions({
            origin: route.start,
            destination: route.end,
            waypoints: route.waypoints.map(waypoint => ({
                location: waypoint,
                stopover: true
            })),
            optimize: true
        }).asPromise();

        if (response.json.routes && response.json.routes.length > 0) {
            const legs = response.json.routes[0].legs;
            for (const leg of legs) {
                for (const step of leg.steps) {
                    if (step.duration_in_traffic && step.duration_in_traffic.value > step.duration.value * 1.5) {
                        console.log('Busy road found:', step);
                        return true;
                    }
                }
            }
        }
        console.log('No busy roads found');
        return false;
    } catch (error) {
        console.error('Failed to check busy roads:', error);
        return false;
    }
}

async function countPOIsAlongRoute(route) {
    console.log('Counting POIs along route...');
    try {
        const center = getRouteCenter(route);
        const radius = getRouteRadius(route, center);

        if (radius === 0) {
            console.warn('Route radius is 0. Skipping POI count.');
            return 0;
        }

        const response = await googleMaps.placesNearby({
            location: center,
            radius: radius,
            type: 'point_of_interest'
        }).asPromise();

        return response.json.results.length;
    } catch (error) {
        console.error('Failed to count POIs along route:', error);
        return 0;
    }
}

function getBoundsFromRoute(route) {
    console.log('Calculating bounds from route...');
    let minLat = Infinity;
    let maxLat = -Infinity;
    let minLng = Infinity;
    let maxLng = -Infinity;

    // Process the start location
    minLat = Math.min(minLat, route.start.lat);
    maxLat = Math.max(maxLat, route.start.lat);
    minLng = Math.min(minLng, route.start.lng);
    maxLng = Math.max(maxLng, route.start.lng);

    // Process each waypoint
    route.waypoints.forEach(waypoint => {
        minLat = Math.min(minLat, waypoint.lat);
        maxLat = Math.max(maxLat, waypoint.lat);
        minLng = Math.min(minLng, waypoint.lng);
        maxLng = Math.max(maxLng, waypoint.lng);
    });

    // Process the end location
    minLat = Math.min(minLat, route.end.lat);
    maxLat = Math.max(maxLat, route.end.lat);
    minLng = Math.min(minLng, route.end.lng);
    maxLng = Math.max(maxLng, route.end.lng);

    return {
        southwest: { lat: minLat, lng: minLng },
        northeast: { lat: maxLat, lng: maxLng }
    };
}



function getRouteCenter(route) {
    console.log('Calculating center of route...');
    const { start, end } = route;
    const centerLat = (start.lat + end.lat) / 2;
    const centerLng = (start.lng + end.lng) / 2;
    return { lat: centerLat, lng: centerLng };
}

function getRouteRadius(route, center) {
    console.log('Calculating radius of route...');
    const { start, end } = route;
    const startDistance = getDistance(start, center);
    const endDistance = getDistance(end, center);
    const radius = Math.max(startDistance, endDistance);
    return radius > 0 ? radius : 5000; // Set a default radius of 5000 meters if the calculated radius is 0
}

function getDistance(point1, point2) {
    console.log('Calculating distance between two points...');
    const R = 6371; // Earth's radius in kilometers
    const dLat = toRadians(point2.lat - point1.lat);
    const dLng = toRadians(point2.lng - point1.lng);
    const lat1 = toRadians(point1.lat);
    const lat2 = toRadians(point2.lat);

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.sin(dLng / 2) * Math.sin(dLng / 2) * Math.cos(lat1) * Math.cos(lat2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c * 1000; // Convert to meters
    return distance;
}

function toRadians(degrees) {
    console.log('Converting degrees to radians...');
    return degrees * Math.PI / 180;
}

async function checkHighCrimeAreas(route) {
    console.log('Checking for high crime areas along route...');
    const CRIME_THRESHOLD = 10;
    const MAX_RETRIES = 3;
    const INITIAL_DELAY = 1000; // Initial delay in milliseconds

    const retryRequest = async (retries, delay) => {
        try {
            const crimePromises = route.waypoints.map(async (waypoint) => {
                const response = await axios.get('https://data.police.uk/api/crimes-street/all-crime', {
                    params: {
                        lat: waypoint.lat,
                        lng: waypoint.lng,
                        date: getLastMonth(),
                    }
                });
                console.log(`Crimes at ${waypoint.lat},${waypoint.lng}:`, response.data.length);
                return response.data.length;
            });

            const crimeCountArray = await Promise.all(crimePromises);
            const totalCrimes = crimeCountArray.reduce((sum, count) => sum + count, 0);

            return totalCrimes > CRIME_THRESHOLD;
        } catch (error) {
            if (error.response && error.response.status === 429 && retries < MAX_RETRIES) {
                console.log(`Rate limited. Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                return retryRequest(retries + 1, delay * 2);
            } else {
                console.error('Failed to check high crime areas:', error);
                return false;
            }
        }
    };
    console.log('Fetching crime data...');
    return retryRequest(0, INITIAL_DELAY);
}
function getLastMonth() {
    console.log('Getting last month...');
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    return lastMonth.toISOString().slice(0, 7);
}


// Function to fetch weather data
async function fetchWeather(apiKey, latitude, longitude, datetime) {
    const url = `https://api.weatherapi.com/v1/history.json?key=${apiKey}&q=${latitude},${longitude}&dt=${datetime}`;
    try {
      const response = await axios.get(url);
      return response.data;  // Extract and format this data as needed
    } catch (error) {
      console.error('Error fetching weather data:', error);
      return {};
    }
  }
  
// Function to call the prediction endpoint
async function getPrediction(waypoint) {
    try {
        const weatherData = await fetchWeather('a1552cda7bab471a91e230830231312', waypoint.latitude, waypoint.longitude, waypoint.datetime);
        const formattedWaypoint = {
            longitude: waypoint.lng,
            latitude: waypoint.lat,
            datetime: waypoint.datetime,
            day_of_week: waypoint.day_of_week,
            sex_of_casualty: waypoint.sex_of_casualty,
            age_band_of_casualty: waypoint.age_band_of_casualty,
            weather: weatherData.condition,
            season: waypoint.season,
            time_of_day: waypoint.time_of_day
        };
        const response = await axios.post('http://localhost:5000/predict', formattedWaypoint);
        return response.data.prediction;
    } catch (error) {
        console.error('Error fetching prediction:', error);
        return null;
    }
}


app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
}); 