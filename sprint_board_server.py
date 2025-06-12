from fastapi import FastAPI, Request
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

@app.post("/call_tool")
async def call_tool(request: Request):
    body = await request.json()
    tool = body.get("tool")
    args = body.get("args", {})

    if tool == "get_tasks":
        return get_tasks()
    elif tool == "create_task":
        return create_task(args["title"])
    elif tool == "update_task_status" or tool == "change_task_status":
        return update_task_status(args["task_id"], args.get("new_status", args.get("status")))
    elif tool == "delete_task":
        return delete_task(args["task_id"])
    elif tool == "find_task_by_title":
        return find_task_by_title(args["title"])
    else:
        return {"error": f"Unknown tool: {tool}. Available tools: get_tasks, create_task, update_task_status, delete_task, find_task_by_title"}

def get_tasks():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/tasks", headers=HEADERS)
    return res.json()

def create_task(title):
    try:
        data = {"title": title, "status": "not_started"}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/tasks", headers=HEADERS, json=data)
        
        print(f"🔍 Supabase response status: {res.status_code}")
        print(f"🔍 Supabase response text: {res.text}")
        
        # Supabase usually returns 201 for creates, but let's be flexible
        if res.status_code in [200, 201]:
            try:
                # Try to parse JSON response if it exists
                if res.text.strip():
                    response_data = res.json()
                    return {"status": "success", "message": f"Task '{title}' created successfully", "data": response_data}
                else:
                    return {"status": "success", "message": f"Task '{title}' created successfully"}
            except json.JSONDecodeError:
                # If JSON parsing fails, still return success since the HTTP status was good
                return {"status": "success", "message": f"Task '{title}' created successfully"}
        else:
            return {"status": "error", "message": f"Failed to create task: HTTP {res.status_code} - {res.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Exception creating task: {str(e)}"}

def update_task_status(task_id, new_status):
    try:
        url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}"
        data = {"status": new_status}
        res = requests.patch(url, headers=HEADERS, json=data)
        
        print(f"🔍 Update response status: {res.status_code}")
        print(f"🔍 Update response text: {res.text}")
        
        if res.status_code in [200, 204]:  # 204 is also common for updates
            return {"status": "success", "message": f"Task {task_id} updated to {new_status}"}
        else:
            return {"status": "error", "message": f"Failed to update task: HTTP {res.status_code} - {res.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Exception updating task: {str(e)}"}

def delete_task(task_id):
    url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}"
    res = requests.delete(url, headers=HEADERS)
    return {"status": "deleted" if res.status_code == 204 else "failed"}

def find_task_by_title(title):
    try:
        url = f"{SUPABASE_URL}/rest/v1/tasks?title=ilike.%{title}%"
        res = requests.get(url, headers=HEADERS)
        
        if res.status_code == 200:
            tasks = res.json()
            if tasks:
                return {"status": "success", "tasks": tasks, "message": f"Found {len(tasks)} task(s) matching '{title}'"}
            else:
                return {"status": "success", "tasks": [], "message": f"No tasks found matching '{title}'"}
        else:
            return {"status": "error", "message": f"Failed to search tasks: HTTP {res.status_code} - {res.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Exception searching tasks: {str(e)}"}
