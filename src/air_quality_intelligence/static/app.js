async function searchAirQuality() {

    const cityInput =
        document.getElementById("cityInput");

    const city =
        cityInput.value.trim();

    const dashboard =
        document.getElementById("dashboard");

    const loading =
        document.getElementById("loading");

    const error =
        document.getElementById("error");

    if (!city) {
        showError("Please enter a city name.");
        return;
    }

    dashboard.classList.add("hidden");
    error.classList.add("hidden");
    loading.classList.remove("hidden");

    try {

        const response =
            await fetch(
                `/api/air-quality/${encodeURIComponent(city)}`
            );

        const data =
            await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Unable to retrieve air-quality data."
            );
        }

        displayAirQuality(data);

    } catch (err) {

        showError(err.message);

    } finally {

        loading.classList.add("hidden");

    }
}


function displayAirQuality(data) {

    const dashboard =
        document.getElementById("dashboard");

    dashboard.classList.remove("hidden");


    document.getElementById("cityName")
        .textContent =
        data.requested_city ||
        data.place ||
        "-";


    const location =
        data.location || {};


    document.getElementById("locationDetails")
        .textContent =
        `${location.state || ""}, ` +
        `${location.country || ""}`;


    document.getElementById("aqiValue")
        .textContent =
        data.aqi ?? "--";


    document.getElementById("aqiCategory")
        .textContent =
        data.category || "--";


    const pollutantAQI =
        data.pollutant_aqi || {};


    document.getElementById("pm25")
        .textContent =
        pollutantAQI["pm2.5"] ?? "--";


    document.getElementById("pm10")
        .textContent =
        pollutantAQI["pm10"] ?? "--";


    document.getElementById("ozone")
        .textContent =
        pollutantAQI["ozone"] ?? "--";


    document.getElementById("no2")
        .textContent =
        pollutantAQI["nitrogen_dioxide"] ?? "--";


    document.getElementById("dominantPollutant")
        .textContent =
        data.dominant_pollutant || "--";


    document.getElementById("dataSource")
        .textContent =
        data.source || "--";


    document.getElementById("recommendation")
        .textContent =
        data.recommendation || "--";


    displayCurrentData(data.current);

}


function displayCurrentData(current) {

    const container =
        document.getElementById("currentData");

    if (!current) {
        container.innerHTML =
            "<p>No current measurements available.</p>";

        return;
    }


    const measurements = [
        ["PM2.5", current.pm2_5],
        ["PM10", current.pm10],
        ["Carbon Monoxide", current.carbon_monoxide],
        ["Nitrogen Dioxide", current.nitrogen_dioxide],
        ["Sulphur Dioxide", current.sulphur_dioxide],
        ["Ozone", current.ozone]
    ];


    container.innerHTML =
        measurements.map(
            ([name, value]) => `
                <div class="measurement">
                    <span>${name}</span>
                    <strong>
                        ${value ?? "--"}
                    </strong>
                </div>
            `
        ).join("");

}


function showError(message) {

    const error =
        document.getElementById("error");

    error.textContent = message;

    error.classList.remove("hidden");
}


document
    .getElementById("cityInput")
    .addEventListener(
        "keypress",
        function (event) {

            if (event.key === "Enter") {
                searchAirQuality();
            }

        }
    );