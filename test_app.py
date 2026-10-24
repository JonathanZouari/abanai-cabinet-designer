from streamlit.testing.v1 import AppTest


def test_app_loads_without_exceptions():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    assert at.tabs[0].label == "חזית – הזזה ידנית"
