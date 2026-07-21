import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROULETTE_VIEW = Path(__file__).parents[1] / "views" / "roulette.py"


class RouletteTeamModeTests(unittest.TestCase):
    def open_team_mode(self, names: str = "") -> AppTest:
        app = AppTest.from_file(str(ROULETTE_VIEW)).run()
        app.text_area[0].set_value(names)
        app.radio[0].set_value("👥 チーム分け")
        return app.run()

    def test_team_mode_does_not_raise_without_names(self) -> None:
        app = self.open_team_mode()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.slider), 0)
        self.assertTrue(app.button[0].disabled)

    def test_team_mode_offers_slider_for_three_or_more_names(self) -> None:
        app = self.open_team_mode("あき\nいお\nうみ")

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.slider[0].min, 2)
        self.assertEqual(app.slider[0].max, 3)
        self.assertFalse(app.button[0].disabled)


if __name__ == "__main__":
    unittest.main()
