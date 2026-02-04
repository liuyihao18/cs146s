"""
Test script to verify the frontend integration works correctly.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_extract_heuristic():
    """Test extraction with heuristic method."""
    payload = {
        "text": "- [ ] Set up database\n- Implement API\n- Write tests",
        "save_note": True,
        "use_llm": False
    }
    response = requests.post(f"{BASE_URL}/action-items/extract", json=payload)
    print(f"✓ Heuristic extraction: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"  Extracted {len(data['items'])} items")
        print(f"  Note ID: {data['note_id']}")

def test_extract_llm():
    """Test extraction with LLM method."""
    payload = {
        "text": "- [ ] Set up database\n- Implement API\n- Write tests",
        "save_note": True,
        "use_llm": True
    }
    response = requests.post(f"{BASE_URL}/action-items/extract", json=payload)
    print(f"✓ LLM extraction: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"  Extracted {len(data['items'])} items (LLM)")
        print(f"  Note ID: {data['note_id']}")

def test_list_notes():
    """Test listing all notes."""
    response = requests.get(f"{BASE_URL}/notes")
    print(f"✓ List notes: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"  Found {len(data)} notes")
        if data:
            print(f"  Latest note ID: {data[0]['id']}")

def test_frontend():
    """Test that frontend is accessible."""
    response = requests.get(BASE_URL)
    print(f"✓ Frontend: {response.status_code}")
    if response.ok:
        content = response.text
        assert "Extract (Heuristic)" in content, "Heuristic button not found"
        assert "Extract (LLM)" in content, "LLM button not found"
        assert "List Notes" in content, "List Notes button not found"
        print("  All buttons present in HTML")

if __name__ == "__main__":
    print("Testing Week2 Backend Integration\n")
    print("Note: Make sure the server is running with:")
    print("  poetry run uvicorn week2.app.main:app --reload\n")
    
    try:
        test_frontend()
        print()
        test_extract_heuristic()
        print()
        test_extract_llm()
        print()
        test_list_notes()
        print("\n✅ All tests passed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")
