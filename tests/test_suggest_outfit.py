from types import SimpleNamespace

import tools


class FakeCompletions:
    def __init__(self, content="LLM outfit suggestion"):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeClient:
    def __init__(self, content="LLM outfit suggestion"):
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def sample_item():
    return {
        "title": "Vintage Graphic Tee",
        "description": "Faded band tee with a relaxed fit",
        "category": "tops",
        "price": 24.0,
        "style_tags": ["vintage", "streetwear"],
        "colors": ["black", "white"],
    }


def test_suggest_outfit_empty_wardrobe_asks_for_general_styling(monkeypatch):
    fake_client = FakeClient("Try it with loose denim and silver jewelry.")
    monkeypatch.setattr(tools, "_get_groq_client", lambda: fake_client)

    result = tools.suggest_outfit(sample_item(), {"items": []})

    assert result == "Try it with loose denim and silver jewelry."
    call = fake_client.completions.calls[0]
    assert call["model"] == "llama-3.3-70b-versatile"
    prompt = call["messages"][1]["content"]
    assert "wardrobe list is empty" in prompt
    assert "general styling ideas" in prompt
    assert "Vintage Graphic Tee" in prompt


def test_suggest_outfit_with_wardrobe_names_existing_pieces(monkeypatch):
    fake_client = FakeClient("Wear the tee with baggy jeans and chunky sneakers.")
    monkeypatch.setattr(tools, "_get_groq_client", lambda: fake_client)
    wardrobe = {
        "items": [
            {
                "title": "Black Baggy Jeans",
                "category": "bottoms",
                "size": "M",
                "colors": ["black"],
            },
            {
                "title": "Chunky White Sneakers",
                "category": "shoes",
                "size": "8",
                "colors": ["white"],
            },
        ]
    }

    result = tools.suggest_outfit(sample_item(), wardrobe)

    assert result == "Wear the tee with baggy jeans and chunky sneakers."
    prompt = fake_client.completions.calls[0]["messages"][1]["content"]
    assert "Black Baggy Jeans" in prompt
    assert "Chunky White Sneakers" in prompt
    assert "Suggest 1-2 specific outfit combinations" in prompt


def test_suggest_outfit_returns_fallback_when_llm_errors(monkeypatch):
    def raise_error():
        raise RuntimeError("api unavailable")

    monkeypatch.setattr(tools, "_get_groq_client", raise_error)

    result = tools.suggest_outfit(sample_item(), {"items": []})

    assert isinstance(result, str)
    assert result.strip()
    assert "couldn't fetch a style response" in result


def test_suggest_outfit_returns_fallback_when_llm_content_is_empty(monkeypatch):
    fake_client = FakeClient("   ")
    monkeypatch.setattr(tools, "_get_groq_client", lambda: fake_client)

    result = tools.suggest_outfit(sample_item(), {"items": []})

    assert isinstance(result, str)
    assert result.strip()
    assert "couldn't fetch a style response" in result
