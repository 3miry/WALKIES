const axios = require('axios');
const { routeContainsPOI, countPOIsAlongRoute } = require('./pois');
const { fetchWeather } = require('./externalApis');
const googleMaps = require('@google/maps').createClient({
    key: 'AIzaSyB3VHxQd2YagSkANqk_xmxBrEjl3DaDoBY',
    Promise: Promise
});
const { fetchCrimeData } = require('./externalApis');


async function scoreRoute(route, userPreferences) {
    let score = 0;

    for (const preference of userPreferences) {
        if (await routeContainsPOI(route, preference)) {
            score += 10;
        }
    }

    const busyRoads = await checkBusyRoads(route);
    if (busyRoads) {
        score -= 5;
    }

    const highCrimeAreas = await checkHighCrimeAreas(route);
    if (highCrimeAreas) {
        score -= 8;
    }

    const poiCount = await countPOIsAlongRoute(route);
    score += poiCount * 2;

    try {
        let aggregatePrediction = 0;
        for (const waypoint of route.waypoints) {
            const prediction = await getPrediction(waypoint);
            aggregatePrediction += prediction;
        }
        const averagePrediction = aggregatePrediction / route.waypoints.length;

        if (averagePrediction > 0.5) {
            score -= 20;  
        }
    } catch (error) {
        console.error('Error incorporating ML predictions:', error);
    }

    return score;
}



async function checkBusyRoads(route) {
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
                        return true;
                    }
                }
            }
        }
        return false;
    } catch (error) {
        console.error('Failed to check busy roads:', error);
        return false;
    }
}


async function checkHighCrimeAreas(route) {
    const CRIME_THRESHOLD = 10;
    const MAX_RETRIES = 3;
    const INITIAL_DELAY = 1000;

    const retryRequest = async (retries, delay) => {
        try {
            const crimePromises = route.waypoints.map(fetchCrimeData);
            const crimeCountArray = await Promise.all(crimePromises);
            const totalCrimes = crimeCountArray.reduce((sum, count) => sum + count, 0);

            return totalCrimes > CRIME_THRESHOLD;
        } catch (error) {
            if (error.response && error.response.status === 429 && retries < MAX_RETRIES) {
                await new Promise(resolve => setTimeout(resolve, delay));
                return retryRequest(retries + 1, delay * 2);
            } else {
                console.error('Failed to check high crime areas:', error);
                return false;
            }
        }
    };

    return retryRequest(0, INITIAL_DELAY);
}


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

module.exports = {
    scoreRoute,
    checkBusyRoads,
    checkHighCrimeAreas,
    getPrediction
};
