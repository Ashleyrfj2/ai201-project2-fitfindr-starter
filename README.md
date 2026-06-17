# FitFindr

a thrift-search agent. you describe what you want, it finds a secondhand listing, styles it against your wardrobe, and writes a shareable caption. three tools, one planning loop, all state in a session dict.

## setup

```bash
pip install -r requirements.txt
```

drop your Groq key in a `.env`:

```text
GROQ_API_KEY=your_key_here
```

run the app:

```bash
python app.py
```

run the tests:

```bash
pytest
```

## app

`app.py` is the Gradio interface. the layout is already wired, and `handle_query()` maps one user query into three panels:

- top listing found
- outfit idea
- fit card

blank query returns an error in the first panel. agent errors also return in the first panel, with the other two panels empty.

## tools

three tools, each callable and testable on its own. signatures are exact.

### search_listings

```python
search_listings(description: str, size: str | None = None, max_price: float | None = None) -> list[dict]
```

searches the mock listings for items matching the description, plus optional size and price ceiling. returns matching listing dicts ranked by keyword relevance, best first. each dict has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`. no matches returns `[]`.

### suggest_outfit

```python
suggest_outfit(new_item: dict, wardrobe: dict) -> str
```

takes the found item plus the user's wardrobe and asks Groq for 1-2 outfit ideas. empty wardrobe still works: it asks for general styling ideas for the new item instead of crashing or returning an empty string.

### create_fit_card

```python
create_fit_card(outfit: str, new_item: dict) -> str
```

takes the outfit string plus the item and asks Groq for a 2-4 sentence OOTD caption. the caption should mention the item name, price, and platform naturally once each. empty outfit returns an error string and does not call the LLM.

## planning loop

the agent branches. it does not fire all three tools blindly.

1. initialize the session with `_new_session(query, wardrobe)`.
2. parse the query into `description`, `size`, and `max_price`. regex scans for the `$` amount and an explicit size mention. the raw query text becomes the description.
3. run `search_listings(description, size, max_price)`.
4. no results -> set `session["error"]`, stop, and return the session. `suggest_outfit` and `create_fit_card` do not run.
5. results -> set `session["selected_item"]` to the top result.
6. run `suggest_outfit(selected_item, wardrobe)` and store `session["outfit_suggestion"]`.
7. run `create_fit_card(outfit_suggestion, selected_item)` and store `session["fit_card"]`.
8. return the session.

so tool 2 and tool 3 only run on the happy path.

## state management

everything for one run lives in the session dict, built at the top of `run_agent`. each step writes its result, and the next step reads from that same session. the user only enters one query.

what is stored:

- `query` - the original request
- `parsed` - description, size, and max_price pulled from the query
- `search_results` - full list returned by `search_listings`
- `selected_item` - top result, passed into `suggest_outfit`
- `wardrobe` - the selected wardrobe dict
- `outfit_suggestion` - string returned by `suggest_outfit`
- `fit_card` - string returned by `create_fit_card`
- `error` - set when the run ends early

session is the single source of truth.

## error handling

- `search_listings` -> returns `[]` when no listings match. the agent sets an error message and stops.
- `suggest_outfit` -> catches LLM errors and returns a short fallback string. empty wardrobe gets general styling advice.
- `create_fit_card` -> empty outfit returns an error string. LLM errors return a short fallback caption.
- `handle_query` -> blank input returns an error in the first panel and empty strings for the other two.

example: `"designer ballgown size XXS under $5"` -> search returns `[]` -> agent sets a no-results message and returns. `suggest_outfit` and `create_fit_card` never run.

## tests

the test suite covers all three tools, the agent loop, and the app query handler.

```bash
pytest tests -q
```

current coverage focus:

- keyword scoring, size filtering, price filtering, and no-match behavior for `search_listings`
- empty wardrobe, populated wardrobe, and LLM fallback paths for `suggest_outfit`
- blank outfit guard, prompt content, and LLM fallback paths for `create_fit_card`
- happy path and no-results branching in `run_agent`
- blank query, wardrobe choice, agent error, and output formatting in `handle_query`

## spec reflection

what helped: writing the tool specs first made each implementation easy to test in isolation. once the tools had focused tests, the planning loop was mostly about wiring state and verifying the branch on empty search results.

where it is simple: search relevance is keyword overlap, not a semantic search engine. it lowercases the query, extracts word-like tokens, checks whether each token appears in the listing text, drops zero-score listings, and sorts by score.

## ai usage

- used Copilot to implement `suggest_outfit`, `create_fit_card`, `run_agent`, and `handle_query` from the project specs.
- used Copilot to mock Groq clients in tests so the suite can run without network calls or a real API key.
- used Copilot to implement pytest after each milestone to catch branch mistakes, especially making sure the agent stops after empty search results.