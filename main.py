import discord
import openai

intents = discord.Intents.default()
intents.message_content = True

class BrophyBot(discord.Client):
    async def on_ready(self):
        print("Loaded in.")

    async def on_message(self):
        print("new message")

if __name__ == "__main__":
    with open("token.env", "r") as file:
        token = file.read()

    client = BrophyBot(intents=intents)
    client.run(token)