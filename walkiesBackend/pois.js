const { getBoundsFromRoute } = require('./utils');
const googleMaps = require('@google/maps').createClient({
    key: 'AIzaSyB3VHxQd2YagSkANqk_xmxBrEjl3DaDoBY',
    Promise: Promise
});
const { getRouteCenter, getRouteRadius } = require('./routes');

async function fetchPOIs(waypoints, userPreferences) {
    const pois = [];

    try {
        const placeTypes = userPreferences.length > 0 ? userPreferences.join('|') : 'park|museum|cafe|restaurant|art_gallery|shopping_mall|tourist_attraction';

        const placesPromises = waypoints.map(fetchPlacesNearby(placeTypes));
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

    return pois;
}


function fetchPlacesNearby(placeTypes) {
    return waypoint => {
        if (!waypoint || !waypoint.lat || !waypoint.lng) {
            console.warn('Invalid waypoint:', waypoint);
            return Promise.resolve({ json: { results: [] } });
        }
        return googleMaps.placesNearby({
            location: [waypoint.lat, waypoint.lng],
            radius: 500,
            type: placeTypes,
        }).asPromise();
    };
}

async function routeContainsPOI(route, poiType) {
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


async function countPOIsAlongRoute(route) {
    try {
        const center = getRouteCenter(route);
        const radius = getRouteRadius(route, center);

        if (radius === 0) {
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

module.exports = {
    fetchPOIs,
    fetchPlacesNearby,
    routeContainsPOI,
    countPOIsAlongRoute
};