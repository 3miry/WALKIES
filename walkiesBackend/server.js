const express = require('express');
const { generateMultipleRoutes } = require('./routes');
const { scoreRoute } = require('./scoring');
const { fetchPOIs, routeContainsPOI, countPOIsAlongRoute } = require('./pois');
const { fetchWeather, fetchCrimeData } = require('./externalApis');
const { getBoundsFromRoute, getDistance, toRadians, getLastMonth } = require('./utils');


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
    const { startLocation, userPreferences, routeLength, userSex = 'Female', userAgeBand = '26-35', plannedTime = new Date() } = req.body;

    const generatedRoutes = generateMultipleRoutes(startLocation, routeLength);
    const filteredRoutes = [];

    for (const route of generatedRoutes) {
        const score = await scoreRoute(route, userPreferences);
        if (score >= MINIMUM_SCORE_THRESHOLD) {
            filteredRoutes.push({ route, score });
        }
    }

    if (filteredRoutes.length === 0) {
        return res.status(200).json({ error: 'No suitable routes found', routes: [] });
    }

    filteredRoutes.sort((a, b) => b.score - a.score);

    const bestRoute = filteredRoutes[0].route;
    bestRoute.waypoints = bestRoute.waypoints.map(waypoint => ({
        location: {
            lat: waypoint.lat,
            lng: waypoint.lng
        },
        stopover: true
    }));

    const pois = await fetchPOIs(bestRoute.waypoints, userPreferences);

    res.json({ route: bestRoute, pois: pois });
});




app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});