from fastapi import FastAPI, Request
from dotenv import load_dotenv
import requests
import os

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
    elif tool == "update_task_status":
        return update_task_status(args["task_id"], args["new_status"])
    elif tool == "delete_task":
        return delete_task(args["task_id"])
    else:
        return {"error": "Unknown tool"}

# MCP Tool Functions
def get_tasks():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/tasks", headers=HEADERS)
    return res.json()

def create_task(title):
    data = {"title": title, "status": "not_started"}
    res = requests.post(f"{SUPABASE_URL}/rest/v1/tasks", headers=HEADERS, json=data)
    return res.json()

def update_task_status(task_id, new_status):
    url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}"
    data = {"status": new_status}
    res = requests.patch(url, headers=HEADERS, json=data)
    return res.json()

def delete_task(task_id):
    url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{task_id}"
    res = requests.delete(url, headers=HEADERS)
    return {"status": "deleted" if res.status_code == 204 else "failed"}
