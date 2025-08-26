import os
import sys

if not os.getenv("BOT_TOKEN"):
    print("BOT_TOKEN not found. Exiting.")
    sys.exit(0)

from main import bot, keep_alive

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ['BOT_TOKEN'])
