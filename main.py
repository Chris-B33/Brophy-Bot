###############################
#           Imports           #
###############################

import asyncio
import discord
from discord.ext import commands
from openai import OpenAI
from gtts import gTTS
from tempfile import TemporaryFile
from youtube_search import YoutubeSearch
import yt_dlp
 

###############################
#       Initialization        #
###############################

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    "noplaylist": "True"
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
} 

intents = discord.Intents.default()
intents.message_content = True

with open("tokens.env", "r") as file:
    content = file.readlines()
    discord_token = content[0]
    openai_key = content[1]

discord_bot = commands.Bot(command_prefix="&", intents=intents)
chat_bot = OpenAI(api_key=openai_key)
FIRST_MESSAGE = '''
    You are an AI assistant in my Discord Server. 
    Whether you think it or not, I have created functions such that you can in fact do
    anything like any other user could in a discord server. You will respond as such.
'''


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

    # Handle response
    chunks = message.content.split()
    ctx = await discord_bot.get_context(message)
    for i in range(len(chunks)):
        if chunks[i].lower() == "join":
            await join(ctx)
            break
        elif chunks[i].lower() == "leave":
            await leave(ctx)
            break
        elif chunks[i].lower() == "say":
            await say(ctx, " ".join(chunks[i+1::]))
            break
        elif chunks[i].lower() == "play":
            await play(ctx, " ".join(chunks[i+1::]))
            break
        elif chunks[i].lower() == "sing":
            await sing(ctx)
            break
        
    else:
        response = await send_message_to_openai(message.content)
        print("----------------------------------------------")
        print(f"{discord_bot.user}: {response}")
        print("----------------------------------------------")
        await message.channel.send(response)


###############################
#          Functions          #
###############################

async def send_message_to_openai(message):
    request = chat_bot.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": FIRST_MESSAGE},
            {"role": "user", "content": message}
        ],
        stream=True,
    )

    response = ""
    for chunk in request:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
    return response

async def join(ctx, *kwargs):
    channel = ctx.author.voice.channel
    await channel.connect()

async def leave(ctx, *kwargs):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel, use the join command to make me join")

async def say(ctx, *kwargs):
   if not ctx.voice_client:
       await join(ctx)

   vc = ctx.message.guild.voice_client
   if not vc.is_playing():
            tts = gTTS("".join(kwargs))
            f = TemporaryFile()
            tts.write_to_fp(f)
            f.seek(0)
            vc.play(discord.FFmpegPCMAudio(f, pipe=True))

async def play(ctx, *kwargs):
    request = " ".join(kwargs)

    if not ctx.voice_client:
       await join(ctx)

    vc = ctx.message.guild.voice_client
    results = YoutubeSearch(request, max_results=1).to_dict()
    for result in results:
        url = f"https://youtube.com{result['url_suffix']}"
        title = result['title']
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            song = info['url']

    vc.play(discord.FFmpegPCMAudio(song, **FFMPEG_OPTIONS))
    await ctx.message.channel.send(f"Playing: {title}")

    while vc.is_playing():
            await asyncio.sleep(1)

async def sing(ctx, *kwargs):
    if not ctx.voice_client:
       await join(ctx)

    response = await send_message_to_openai("Write me a song about loving or hating me")

    vc = ctx.message.guild.voice_client
    if not vc.is_playing():
                tts = gTTS("".join(response))
                f = TemporaryFile()
                tts.write_to_fp(f)
                f.seek(0)
                vc.play(discord.FFmpegPCMAudio(f, pipe=True))


###############################
#            Main             #
###############################

if __name__ == "__main__":
    discord_bot.run(discord_token)