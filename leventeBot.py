import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)


pinging = {}
dcId= None

@bot.command()
async def ping(ctx, member: discord.Member):
    try:
        global dcId
        dcId = member.id
        if member.voice and member.voice.channel:
            await ctx.send(f"{member.display_name} hangcsatornában van, leállítom a pingelést.")
            await stop(ctx)
            return
        
        #print(ctx.author.id, member.id)
        if ctx.channel.id in pinging:
            await ctx.send("Már pingelek valakit ebben a csatornában. Írd be, hogy `!stop`!")
            return


        await ctx.send(f"Elkezdtem pingelni {member.mention}-t. Írd be `!stop`, ha elég!")
        pinging[ctx.channel.id] = {
            "member": member,
            "task": bot.loop.create_task(ping_loop(ctx, member))
        }
    except:
        await ctx.send("Hiba")

async def ping_loop(ctx, member):
    try:
        while True:
            await ctx.send(f"{member.mention}")
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass

@bot.event
async def on_voice_state_update(member, before, after):
    # Did the user join a voice channel?
    if before.channel is None and after.channel is not None:
        for channel_id, info in list(pinging.items()):
            if info["member"].id == member.id:
                # Stop pinging if the pinged user joined a voice channel
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send(f"{member.display_name} belépett egy hangcsatornába, leállítom a pingelést.")
                info["task"].cancel()
                del pinging[channel_id]

@bot.command()
async def stop(ctx):
    if ctx.channel.id in pinging:
        print(ctx.author.id, dcId)
        if ctx.author.id == dcId:
            await ctx.send("Beszoptad haha, nem állítom le a pingelést.")
            return
        pinging[ctx.channel.id]["task"].cancel()
        del pinging[ctx.channel.id]
        await ctx.send("Leállítottam a pingelést.")
    else:
        await ctx.send("Nem pingelek senkit ebben a csatornában.")

@bot.event
async def on_ready():
    print(f'Bejelentkezve mint {bot.user}')

bot.run(token)