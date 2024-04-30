
function getBoundsFromRoute(route) {
    let minLat = Infinity;
    let maxLat = -Infinity;
    let minLng = Infinity;
    let maxLng = -Infinity;

    processLocation(route.start);
    route.waypoints.forEach(processLocation);
    processLocation(route.end);

    function processLocation(location) {
        minLat = Math.min(minLat, location.lat);
        maxLat = Math.max(maxLat, location.lat);
        minLng = Math.min(minLng, location.lng);
        maxLng = Math.max(maxLng, location.lng);
    }

    return {
        southwest: { lat: minLat, lng: minLng },
        northeast: { lat: maxLat, lng: maxLng }
    };
}



function getDistance(point1, point2) {
    const R = 6371;
    const dLat = toRadians(point2.lat - point1.lat);
    const dLng = toRadians(point2.lng - point1.lng);
    const lat1 = toRadians(point1.lat);
    const lat2 = toRadians(point2.lat);

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.sin(dLng / 2) * Math.sin(dLng / 2) * Math.cos(lat1) * Math.cos(lat2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c * 1000;
    return distance;
}

function toRadians(degrees) {
    return degrees * Math.PI / 180;
}


function getLastMonth() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    return lastMonth.toISOString().slice(0, 7);
}


module.exports = {
    getBoundsFromRoute,
    getDistance,
    toRadians,
    getLastMonth
};