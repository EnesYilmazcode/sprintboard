import json

def test_json_cleaning():
    # Simulate the problematic response from AI
    raw_response = """json
{
  "tool_code": "find_task_by_title",
  "arguments": {
    "title": "speed"
  }
}"""

    print("🔍 Original response:")
    print(repr(raw_response))
    print()

    # Apply the same cleaning logic from agent.py
    cleaned = raw_response.strip()

    # Remove any wrapping code block
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
        
    # Handle case where AI adds "json" before the JSON object
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()
        
    # Remove any remaining newlines at the start
    cleaned = cleaned.lstrip('\n\r ')

    print("🔍 Cleaned JSON:")
    print(repr(cleaned))
    print()

    try:
        # Parse JSON
        tool_call = json.loads(cleaned)
        print("✅ JSON parsing successful!")
        print("🤖 Tool Call:", tool_call)
        return True
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        return False

if __name__ == "__main__":
    test_json_cleaning() 