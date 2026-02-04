# Week 2 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.

## YOUR RESPONSES

For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature

Prompt:

```
Analyze the existing extract_action_items() function in week2/app/services/extract.py, which currently extracts action items using predefined heuristics. Your task is to implement an LLM-powered alternative, extract_action_items_llm(), that utilizes Ollama to perform action item extraction via a large language model. To produce structured outputs (i.e. JSON array of strings), you could refer to this documentation: https://ollama.com/blog/structured-outputs.
```

Generated Code Snippets:

```diff
# app/services/extract.py
+ def extract_action_items_llm(text: str, model: str | None = None) -> List[str]:
+     if not text.strip():
+         return []
+ 
+     model_name = model or os.getenv("OLLAMA_MODEL", "llama3.1")
+     schema = {"type": "array", "items": {"type": "string"}}
+     messages = [
+         {
+             "role": "system",
+             "content": (
+                 "Extract action items from the user-provided notes. "
+                 "Return ONLY a JSON array of strings. "
+                 "Each string must be a concise, self-contained task."
+             ),
+         },
+         {"role": "user", "content": text},
+     ]
+ 
+     try:
+         response = client.chat(
+             model=model_name,
+             messages=messages,
+             format=schema,
+         )
+         content = response.get("message", {}).get("content", "")
+         parsed: Any = json.loads(content)
+         if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
+             return [item.strip() for item in parsed if item.strip()]
+     except Exception:
+         pass
+ 
+     return extract_action_items(text)

# app/routers/action_items.py
- items = extract_action_items(text)
+ # items = extract_action_items(text)
+ items = extract_action_items_llm(text)
```

### Exercise 2: Add Unit Tests

Prompt:

```
Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in week2/tests/test_extract.py.
```

Generated Code Snippets:

```diff
# tests/test_extract.py
+ def test_extract_action_items_llm_bullets(monkeypatch):
+     def _fake_chat(*, model, messages, format):
+         return {"message": {"content": "[\"Set up database\", \"Write tests\"]"}}
+ 
+     monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)
+ 
+     text = """
+     Notes:
+     - [ ] Set up database
+     * Write tests
+     """.strip()
+ 
+     items = extract_action_items_llm(text, model="test-model")
+     assert items == ["Set up database", "Write tests"]
+ 
+ 
+ def test_extract_action_items_llm_keywords(monkeypatch):
+     def _fake_chat(*, model, messages, format):
+         return {"message": {"content": "[\"Send follow-up email\", \"Schedule demo\"]"}}
+ 
+     monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)
+ 
+     text = """
+     todo: Send follow-up email
+     action: Schedule demo
+     """.strip()
+ 
+     items = extract_action_items_llm(text, model="test-model")
+     assert items == ["Send follow-up email", "Schedule demo"]
+ 
+ 
+ def test_extract_action_items_llm_empty_input(monkeypatch):
+     def _fake_chat(*, model, messages, format):
+         raise AssertionError("chat should not be called for empty input")
+ 
+     monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)
+ 
+     assert extract_action_items_llm("   ") == []
+ 
+ 
+ def test_extract_action_items_llm_fallback_to_heuristic(monkeypatch):
+     def _fake_chat(*, model, messages, format):
+         raise RuntimeError("LLM unavailable")
+ 
+     monkeypatch.setattr("week2.app.services.extract.client.chat", _fake_chat)
+ 
+     text = """
+     - [ ] Set up database
+     * implement API extract endpoint
+     """.strip()
+ 
+     items = extract_action_items_llm(text, model="test-model")
+     assert "Set up database" in items
+     assert "implement API extract endpoint" in items
```

### Exercise 3: Refactor Existing Code for Clarity

Prompt:

```
Perform a refactor of the code in the week2 backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling.
```

Generated/Modified Code Snippets:

```diff
# Too many changes
+ REFACTORING.md
+ REFACTORING_SUMMARY.md
+ REFACTORING_COMPARISON.md
+ INDEX.md 
+ BEFORE_AFTER_COMPARISON.md
+ VERIFICATION_CHECKLIST.md
# It also tries to pass all tests and fix all warnings.
```

### Exercise 4: Use Agentic Mode to Automate a Small Task

Prompt:

```
Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint. 
Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.
```

Generated Code Snippets:

```diff
# app/frontend/index.html
# Too many changes
+ FRONTEND_INTEGRATION.md
```

### Exercise 5: Generate a README from the Codebase

Prompt:

```
Analyze the current codebase and generate a well-structured README.md file. The README should include, at a minimum:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite
```

Generated Code Snippets:

```diff
+ README.md
```

## SUBMISSION INSTRUCTIONS

1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields.
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope.
