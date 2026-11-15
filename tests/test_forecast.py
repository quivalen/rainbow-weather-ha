"""Offline tests without importing Home Assistant."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "forecast", Path(__file__).parents[1] / "custom_components/rainbow_weather/forecast.py")
forecast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forecast)


class ForecastTest(unittest.TestCase):
    def setUp(self):
        self.data = {"forecast": [
            {"timestampBegin": 0, "timestampEnd": 60, "precipRate": 0},
            {"timestampBegin": 60, "timestampEnd": 120, "precipRate": 6},
            {"timestampBegin": 120, "timestampEnd": 180, "precipRate": 0},
        ]}

    def test_current_boundary(self):
        self.assertEqual(forecast.current(self.data, 60)["precipRate"], 6)
        self.assertIsNone(forecast.current(self.data, 180))

    def test_partial_total(self):
        self.assertAlmostEqual(forecast.total(self.data, 90), 0.05)

    def test_episode_end(self):
        self.assertEqual(forecast.episode_end(self.data, 90), 120)
        self.assertIsNone(forecast.episode_end(self.data, 0))

    def test_open_ended_episode(self):
        self.data["forecast"].pop()
        self.assertIsNone(forecast.episode_end(self.data, 90))

    def test_expired(self):
        self.assertEqual(forecast.remaining(self.data, 180), [])
        self.assertEqual(forecast.wet(self.data, 180), [])

    def test_empty(self):
        self.assertIsNone(forecast.current({}, 0))
