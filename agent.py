import google.generativeai as genai
import os, requests, json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MCP_URL = "http://localhost:8000/call_tool"

def extract_status_from_input(user_input):
    """Extract the desired task status from user input"""
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ["in progress", "progress", "working", "started"]):
        return "in_progress"
    elif any(word in input_lower for word in ["completed", "done", "finished", "complete"]):
        return "completed"
    elif any(word in input_lower for word in ["not started", "todo", "new", "pending"]):
        return "not_started"
    
    return None

def call_mcp(tool, args):
    try:
        res = requests.post(MCP_URL, json={"tool": tool, "args": args})
        if res.status_code == 200:
            if res.text.strip():  # Check if response has content
                return res.json()
            else:
                return {"status": "success", "message": "Task completed successfully"}
        else:
            return {"error": f"HTTP {res.status_code}: {res.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {str(e)}", "raw_response": res.text}

def ai_handle_message(user_input):
    prompt = f"""
You are a sprint board assistant.

Available tools:
1. create_task - Create a new task
2. update_task_status - Update task status (requires numeric task_id)
3. get_tasks - Get all tasks
4. find_task_by_title - Find tasks by title
5. delete_task - Delete a task

For status updates, you MUST first find the task ID. Use this workflow:
1. If user wants to update a task by name/title, first call find_task_by_title
2. Then use the returned task ID to call update_task_status

Valid statuses: "not_started", "in_progress", "completed"

Examples:
- "Create task X" → {{ "tool_code": "create_task", "arguments": {{ "title": "X" }} }}
- "Get all tasks" → {{ "tool_code": "get_tasks", "arguments": {{}} }}
- "Find reload task" → {{ "tool_code": "find_task_by_title", "arguments": {{ "title": "reload" }} }}
- "Update task 5 to completed" → {{ "tool_code": "update_task_status", "arguments": {{ "task_id": 5, "new_status": "completed" }} }}

For user input: "{user_input}"

If the user wants to update a task status by name (not ID), respond with find_task_by_title first.
If they provide a numeric ID, use update_task_status directly.

CRITICAL: Respond with ONLY the raw JSON object. Do NOT use code blocks. Do NOT add json before the response. Just return the plain JSON object starting with {{.
"""

    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
    raw = response.text.strip()

    # Remove code block formatting if somehow included
    if raw.startswith("```"):
        raw = raw.split("```")[1].strip()

    try:
        cleaned = raw.strip()

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

        print(f"🔍 Cleaned JSON: {cleaned}")  # Debug output
        
        # Parse JSON
        tool_call = json.loads(cleaned)

        print("🤖 Tool Call:", tool_call)
        result = call_mcp(tool_call["tool_code"], tool_call["arguments"])
        print("🛠️ MCP Result:", result)
        
        # Handle multi-step workflow for status updates
        if tool_call["tool_code"] == "find_task_by_title" and result.get("status") == "success":
            tasks = result.get("tasks", [])
            if tasks:
                # If we found tasks, check if this was for a status update
                if any(word in user_input.lower() for word in ["update", "change", "mark", "move", "set", "progress", "completed", "done"]):
                    # Extract the desired status from the original user input
                    status = extract_status_from_input(user_input)
                    if status:
                        # Use the first matching task
                        task_id = tasks[0]["id"]
                        print(f"🔄 Auto-updating task {task_id} to {status}...")
                        update_result = call_mcp("update_task_status", {"task_id": task_id, "new_status": status})
                        print("🛠️ Update Result:", update_result)
                        
                        if update_result.get("status") == "success":
                            print("✅", update_result.get("message", f"Task updated to {status}!"))
                        else:
                            print("❌", update_result.get("error", "Failed to update task"))
                        return
        
        # Print user-friendly success message
        if result.get("status") == "success":
            print("✅", result.get("message", "Task completed successfully!"))
        elif "error" in result:
            print("❌", result["error"])
        else:
            print("✅ Task completed successfully!")
    except Exception as e:
        print("❌ Failed to process tool call:", e)
        print("Raw response:\n", raw)


