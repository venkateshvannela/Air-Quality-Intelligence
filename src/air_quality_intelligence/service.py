from decouple import config
from ozon3 import Ozon3

from .analyzer import AirQualityAnalyzer
from .open_meteo import OpenMeteoService


class AirQualityService:

    def __init__(self):
        self.token = config("WAQI_TOKEN")
        self.ozon3 = Ozon3(token=self.token)
        self.open_meteo = OpenMeteoService()
        self.analyzer = AirQualityAnalyzer()

    def get_city_analysis(self, city):

        # Try WAQI first
        try:
            data = self.ozon3.get_city_air(city)

            if not data.empty:

                latest = data.iloc[-1].to_dict()

                result = self.analyzer.analyze_air_data(latest)

                result["requested_city"] = city
                result["source"] = "WAQI / Ozon3"
                result["source_type"] = "Monitoring station data"
                result["fallback"] = False

                latitude = latest.get("latitude")
                longitude = latest.get("longitude")

                if latitude is not None and longitude is not None:

                    try:
                        weather_result = self.open_meteo.get_weather(
                            latitude,
                            longitude
                        )

                        result["weather"] = {
                            "current": weather_result.get("current", {}),
                            "hourly": weather_result.get("hourly", {})
                        }

                    except Exception:
                        result["weather"] = {
                            "status": "Weather unavailable"
                        }

                return result

        except Exception:
            pass

        # Use Open-Meteo when WAQI is unavailable
        try:

            result = self.open_meteo.analyze_place_with_weather(
                city,
                self.analyzer
            )

            if result["status"] == "success":

                result["requested_city"] = city
                result["fallback"] = True

                return result

        except Exception:
            pass

        # Both services failed
        return {
            "status": "No data",
            "requested_city": city,
            "message": (
                "Air quality data is not available "
                "from WAQI or Open-Meteo."
            )
        }