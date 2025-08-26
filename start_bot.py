#!/usr/bin/env python3
import os
import sys
import time

# Check if BOT_TOKEN is available
if not os.getenv("BOT_TOKEN"):
    print("BOT_TOKEN not found. Exiting.")
    sys.exit(0)

# Wait a bit to ensure the environment is fully ready
time.sleep(5)

try:
    # Import and run the bot
    from main import bot, keep_alive
    
    if __name__ == "__main__":
        keep_alive()
        bot.run(os.environ['BOT_TOKEN'])
except Exception as e:
    print(f"Error starting bot: {e}")
    sys.exit(1)
