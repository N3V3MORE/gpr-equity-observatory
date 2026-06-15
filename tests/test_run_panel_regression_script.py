from scripts.run_panel_regression import _summary_text


class _Summary:
    def as_text(self) -> str:
        return "summary text"


class _StatsmodelsLikeResult:
    def summary(self):
        return _Summary()


class _LinearmodelsLikeResult:
    summary = _Summary()


def test_summary_text_handles_method_and_property_summaries():
    assert _summary_text(_StatsmodelsLikeResult()) == "summary text"
    assert _summary_text(_LinearmodelsLikeResult()) == "summary text"
