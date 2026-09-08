class AirQualityAnalyzer:
    """Analyze AQI values and provide air-quality insights."""

    def classify_aqi(self, aqi):
        """Classify an AQI value into a standard category."""

        if aqi is None:
            return "Unknown"

        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    def get_recommendation(self, category):
        """Provide a recommendation based on the AQI category."""

        recommendations = {
            "Good": (
                "Air quality is good. "
                "Outdoor activities are generally safe."
            ),
            "Moderate": (
                "Air quality is acceptable. "
                "Sensitive people should take care."
            ),
            "Unhealthy for Sensitive Groups": (
                "Sensitive people should reduce prolonged "
                "outdoor activity."
            ),
            "Unhealthy": (
                "Consider reducing outdoor activity "
                "and prolonged exposure."
            ),
            "Very Unhealthy": (
                "Avoid prolonged outdoor activity "
                "and consider staying indoors."
            ),
            "Hazardous": (
                "Avoid outdoor exposure as much as possible."
            ),
            "Unknown": (
                "AQI information is not available."
            )
        }

        return recommendations.get(
            category,
            "No recommendation available."
        )

    def analyze(self, aqi):
        """Analyze a single AQI value."""

        category = self.classify_aqi(aqi)

        return {
            "aqi": aqi,
            "category": category,
            "recommendation": self.get_recommendation(category)
        }

    def analyze_air_data(self, air_data):
        """Create an intelligence report from air-quality data."""

        if not air_data:
            return {
                "status": "No data",
                "message": "Air quality data is not available."
            }

        aqi = air_data.get("aqi")
        category = self.classify_aqi(aqi)

        return {
            "status": "success",
            "aqi": aqi,
            "category": category,
            "dominant_pollutant": air_data.get(
                "dominant_pollutant"
            ),
            "city": air_data.get("city"),
            "station": air_data.get("station"),
            "recommendation": self.get_recommendation(category)
        }