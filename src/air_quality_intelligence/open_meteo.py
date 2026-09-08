import requests


class OpenMeteoService:
    """Get location and air-quality data from Open-Meteo."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def search_location(self, place):
        """Find a location and return its coordinates."""

        params = {
            "name": place,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        response = requests.get(
            self.GEOCODING_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return None

        location = data["results"][0]

        return {
            "name": location.get("name"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "country": location.get("country"),
            "state": location.get("admin1"),
            "timezone": location.get("timezone"),
        }

    def get_air_quality(self, latitude, longitude):
        """Get current and hourly air-quality data."""

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "european_aqi,"
                "us_aqi,"
                "us_aqi_pm2_5,"
                "us_aqi_pm10,"
                "us_aqi_nitrogen_dioxide,"
                "us_aqi_ozone,"
                "us_aqi_sulphur_dioxide,"
                "us_aqi_carbon_monoxide,"
                "pm2_5,"
                "pm10,"
                "carbon_monoxide,"
                "nitrogen_dioxide,"
                "sulphur_dioxide,"
                "ozone"
            ),
            "hourly": (
                "pm2_5,"
                "pm10,"
                "carbon_monoxide,"
                "nitrogen_dioxide,"
                "sulphur_dioxide,"
                "ozone"
            ),
            "forecast_days": 5,
            "timezone": "auto",
        }

        response = requests.get(
            self.AIR_QUALITY_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def get_place_air_quality(self, place):
        """Find a place and retrieve its air quality."""

        location = self.search_location(place)

        if location is None:
            return {
                "status": "Location not found",
                "place": place,
            }

        air_quality = self.get_air_quality(
            location["latitude"],
            location["longitude"],
        )

        return {
            "status": "success",
            "location": location,
            "air_quality": air_quality,
        }

    def analyze_place(self, place, analyzer):
        """Get air quality and generate an intelligence report."""

        result = self.get_place_air_quality(place)

        if result["status"] != "success":
            return result

        current = result["air_quality"].get("current", {})

        aqi = current.get("us_aqi")

        analysis = analyzer.analyze(aqi)

        pollutant_aqi = {
            "pm2.5": current.get("us_aqi_pm2_5"),
            "pm10": current.get("us_aqi_pm10"),
            "nitrogen_dioxide": current.get(
                "us_aqi_nitrogen_dioxide"
            ),
            "ozone": current.get("us_aqi_ozone"),
            "sulphur_dioxide": current.get(
                "us_aqi_sulphur_dioxide"
            ),
            "carbon_monoxide": current.get(
                "us_aqi_carbon_monoxide"
            ),
        }

        valid_pollutants = {
            name: value
            for name, value in pollutant_aqi.items()
            if value is not None
        }

        dominant_pollutant = None

        if valid_pollutants:
            dominant_pollutant = max(
                valid_pollutants,
                key=valid_pollutants.get,
            )

        return {
            "status": "success",
            "place": place,
            "location": result["location"],
            "source": "Open-Meteo",
            "source_type": "Model-based air quality",
            "aqi_standard": "US AQI",
            "aqi": aqi,
            "category": analysis["category"],
            "recommendation": analysis["recommendation"],
            "dominant_pollutant": dominant_pollutant,
            "pollutant_aqi": pollutant_aqi,
            "current": current,
            "hourly": result["air_quality"].get("hourly", {}),
        }