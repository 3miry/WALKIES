const axios = require('axios');

function fetchCrimeData(waypoint) {
    return axios.get('https://data.police.uk/api/crimes-street/all-crime', {
        params: {
            lat: waypoint.lat,
            lng: waypoint.lng,
            date: getLastMonth(),
        }
    }).then(response => response.data.length);
}

async function fetchWeather(apiKey, latitude, longitude, datetime) {
    const url = `https://api.weatherapi.com/v1/history.json?key=${apiKey}&q=${latitude},${longitude}&dt=${datetime}`;
    try {
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error('Error fetching weather data:', error);
        return {};
    }
}

module.exports = {
    fetchWeather,
    fetchCrimeData
};