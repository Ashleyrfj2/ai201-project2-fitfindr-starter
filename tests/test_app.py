import app


def test_handle_query_blank_query_returns_error_without_agent(monkeypatch):
    def fail_if_called(*args):
        raise AssertionError("run_agent should not be called for a blank query")

    monkeypatch.setattr(app, "run_agent", fail_if_called)

    result = app.handle_query("   ", "Example wardrobe")

    assert result == ("Please enter what you are looking for.", "", "")


def test_handle_query_uses_example_wardrobe(monkeypatch):
    example_wardrobe = {"items": [{"title": "Example Jeans"}]}
    empty_wardrobe = {"items": []}
    captured = {}

    monkeypatch.setattr(app, "get_example_wardrobe", lambda: example_wardrobe)
    monkeypatch.setattr(app, "get_empty_wardrobe", lambda: empty_wardrobe)

    def fake_run_agent(query, wardrobe):
        captured["query"] = query
        captured["wardrobe"] = wardrobe
        return {
            "error": None,
            "selected_item": {
                "title": "Vintage Graphic Tee",
                "price": 24.0,
                "platform": "depop",
                "condition": "good",
            },
            "outfit_suggestion": "Wear it with jeans.",
            "fit_card": "Casual OOTD caption.",
        }

    monkeypatch.setattr(app, "run_agent", fake_run_agent)

    listing_text, outfit, fit_card = app.handle_query(
        " vintage graphic tee ",
        "Example wardrobe",
    )

    assert captured == {
        "query": "vintage graphic tee",
        "wardrobe": example_wardrobe,
    }
    assert "Title: Vintage Graphic Tee" in listing_text
    assert "Price: $24.0" in listing_text
    assert "Platform: depop" in listing_text
    assert "Condition: good" in listing_text
    assert outfit == "Wear it with jeans."
    assert fit_card == "Casual OOTD caption."


def test_handle_query_uses_empty_wardrobe_for_other_choice(monkeypatch):
    empty_wardrobe = {"items": []}
    captured = {}

    monkeypatch.setattr(app, "get_empty_wardrobe", lambda: empty_wardrobe)

    def fake_run_agent(query, wardrobe):
        captured["wardrobe"] = wardrobe
        return {
            "error": "No listings matched your request.",
            "selected_item": None,
            "outfit_suggestion": None,
            "fit_card": None,
        }

    monkeypatch.setattr(app, "run_agent", fake_run_agent)

    result = app.handle_query("ballgown under $5", "Empty wardrobe (new user)")

    assert captured["wardrobe"] == empty_wardrobe
    assert result == ("No listings matched your request.", "", "")


def test_handle_query_agent_error_returns_first_panel_only(monkeypatch):
    monkeypatch.setattr(
        app,
        "run_agent",
        lambda query, wardrobe: {
            "error": "Try broadening your search.",
            "selected_item": None,
            "outfit_suggestion": None,
            "fit_card": None,
        },
    )

    result = app.handle_query("designer ballgown", "Example wardrobe")

    assert result == ("Try broadening your search.", "", "")
