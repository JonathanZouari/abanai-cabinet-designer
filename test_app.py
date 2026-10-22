from streamlit.testing.v1 import AppTest


def test_app_switches_furniture():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    for kind in ("שידה", "ארון"):
        at.radio[0].set_value(kind).run()
        assert not at.exception and not at.error
