import os
import discord
import mysql.connector
from typing import Final
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
load_dotenv()

intents: Intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Database config
DATABASE_PASS: Final[str] = os.getenv('DATABASE_PASS')
uscmc_db = {
    'host': 'localhost',
    'user': 'root',
    'password': DATABASE_PASS,
    'db': 'uscmc'
}

# Database connection
# uscmc_db_conn = mysql.connector.connect(**uscmc_db)

# Init commands
bot.load_extension("commands")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

bot.run(os.getenv('DISCORD_TOKEN'))