from agent import ai_handle_message

if __name__ == "__main__":
    while True:
        msg = input("🧑 You: ")
        if msg.lower() in ("exit", "quit"):
            break
        ai_handle_message(msg)
