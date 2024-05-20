###############################
#           Imports           #
###############################

import discord
from discord.ext import commands
from openai import OpenAI


###############################
#       Initialization        #
###############################

intents = discord.Intents.default()
intents.message_content = True

with open("tokens.env", "r") as file:
    content = file.readlines()
    discord_token = content[0]
    openai_key = content[1]

chat_bot = OpenAI(api_key=openai_key)
discord_bot = commands.Bot(command_prefix="&", intents=intents)


###############################
#            Events           #
###############################

@discord_bot.event
async def on_ready():
    print("----------------------------------------------")
    print(f"Logged in as:\n{discord_bot.user.name} \n{discord_bot.user.id}")
    print("----------------------------------------------")

@discord_bot.event
async def on_message(message):
    mention = f'<@!{discord_bot.user.id}>'
    if message.author == discord_bot.user or not discord_bot.user.mentioned_in(message):
        return

    # Get message
    print(f"{message.author}: {message.content}")
    print("----------------------------------------------")

    # Send to OpenAI
    request = chat_bot.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are the Trash Man, a pro wrestler. You throw garbage around the arena."},
            {"role": "user", "content": "".join(message.content.split(" ")[1::])}
        ]
    )
    response = request.choices[0].message

    # Handle response
    print(f"{discord_bot.user}: {response}")
    print("----------------------------------------------")
    await message.channel.send(response)


###############################
#             Main            #
###############################

if __name__ == "__main__":
    discord_bot.run(discord_token)