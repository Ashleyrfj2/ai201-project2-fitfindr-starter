# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
This tool searches the data for items that match the requested outfit description using size and max price as additional filters.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Descriptive keywords the usr is looking for 
- `size` (str): The size the user is requesting for the outfit, S, M, L or none if not provided
- `max_price` (float): The max amount of the total price for the agent to use as a filter. 0 if the user does not provide one

**What it returns:**
"id": 
"title"
"description"
"category": 
"style_tags": 
"size": 
"condition": 
"price": 
"colors": 
"brand": 
"platform": 
Best matching result will be returned first

**What happens if it fails or returns nothing:**
An empty list should be returned and the agent should tell the user that there were no results based off the current request and to modify the request to be more broad.

---

### Tool 2: suggest_outfit

**What it does:**
It uses the item from the search_listing to find an outfit recommendation from the users available items. If there are no available items based on the users input, then LLM should use basic styling guidelines and suggest recommendations and brands that fit the users need.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict):  The outfit suggestion returned from suggest_outfit
- `wardrobe` (dict): The users current owned items

**What it returns:**
This tool should return listings that meets the users request and why it is being suggested as an outfit. Such as matching current trends, colors compliment, weather, etc.

**What happens if it fails or returns nothing:**
LLM should provide basic style guidance for the user based off the users request. Such as, "If you increase your max price $20, there will be a few outfits that would work for what you are looking for"

---

### Tool 3: create_fit_card

**What it does:**
The results from the other two calls are used to create a description of the outfit that matches the users request.  The description should match the users overall tone and voice from the original input.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): The complete list of items that make up the requested outfit

**What it returns:**
A description of the outfit that was found to match the users request. 
A list of each item that is included in the suggested outfit with the price and a one sentence description of the item.

The description should match the users overall tone and voice. 
If no outfit is being returned, a 

**What happens if it fails or returns nothing:**
No exceptions - General recommendations are returned based off the users request

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | | Basic styling advice based off what the user already owns
| suggest_outfit | Wardrobe is empty | | Suggest the user update settings
| create_fit_card | Outfit input is missing or incomplete | | Explain what information is missing to the user so the user can modify the request

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
I will use auto agent in co-pilot and will work on one tool at a time. I will share the information I provided in the plan directly under each tool.

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
Agent runs the tool call search_listing and users the description, size, and max price to filter through options. The tool uses the users input to determine what is being used as description, size, and max price. 

If no results then the agent does not continue the remaining tool callls but outputs a message to the user that there are no available results.

If there are results then the agent stores the first result that matches it is stored for the remaining tool calls

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The agent calls suggest_outfit and uses the stored results from step 1 and stores it to be used for the fit card

**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->
