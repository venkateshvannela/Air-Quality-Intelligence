const searchInput = document.getElementById("cityInput");
const searchButton = document.getElementById("searchButton");

let pm25Chart = null;
let pm10Chart = null;
let ozoneChart = null;
let forecastChart = null;

async function loadAirQuality() {
    const city = searchInput.value.trim();

    if (!city) {
        showError("Please enter a city name.");
        return;
    }

    showLoading(true);
    hideError();

    try {
        const response = await fetch(
            `/api/air-quality/${encodeURIComponent(city)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to fetch air-quality data."
            );
        }

        updateDashboard(data);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

function updateDashboard(data) {
    document.getElementById("cityName").textContent =
        data.requested_city || data.city || "Unknown";

    document.getElementById("aqiValue").textContent =
        data.aqi ?? "--";

    document.getElementById("aqiCategory").textContent =
        data.category || "Unknown";

    document.getElementById("dominantPollutant").textContent =
        formatPollutant(data.dominant_pollutant);

    document.getElementById("source").textContent =
        data.source || "Unknown";

    document.getElementById("recommendation").textContent =
        data.recommendation || "No recommendation available.";

    updateAQIIndicator(data.aqi);
    updateCurrentMeasurements(data);
    updateForecast(data);
    updateWeather(data);
    updateCharts(data);
}

function updateCurrentMeasurements(data) {
    const current = data.current || {};

    const measurements = {
        currentPM25: current.pm25,
        currentPM10: current.pm10,
        currentOzone: current.o3,
        currentCO: current.co,
        currentNO2: current.no2,
        currentSO2: current.so2
    };

    Object.entries(measurements).forEach(([id, value]) => {
        const element = document.getElementById(id);

        if (element) {
            element.textContent =
                value !== undefined && value !== null
                    ? value
                    : "--";
        }
    });
}

function updateWeather(data) {
    const weather = data.weather?.current;

    if (!weather) {
        return;
    }

    setText("temperature", weather.temperature_2m, " °C");
    setText("feelsLike", weather.apparent_temperature, " °C");
    setText("humidity", weather.relative_humidity_2m, " %");
    setText("windSpeed", weather.wind_speed_10m, " km/h");
    setText("windDirection", weather.wind_direction_10m, "°");

    const weatherElement = document.getElementById("weatherDescription");

    if (weatherElement) {
        weatherElement.textContent =
            getWeatherDescription(weather.weather_code);
    }
}

function updateForecast(data) {
    const forecast = data.forecast_analysis;

    if (!forecast) {
        return;
    }

    setText("forecastAQI", forecast.forecast_aqi);
    setText("minimumAQI", forecast.minimum_aqi);
    setText("maximumAQI", forecast.maximum_aqi);
    setText("aqiChange", forecast.change);
    setText("aqiPercentage", forecast.percentage_change, " %");

    const trendElement = document.getElementById("forecastTrend");

    if (trendElement) {
        trendElement.textContent = forecast.trend || "Unknown";
    }

    const alertElement = document.getElementById("forecastAlert");

    if (alertElement) {
        alertElement.textContent = forecast.alert || "No forecast alert.";
    }

    const peakTimeElement = document.getElementById("peakTime");

    if (peakTimeElement) {
        peakTimeElement.textContent = formatDateTime(forecast.peak_time);
    }

    setText("peakAQI", forecast.peak_aqi);
    setText("peakCategory", forecast.peak_category);

    updateForecastChart(data);
}

function updateForecastChart(data) {
    const hourly = data.hourly || {};
    const times = hourly.time || [];
    const values = hourly.us_aqi || hourly.european_aqi || [];

    const canvas = document.getElementById("forecastChart");

    if (!canvas || !times.length || !values.length) {
        return;
    }

    if (forecastChart) {
        forecastChart.destroy();
    }

    const limitedTimes = times.slice(0, 24);
    const limitedValues = values.slice(0, 24);

    forecastChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: limitedTimes.map(formatTime),
            datasets: [
                {
                    label: "AQI Forecast",
                    data: limitedValues,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 200
                }
            }
        }
    });
}

function updateCharts(data) {
    const hourly = data.hourly || {};
    const times = hourly.time || [];

    if (!times.length) {
        return;
    }

    const labels = times.slice(0, 24).map(formatTime);

    createPollutantChart(
        "pm25Chart",
        pm25Chart,
        "PM2.5",
        labels,
        (hourly.pm25 || []).slice(0, 24),
        chart => {
            pm25Chart = chart;
        }
    );

    createPollutantChart(
        "pm10Chart",
        pm10Chart,
        "PM10",
        labels,
        (hourly.pm10 || []).slice(0, 24),
        chart => {
            pm10Chart = chart;
        }
    );

    createPollutantChart(
        "ozoneChart",
        ozoneChart,
        "Ozone",
        labels,
        (hourly.o3 || []).slice(0, 24),
        chart => {
            ozoneChart = chart;
        }
    );
}

function createPollutantChart(
    canvasId,
    existingChart,
    label,
    labels,
    values,
    saveChart
) {
    const canvas = document.getElementById(canvasId);

    if (!canvas || !values.length) {
        return;
    }

    if (existingChart) {
        existingChart.destroy();
    }

    const chart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: label,
                    data: values,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    saveChart(chart);
}

function updateAQIIndicator(aqi) {
    const indicator = document.getElementById("aqiIndicator");

    if (!indicator || aqi === null || aqi === undefined) {
        return;
    }

    const numericAQI = Number(aqi);

    if (Number.isNaN(numericAQI)) {
        return;
    }

    const percentage = Math.max(0, Math.min(numericAQI, 500)) / 5;

    indicator.style.left = `${percentage}%`;
}

function setText(id, value, suffix = "") {
    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    if (value === undefined || value === null) {
        element.textContent = "--";
        return;
    }

    element.textContent = `${value}${suffix}`;
}

function formatPollutant(value) {
    if (!value) {
        return "Unknown";
    }

    const names = {
        pm25: "PM2.5",
        "pm2.5": "PM2.5",
        pm10: "PM10",
        o3: "Ozone",
        co: "Carbon Monoxide",
        no2: "Nitrogen Dioxide",
        so2: "Sulfur Dioxide"
    };

    return names[value.toLowerCase()] || value;
}

function formatTime(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function formatDateTime(value) {
    if (!value) {
        return "--";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString([], {
        dateStyle: "medium",
        timeStyle: "short"
    });
}

function getWeatherDescription(code) {
    const descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    };

    return descriptions[code] || "Unknown weather";
}

function showLoading(show) {
    const loading = document.getElementById("loading");

    if (loading) {
        loading.style.display = show ? "block" : "none";
    }
}

function showError(message) {
    const error = document.getElementById("error");

    if (error) {
        error.textContent = message;
        error.style.display = "block";
    }
}

function hideError() {
    const error = document.getElementById("error");

    if (error) {
        error.style.display = "none";
    }
}

searchButton.addEventListener("click", loadAirQuality);

searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        loadAirQuality();
    }
});

window.addEventListener("DOMContentLoaded", () => {
    loadAirQuality();
});