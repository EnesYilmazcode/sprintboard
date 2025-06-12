#!/usr/bin/env python3

from agent import ai_handle_message, call_mcp
import requests

def test_mcp_connection():
    """Test if MCP server is running and responding"""
    try:
        print("🔍 Testing MCP server connection...")
        result = call_mcp("get_tasks", {})
        print("✅ MCP server is running!")
        print("📋 Current tasks:", result)
        return True
    except Exception as e:
        print("❌ MCP server connection failed:", e)
        print("💡 Make sure to run: uvicorn sprint_board_server:app --reload --port 8000")
        return False

def test_task_creation():
    """Test creating a task"""
    print("\n🧪 Testing task creation...")
    result = call_mcp("create_task", {"title": "Test task from Python"})
    print("📝 Create task result:", result)

def test_ai_agent():
    """Test the full AI agent flow"""
    print("\n🤖 Testing AI agent...")
    print("Input: 'create a task to add mobile compatibility'")
    ai_handle_message("create a task to add mobile compatibility")

if __name__ == "__main__":
    print("🚀 Sprint Board Agent Test\n")
    
    # Test MCP connection first
    if test_mcp_connection():
        test_task_creation()
        test_ai_agent()
    else:
        print("\n🛠️  To fix this:")
        print("1. Make sure your .env file has the correct Supabase credentials")
        print("2. Run the MCP server: uvicorn sprint_board_server:app --reload --port 8000")
        print("3. Run this test again: python test_agent.py") 