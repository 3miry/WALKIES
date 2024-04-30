const { getDistance } = require('./utils');



function generateMultipleRoutes(startLocation, routeLength) {
    const routes = [];
    const routeLengthParams = {
        short: { minPoints: 3, maxPoints: 5, minRadius: 200, maxRadius: 500 },
        medium: { minPoints: 5, maxPoints: 8, minRadius: 500, maxRadius: 1000 },
        long: { minPoints: 8, maxPoints: 12, minRadius: 1000, maxRadius: 2000 },
    };
    const { minPoints, maxPoints, minRadius, maxRadius } = routeLengthParams[routeLength];

    for (let i = 0; i < 5; i++) {
        const numberOfPoints = Math.floor(Math.random() * (maxPoints - minPoints + 1)) + minPoints;
        const radius = Math.random() * (maxRadius - minRadius) + minRadius;
        const waypoints = generateWaypoints(startLocation, numberOfPoints, radius);
        const smoothedWaypoints = smoothWaypoints(waypoints, startLocation, radius);

        routes.push({
            start: startLocation,
            end: startLocation,
            waypoints: smoothedWaypoints,
        });
    }

    return routes;
}

function generateWaypoints(startLocation, numberOfPoints, radius) {
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
    return waypoints;
}



function smoothWaypoints(waypoints, startLocation, radius) {
    waypoints.sort((a, b) => {
        const angleA = Math.atan2(a.lat - startLocation.lat, a.lng - startLocation.lng);
        const angleB = Math.atan2(b.lat - startLocation.lat, b.lng - startLocation.lng);
        return angleA - angleB;
    });

    const smoothedWaypoints = [waypoints[0]];
    for (let j = 1; j < waypoints.length; j++) {
        const prev = smoothedWaypoints[smoothedWaypoints.length - 1];
        const current = waypoints[j];
        const distance = getDistance(prev, current);
        const angle = Math.atan2(current.lat - prev.lat, current.lng - prev.lng);

        if (distance > radius / 2 || Math.abs(angle) > Math.PI / 2) {
            const intermediateLat = (prev.lat + current.lat) / 2;
            const intermediateLng = (prev.lng + current.lng) / 2;
            smoothedWaypoints.push({ lat: intermediateLat, lng: intermediateLng });
        }

        smoothedWaypoints.push(current);
    }

    return smoothedWaypoints;
}


function getRouteCenter(route) {
    const { start, end } = route;
    const centerLat = (start.lat + end.lat) / 2;
    const centerLng = (start.lng + end.lng) / 2;
    return { lat: centerLat, lng: centerLng };
}

function getRouteRadius(route, center) {
    const { start, end } = route;
    const startDistance = getDistance(start, center);
    const endDistance = getDistance(end, center);
    const radius = Math.max(startDistance, endDistance);
    return radius > 0 ? radius : 5000;
}

module.exports = {
    generateMultipleRoutes,
    generateWaypoints,
    smoothWaypoints,
    getRouteCenter,
    getRouteRadius
};