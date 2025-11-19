from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

class ComfortByCityTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.views.requests.get")          # for forecast + geocode
    @patch("api.views.predict_comfort")       # ML model predict
    def test_comfort_by_city(self, mock_predict, mock_requests):
        # -------------------------------------------
        # Mock geocoding API response
        # -------------------------------------------
        mock_requests.side_effect = [
            # Geocoding call
            type("Resp", (), {"json": lambda: {
                "results": [{
                    "latitude": 25.77,
                    "longitude": -80.19,
                    "name": "Miami",
                    "country": "United States"
                }]
            }}),
            # Forecast call
            type("Resp", (), {"json": lambda: {
                "daily": {
                    "time": ["2025-04-01", "2025-04-02"],
                    "temperature_2m_max": [28.0, 29.0],
                    "temperature_2m_min": [22.0, 23.0],
                    "precipitation_sum": [0.0, 1.0],
                    "wind_speed_10m_max": [10.0, 12.0],
                    "relativehumidity_2m_max": [65, 70],
                    "cloudcover_mean": [40, 60]
                }
            }}),
        ]

        # -------------------------------------------
        # Mock ML model predict_comfort return values
        # -------------------------------------------
        mock_predict.side_effect = [75.5, 72.1]

        # -------------------------------------------
        # Make POST request
        # -------------------------------------------
        payload = {
            "city": "Miami",
            "start_date": "2025-11-24",
            "end_date": "2025-11-21"
        }
        response = self.client.post("/api/comfort-by-city/", payload, format="json")

        # -------------------------------------------
        # Assert correct behavior
        # -------------------------------------------
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["city"], "Miami")
        self.assertEqual(len(data["daily_scores"]), 2)

        self.assertEqual(data["daily_scores"][0]["comfort_score"], 75.5)
        self.assertEqual(data["daily_scores"][1]["comfort_score"], 72.1)
