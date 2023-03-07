#!/usr/bin/env python3
import os
import sys
import docker
import yaml
import asyncio
import discord
from discord.ext import commands
import concurrent.futures

if len(sys.argv) < 2:
    sys.stderr.write(
        f"Usage: {os.path.basename(sys.argv[0])} /path/to/config.yaml")

    sys.exit(1)

config_path = sys.argv[1]
try:
    with open(config_path, encoding="UTF8") as config_file:
        config = yaml.safe_load(config_file)
except IOError as e:
    sys.stderr.write(f"Could not open config file: {e}")
    sys.exit(1)
except yaml.YAMLError as e:
    sys.stderr.write(f"Could not parse config file: {e}")
    sys.exit(1)

try:
    container_names = config["containers"]
    discord_token = config["discord_token"]
    channelid = config["channelid"]
except KeyError as e:
    sys.stderr.write(f"Config file missing parameter: {e}")
    sys.exit(1)


client = commands.Bot(command_prefix="!", intents=discord.Intents.default())
docker_client = docker.from_env()
tasks = []
threads = []
eventqueue = asyncio.Queue()


async def handle_docker_event(event):
    if event.get("Type", "") != 'container':
        return

    from_ = event.get("from", "")
    if from_ not in container_names:
        return

    message = "Container **" + from_ + "** "

    action = event.get("Action", "")
    if action == "die":
        message = f"☠️ {message} died"
    elif action == "start":
        message = f"✅ {message} started"
    elif action == "destroy":
        message = f"💥 {message} was destroyed"
    elif action == "stop":
        message = f"🛑 {message} stopped"
    elif action == "killed":
        message = f"🔪 {message} was killed"
    else:
        return

    print(message)
    channel = client.get_channel(int(channelid))
    if channel:
        await channel.send(message)
    else:
        print("No channel")


async def monitor_events():
    print("Monitoring events")
    loop = asyncio.get_event_loop()
    events = docker_client.events(decode=True)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            event = await loop.run_in_executor(executor, events.next)
            await handle_docker_event(event)


@ client.event
async def on_ready():
    print('Bot is ready.')
    tasks.append(asyncio.create_task(monitor_events()))

# Start the bot
client.run(discord_token)

for thread in threads:
    thread.join()
