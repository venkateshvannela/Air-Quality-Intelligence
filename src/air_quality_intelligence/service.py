from decouple import config

from ozon3 import Ozon3
from .analyzer import AirQualityAnalyzer


class AirQualityService:
    """Connect Ozon3 data with the Air Quality Intelligence analyzer."""

    def __init__(self):
        self.token = config("WAQI_TOKEN")
        self.ozon3 = Ozon3(token=self.token)
        self.analyzer = AirQualityAnalyzer()

    def get_city_analysis(self, city):
        """Get live air-quality data for a city and analyze it."""

        try:
            data = self.ozon3.get_city_air(city)
        except Exception:
            return {
                "status": "No coverage",
                "city": city,
                "message": (
                    f"No WAQI air-quality station is available "
                    f"for {city}."
                )
            }

        if data.empty:
            return {
                "status": "No data",
                "city": city,
                "message": (
                    "Air quality data is currently not available."
                )
            }

        latest = data.iloc[-1].to_dict()

        result = self.analyzer.analyze_air_data(latest)
        result["requested_city"] = city

        return result