# Frontend Integration - Week2 Updates

## New Features Added

### 1. LLM-Powered Extraction Button

Added a dedicated **"Extract (LLM)"** button that uses Ollama for intelligent action item extraction.

**How it works:**

- Sends `use_llm: true` to the `/action-items/extract` endpoint
- Uses the configured LLM model (default: llama3.1)
- Falls back to heuristic extraction if LLM fails
- Displays "(using LLM)" indicator when complete

### 2. List Notes Functionality

Added a **"List Notes"** button to view all saved notes.

**How it works:**

- Calls `GET /notes` endpoint to retrieve all notes
- Displays notes with content, ID, and creation timestamp
- Styled cards for better readability

### 3. Dual Extraction Methods

Users can now choose between two extraction methods:

| Button | Method | Description |
|--------|--------|-------------|
| **Extract (Heuristic)** | Rule-based | Fast, deterministic, pattern matching |
| **Extract (LLM)** | AI-powered | Intelligent, context-aware, requires LLM |

## UI Layout

```
┌─────────────────────────────────────────────┐
│  Action Item Extractor                      │
├─────────────────────────────────────────────┤
│  [Textarea for notes]                       │
│                                             │
│  [✓] Save as note                          │
│  [Extract (Heuristic)]  [Extract (LLM)]    │
│                                             │
│  Extracted items appear here...            │
├─────────────────────────────────────────────┤
│  Saved Notes                                │
│  [List Notes]                               │
│                                             │
│  Notes appear here...                       │
└─────────────────────────────────────────────┘
```

## API Endpoints Used

### POST /action-items/extract

```json
{
  "text": "- [ ] Task 1\n- Task 2",
  "save_note": true,
  "use_llm": true
}
```

**Response:**

```json
{
  "note_id": 1,
  "items": [
    {
      "id": 1,
      "text": "Task 1",
      "note_id": 1,
      "done": false,
      "created_at": "2026-02-04T10:30:00"
    }
  ]
}
```

### GET /notes

Retrieves all saved notes.

**Response:**

```json
[
  {
    "id": 1,
    "content": "- [ ] Task 1\n- Task 2",
    "created_at": "2026-02-04T10:30:00"
  }
]
```

## Frontend Implementation Details

### Key Features

1. **Unified Extract Function**
   - Single `extractItems(useLlm)` function handles both methods
   - Clear loading states: "Extracting..." vs "Extracting with LLM..."
   - Error handling with descriptive messages

2. **Note Display**
   - Formatted cards with gray background
   - Shows ID and localized timestamp
   - HTML escaping for security

3. **Visual Feedback**
   - Different button colors (primary blue vs secondary gray)
   - Hover states for better UX
   - Loading indicators during API calls

4. **Error Handling**
   - Catches network errors
   - Displays error messages to user
   - Logs errors to console for debugging

## Testing

### Manual Testing Steps

1. Start the server:

   ```bash
   poetry run uvicorn week2.app.main:app --reload
   ```

2. Open <http://localhost:8000> in browser

3. Test heuristic extraction:
   - Paste: `- [ ] Set up database\n- Implement API`
   - Click "Extract (Heuristic)"
   - Verify items appear with checkboxes

4. Test LLM extraction:
   - Paste: `We need to implement the API and set up the database`
   - Click "Extract (LLM)"
   - Verify items appear with "(using LLM)" indicator

5. Test notes listing:
   - Click "List Notes"
   - Verify all saved notes appear with IDs and timestamps

### Automated Testing

Run the integration test:

```bash
poetry run python week2/test_integration.py
```

This verifies:

- Frontend HTML contains all buttons
- Heuristic extraction endpoint works
- LLM extraction endpoint works
- Notes listing endpoint works

## Configuration

The LLM model can be configured via environment variables:

```bash
export APP_OLLAMA_MODEL=llama3.2
export APP_OLLAMA_HOST=http://localhost:11434/
poetry run uvicorn week2.app.main:app --reload
```

Or via `.env` file:

```env
APP_OLLAMA_MODEL=llama3.2
APP_OLLAMA_HOST=http://localhost:11434/
```

## Security Features

1. **HTML Escaping**: All user content is escaped to prevent XSS
2. **Input Validation**: Pydantic schemas validate all API inputs
3. **Error Messages**: Generic errors to avoid leaking internal details

## Browser Compatibility

Tested and working in:

- Chrome/Edge (modern)
- Firefox (modern)
- Safari (modern)

Requires ES6+ support (async/await, arrow functions, template literals).

## Future Enhancements

Potential improvements:

- [ ] Compare LLM vs Heuristic side-by-side
- [ ] Note editing and deletion
- [ ] Filter notes by date
- [ ] Export notes/action items
- [ ] Batch extraction from multiple notes
- [ ] Custom LLM prompt configuration
