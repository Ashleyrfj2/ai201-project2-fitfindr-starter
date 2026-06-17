import agent


def test_run_agent_happy_path_stores_state_and_calls_tools_in_order(monkeypatch):
    calls = []
    wardrobe = {"items": [{"title": "Black Baggy Jeans"}]}
    selected_item = {
        "id": "lst_001",
        "title": "Vintage Graphic Tee",
        "price": 24.0,
        "platform": "depop",
    }

    def fake_search(description, size, max_price):
        calls.append(("search", description, size, max_price))
        return [selected_item]

    def fake_suggest(item, passed_wardrobe):
        calls.append(("suggest", item, passed_wardrobe))
        return "Wear it with black baggy jeans."

    def fake_fit_card(outfit, item):
        calls.append(("fit_card", outfit, item))
        return "Vintage tee OOTD caption."

    monkeypatch.setattr(agent, "search_listings", fake_search)
    monkeypatch.setattr(agent, "suggest_outfit", fake_suggest)
    monkeypatch.setattr(agent, "create_fit_card", fake_fit_card)

    query = "vintage graphic tee size M under $30"
    session = agent.run_agent(query, wardrobe)

    assert session["query"] == query
    assert session["wardrobe"] == wardrobe
    assert session["parsed"] == {
        "description": query,
        "size": "M",
        "max_price": 30.0,
    }
    assert session["search_results"] == [selected_item]
    assert session["selected_item"] == selected_item
    assert session["outfit_suggestion"] == "Wear it with black baggy jeans."
    assert session["fit_card"] == "Vintage tee OOTD caption."
    assert session["error"] is None
    assert calls == [
        ("search", query, "M", 30.0),
        ("suggest", selected_item, wardrobe),
        ("fit_card", "Wear it with black baggy jeans.", selected_item),
    ]


def test_run_agent_no_results_returns_early_without_downstream_tools(monkeypatch):
    calls = []

    def fake_search(description, size, max_price):
        calls.append(("search", description, size, max_price))
        return []

    def fail_if_called(*args):
        raise AssertionError("Downstream tools should not be called")

    monkeypatch.setattr(agent, "search_listings", fake_search)
    monkeypatch.setattr(agent, "suggest_outfit", fail_if_called)
    monkeypatch.setattr(agent, "create_fit_card", fail_if_called)

    query = "designer ballgown size XS under $5"
    session = agent.run_agent(query, {"items": []})

    assert session["parsed"] == {
        "description": query,
        "size": "XS",
        "max_price": 5.0,
    }
    assert session["search_results"] == []
    assert session["selected_item"] is None
    assert session["outfit_suggestion"] is None
    assert session["fit_card"] is None
    assert session["error"]
    assert calls == [("search", query, "XS", 5.0)]


def test_run_agent_leaves_missing_price_and_size_as_none(monkeypatch):
    captured = {}

    def fake_search(description, size, max_price):
        captured["args"] = (description, size, max_price)
        return []

    monkeypatch.setattr(agent, "search_listings", fake_search)
    monkeypatch.setattr(agent, "suggest_outfit", lambda *args: "unused")
    monkeypatch.setattr(agent, "create_fit_card", lambda *args: "unused")

    query = "show me something cottagecore"
    session = agent.run_agent(query, {"items": []})

    assert session["parsed"] == {
        "description": query,
        "size": None,
        "max_price": None,
    }
    assert captured["args"] == (query, None, None)
