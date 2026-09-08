class AirQualityAnalyzer:
    """Analyze AQI values and provide simple air-quality insights."""

    def classify_aqi(self, aqi):
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
        recommendations = {
            "Good": "Air quality is good. Outdoor activities are generally safe.",
            "Moderate": "Air quality is acceptable. Sensitive people should take care.",
            "Unhealthy for Sensitive Groups":
                "Sensitive people should reduce prolonged outdoor activity.",
            "Unhealthy":
                "Consider reducing outdoor activity and prolonged exposure.",
            "Very Unhealthy":
                "Avoid prolonged outdoor activity and consider staying indoors.",
            "Hazardous":
                "Avoid outdoor exposure as much as possible.",
            "Unknown":
                "AQI information is not available."
        }

        return recommendations.get(
            category,
            "No recommendation available."
        )

    def analyze(self, aqi):
        category = self.classify_aqi(aqi)

        return {
            "aqi": aqi,
            "category": category,
            "recommendation": self.get_recommendation(category)
        }