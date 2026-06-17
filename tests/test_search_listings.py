import tools


def sample_listings():
    return [
        {
            "id": "tee_1",
            "title": "Vintage Graphic Tee",
            "description": "Soft black band tee with a faded front graphic.",
            "category": "tops",
            "style_tags": ["vintage", "graphic tee", "streetwear"],
            "size": "M",
            "condition": "good",
            "price": 24.0,
            "colors": ["black"],
            "brand": None,
            "platform": "depop",
        },
        {
            "id": "tee_2",
            "title": "Plain White Tee",
            "description": "Simple cotton tee.",
            "category": "tops",
            "style_tags": ["basic", "minimal"],
            "size": "M",
            "condition": "excellent",
            "price": 12.0,
            "colors": ["white"],
            "brand": "Uniqlo",
            "platform": "thredUp",
        },
        {
            "id": "jeans_1",
            "title": "Vintage Levi's 501 Jeans",
            "description": "Classic straight leg denim.",
            "category": "bottoms",
            "style_tags": ["vintage", "denim", "classic"],
            "size": "W30 L30",
            "condition": "good",
            "price": 38.0,
            "colors": ["blue"],
            "brand": "Levi's",
            "platform": "poshmark",
        },
        {
            "id": "jacket_1",
            "title": "90s Track Jacket",
            "description": "Lightweight zip jacket with sleeve stripes.",
            "category": "outerwear",
            "style_tags": ["90s", "athletic", "streetwear"],
            "size": "L",
            "condition": "excellent",
            "price": 45.0,
            "colors": ["navy", "white"],
            "brand": "Champion",
            "platform": "depop",
        },
    ]


def test_search_listings_returns_relevant_matches_sorted_by_score(monkeypatch):
    monkeypatch.setattr(tools, "load_listings", sample_listings)

    results = tools.search_listings("vintage graphic tee")

    assert [item["id"] for item in results] == ["tee_1", "tee_2", "jeans_1"]


def test_search_listings_filters_by_size_case_insensitively(monkeypatch):
    monkeypatch.setattr(tools, "load_listings", sample_listings)

    results = tools.search_listings("vintage", size="m")

    assert [item["id"] for item in results] == ["tee_1"]


def test_search_listings_filters_by_max_price(monkeypatch):
    monkeypatch.setattr(tools, "load_listings", sample_listings)

    results = tools.search_listings("tee", max_price=20.0)

    assert [item["id"] for item in results] == ["tee_2"]
    assert all(item["price"] <= 20.0 for item in results)


def test_search_listings_returns_empty_list_when_no_keywords_match(monkeypatch):
    monkeypatch.setattr(tools, "load_listings", sample_listings)

    results = tools.search_listings("sequined ballgown", size="XS", max_price=5.0)

    assert results == []


def test_search_listings_without_description_returns_filtered_items(monkeypatch):
    monkeypatch.setattr(tools, "load_listings", sample_listings)

    results = tools.search_listings("", max_price=25.0)

    assert [item["id"] for item in results] == ["tee_1", "tee_2"]
