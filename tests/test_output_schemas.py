import app


def test_app_uses_original_two_way_fe_panel_regression_filename():
    assert app.REQUIRED_FILES["date_fe_regression"].name == "panel_regression_two_way_fe.csv"
