import requests


class OpenMeteoService:
    """Get location, weather, and air-quality data from Open-Meteo."""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

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
                "ozone,"
                "us_aqi"
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

    def get_weather(self, latitude, longitude):
        """Get current weather and hourly forecast."""

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "wind_speed_10m,"
                "wind_direction_10m,"
                "weather_code"
            ),
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "forecast_days": 5,
            "timezone": "auto",
        }

        response = requests.get(
            self.WEATHER_URL,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def get_place_air_quality(self, place):
        """Find a place and retrieve air-quality data."""

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

    def get_place_weather(self, place):
        """Find a place and retrieve weather data."""

        location = self.search_location(place)

        if location is None:
            return {
                "status": "Location not found",
                "place": place,
            }

        weather = self.get_weather(
            location["latitude"],
            location["longitude"],
        )

        return {
            "status": "success",
            "location": location,
            "weather": weather,
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
            "nitrogen_dioxide": current.get("us_aqi_nitrogen_dioxide"),
            "ozone": current.get("us_aqi_ozone"),
            "sulphur_dioxide": current.get("us_aqi_sulphur_dioxide"),
            "carbon_monoxide": current.get("us_aqi_carbon_monoxide"),
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

    def analyze_place_with_weather(self, place, analyzer):
        """Get air quality, weather, and forecast data."""

        air_result = self.analyze_place(place, analyzer)

        if air_result["status"] != "success":
            return air_result

        location = air_result["location"]

        weather_result = self.get_weather(
            location["latitude"],
            location["longitude"],
        )

        weather_current = weather_result.get("current", {})

        weather_hourly = weather_result.get("hourly", {})

        air_hourly = air_result.get("hourly", {})

        forecast = self.build_forecast(air_hourly, analyzer)

        forecast_analysis = self.analyze_forecast(
            air_result["aqi"],
            forecast,
        )

        air_result["weather"] = {
            "current": weather_current,
            "hourly": weather_hourly,
        }

        air_result["forecast"] = forecast

        air_result["forecast_analysis"] = forecast_analysis

        return air_result

    def build_forecast(self, hourly, analyzer):
        """Build an AQI forecast for the next 24 hours."""

        times = hourly.get("time", [])

        aqi_values = hourly.get("us_aqi", [])

        forecast = []

        limit = min(24, len(times), len(aqi_values))

        for index in range(limit):

            aqi = aqi_values[index]

            if aqi is None:
                continue

            category = analyzer.classify_aqi(aqi)

            forecast.append({
                "time": times[index],
                "aqi": aqi,
                "category": category,
            })

        return forecast

    def analyze_forecast(self, current_aqi, forecast):
        """Analyze AQI changes over the next 24 hours."""

        if current_aqi is None or not forecast:
            return {
                "status": "No forecast data",
                "message": "AQI forecast information is not available.",
            }

        forecast_values = [
            item["aqi"]
            for item in forecast
            if item.get("aqi") is not None
        ]

        if not forecast_values:
            return {
                "status": "No forecast data",
                "message": "AQI forecast information is not available.",
            }

        maximum_aqi = max(forecast_values)

        minimum_aqi = min(forecast_values)

        final_aqi = forecast_values[-1]

        change = final_aqi - current_aqi

        percentage_change = 0

        if current_aqi != 0:
            percentage_change = (change / current_aqi) * 100

        if change >= 10:
            trend = "Increasing"
            alert = (
                "Air quality is expected to deteriorate during the "
                "next 24 hours."
            )
        elif change <= -10:
            trend = "Improving"
            alert = (
                "Air quality is expected to improve during the "
                "next 24 hours."
            )
        else:
            trend = "Stable"
            alert = (
                "Air quality is expected to remain relatively stable "
                "during the next 24 hours."
            )

        peak_item = max(forecast, key=lambda item: item["aqi"])

        return {
            "status": "success",
            "current_aqi": current_aqi,
            "forecast_aqi": final_aqi,
            "maximum_aqi": maximum_aqi,
            "minimum_aqi": minimum_aqi,
            "change": round(change, 1),
            "percentage_change": round(percentage_change, 1),
            "trend": trend,
            "alert": alert,
            "peak_time": peak_item["time"],
            "peak_aqi": peak_item["aqi"],
            "peak_category": peak_item["category"],
        }