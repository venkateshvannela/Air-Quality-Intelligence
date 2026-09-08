from decouple import config

from ozon3 import Ozon3
from .analyzer import AirQualityAnalyzer
from .open_meteo import OpenMeteoService


class AirQualityService:
    """Combine WAQI and Open-Meteo air-quality services."""

    def __init__(self):
        self.token = config("WAQI_TOKEN")
        self.ozon3 = Ozon3(token=self.token)
        self.open_meteo = OpenMeteoService()
        self.analyzer = AirQualityAnalyzer()

    def get_city_analysis(self, city):
        """Use WAQI first and Open-Meteo as a fallback."""

        # -------------------------------------------------
        # STEP 1: Try WAQI / Ozon3
        # -------------------------------------------------
        try:
            data = self.ozon3.get_city_air(city)

            if not data.empty:
                latest = data.iloc[-1].to_dict()

                result = self.analyzer.analyze_air_data(
                    latest
                )

                result["requested_city"] = city
                result["source"] = "WAQI / Ozon3"
                result["source_type"] = (
                    "Monitoring station data"
                )
                result["fallback"] = False

                return result

        except Exception:
            pass

        # -------------------------------------------------
        # STEP 2: WAQI unavailable
        # Use Open-Meteo as fallback
        # -------------------------------------------------
        try:
            result = self.open_meteo.analyze_place(
                city,
                self.analyzer
            )

            if result["status"] == "success":
                result["requested_city"] = city
                result["fallback"] = True

                return result

        except Exception:
            pass

        # -------------------------------------------------
        # STEP 3: Both services unavailable
        # -------------------------------------------------
        return {
            "status": "No data",
            "requested_city": city,
            "message": (
                "Air quality data is not available "
                "from WAQI or Open-Meteo."
            ),
        }