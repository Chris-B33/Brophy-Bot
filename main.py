import discord
from discord.ext import commands
import openai

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="&", intents=intents)

@bot.event
async def on_ready():
    print("----------------------------------------------")
    print(f"Logged in as:\n{bot.user.name} \n{bot.user.id}")
    print("----------------------------------------------")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"{message.author}: {message.content}")
    print("----------------------------------------------")
    
    await bot.process_commands(message)

@bot.command()
async def echo(ctx, arg):
    await ctx.send(arg)

with open("token.env", "r") as file:
    token = file.read()

bot.run(token)