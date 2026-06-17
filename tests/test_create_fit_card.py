from types import SimpleNamespace

import tools


class FakeCompletions:
    def __init__(self, content="Generated fit caption"):
        self.content = content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeClient:
    def __init__(self, content="Generated fit caption"):
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


def sample_item():
    return {
        "title": "Vintage Graphic Tee",
        "price": 24.0,
        "platform": "Depop",
    }


def test_create_fit_card_blank_outfit_returns_error_without_llm(monkeypatch):
    def fail_if_called():
        raise AssertionError("LLM should not be called for a blank outfit")

    monkeypatch.setattr(tools, "_get_groq_client", fail_if_called)

    result = tools.create_fit_card("   ", sample_item())

    assert isinstance(result, str)
    assert result.strip()
    assert "outfit suggestion" in result


def test_create_fit_card_calls_llm_with_caption_prompt(monkeypatch):
    fake_client = FakeClient(
        "Vintage Graphic Tee from Depop for $24.0 is giving relaxed weekend energy."
    )
    monkeypatch.setattr(tools, "_get_groq_client", lambda: fake_client)
    outfit = "Pair it with black baggy jeans and chunky white sneakers."

    result = tools.create_fit_card(outfit, sample_item())

    assert result == "Vintage Graphic Tee from Depop for $24.0 is giving relaxed weekend energy."
    call = fake_client.completions.calls[0]
    assert call["model"] == "llama-3.3-70b-versatile"
    assert call["temperature"] > 0.7
    prompt = call["messages"][1]["content"]
    assert "2-4 sentences" in prompt
    assert "Vintage Graphic Tee" in prompt
    assert "$24.0" in prompt
    assert "Depop" in prompt
    assert outfit in prompt


def test_create_fit_card_returns_fallback_when_llm_errors(monkeypatch):
    def raise_error():
        raise RuntimeError("api unavailable")

    monkeypatch.setattr(tools, "_get_groq_client", raise_error)

    result = tools.create_fit_card("Wear it with jeans.", sample_item())

    assert isinstance(result, str)
    assert result.strip()
    assert "Vintage Graphic Tee" in result
    assert "Depop" in result


def test_create_fit_card_returns_fallback_when_llm_content_is_empty(monkeypatch):
    fake_client = FakeClient(" ")
    monkeypatch.setattr(tools, "_get_groq_client", lambda: fake_client)

    result = tools.create_fit_card("Wear it with jeans.", sample_item())

    assert isinstance(result, str)
    assert result.strip()
    assert "Vintage Graphic Tee" in result
    assert "Depop" in result
