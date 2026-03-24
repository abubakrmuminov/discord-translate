import discord
from discord.ext import commands
import logging
import asyncio
import sys
import os
from threading import Thread  # Добавили для Flask
from flask import Flask        # Добавили для Render
from config import Config
from utils.cache import cache
from utils.database import Database

# --- Блок для Render (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run_flask():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True # Поток умрет вместе с основным процессом
    t.start()
# ------------------------------

# Logging Setup
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('TranslatorBot')

class TranslatorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.db: Database = None

    async def setup_hook(self):
        logger.info("🚀 Starting bot...")
        await cache.connect()
        self.db = Database(Config.DB_PATH)
        await self.db.connect()
        await self.load_cogs()
        logger.info("✅ Bot ready!")

    async def load_cogs(self):
        cogs = [
            "cogs.translation",
            "cogs.settings",
            "cogs.word_of_day",
            "cogs.quiz",
            "cogs.language_exchange",
            "cogs.stats",
            "cogs.admin",
        ]

        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"❌ Failed to load {cog}: {e}")

    async def on_ready(self):
        logger.info(f"✅ Logged in as {self.user} (ID: {self.user.id})")
        await self.tree.sync()

    async def close(self):
        logger.info("🛑 Shutting down...")
        await cache.close()
        # Проверка на существование БД перед закрытием
        if self.db:
            await self.db.close()
        await super().close()

async def main():
    if not Config.TOKEN:
        logger.error("❌ DISCORD_TOKEN not found in environment!")
        return

    # ЗАПУСКАЕМ ФЛАСК ПЕРЕД БОТОМ
    logger.info("🌐 Starting keep-alive server...")
    keep_alive()

    bot = TranslatorBot()
    try:
        await bot.start(Config.TOKEN)
    except KeyboardInterrupt:
        pass
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        if os.name == 'nt':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bye!")
