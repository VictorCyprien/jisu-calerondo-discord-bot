import os
from dotenv import load_dotenv
import time
import logging

import discord
from discord.ext import commands, tasks

from helpers.functions_helpers import (
    open_json,
    save_json,
    get_last_video_id_from_channel,
    build_msg,
    send_msg_to_discord_channel
)

intents = discord.Intents.all()

client = commands.Bot(
    command_prefix="/", 
    description="Ici Jisu CALENRONDO, en direct du journal de Néomuna", 
    intents=intents
)

logging.basicConfig(level = logging.INFO)

@client.event
async def on_ready():
    await client.wait_until_ready()
    logging.info("Ici Jisu CALENRONDO, en direct du journal de Néomuna !")
    try:
        synced = await client.tree.sync()
        logging.info(f"Synced : {len(synced)} command(s) !")
    except Exception as e:
        logging.info(e)


@client.tree.command(name="talk")
async def talk(interaction: discord.Interaction):
    """ Talk to Jisu !
    """
    await interaction.response.send_message("Ici Jisu CALENRONDO, en direct du journal de Néomuna !")


# Check every video every 10 minutes
@tasks.loop(minutes=10)
async def check_new_videos():
    data = open_json()
    logging.info("Checking for new videos...")
    for youtube_channel in data:
        logging.info(f"Channel id : {youtube_channel}")
        latest_video_id = get_last_video_id_from_channel(youtube_channel)
        logging.info(f"Latest video ID : {latest_video_id}")
        latest_video_url = f"https://www.youtube.com/watch?v={latest_video_id}"

        if str(data[youtube_channel]["latest_video_url"]) != latest_video_url:
            logging.info("New video !\nPosting to channel...")
            # Update last video url
            data[str(youtube_channel)]['latest_video_url'] = latest_video_url

            # Save new data
            data = save_json(data)

            # Get discord channel ID and Youtube channel name
            discord_channel_id = data[str(youtube_channel)]['notifying_discord_channel']
            channel_name = data[str(youtube_channel)]['channel_name']

            # Build message and send it to discord channel
            msg = build_msg(channel_name, latest_video_url)
            await send_msg_to_discord_channel(client, discord_channel_id, msg)
            logging.info("Posted to channel !")
        else:
            logging.info("No new video, proceed...")
        time.sleep(5)
    logging.info("Finished !")
    logging.info("Retrying in 10 minutes !")


@client.tree.command(name="add_youtube_channel")
@commands.has_role("Administrateur Echo[Systèmes]")
async def add_youtube_channel(interaction: discord.Interaction, channel_id: str, channel_name: str):
    data = open_json()

    # Check if channel exist in json file
    for channel in data:
        if data[channel]["channel_name"] == channel_name:
            await interaction.response.send_message(f"La chaîne de {channel_name} est déjà dans mon répertoire !")
            return

    # Add new channel in json file
    data[str(channel_id)] = {}
    data[str(channel_id)]["channel_name"] = channel_name
    data[str(channel_id)]["latest_video_url"] = "None"
    data[str(channel_id)]["notifying_discord_channel"]= 697858472548761692

    data = save_json(data)
    await interaction.response.send_message(f"Je viens d'ajouter la chaîne Youtube {channel_name} à mon répertoire !")


@client.tree.command(name="remove_youtube_channel")
@commands.has_role("Administrateur Echo[Systèmes]")
async def remove_youtube_channel(interaction: discord.Interaction, channel_name: str):
    data = open_json()

    # Check if channel exist in json file 
    for channel in data:
        if data[channel]["channel_name"] == channel_name:
            del data[channel]
            data = save_json(data)
            await interaction.response.send_message(f"Je retire la chaîne de {channel_name} de ma liste de notification !")
            return
        
    await interaction.response.send_message(f"La chaine {channel_name} n'est pas dans ma liste de notification !")


@client.tree.command(name="stop_notifying")
@commands.has_role("Administrateur Echo[Systèmes]")
async def stop_notifying(interaction: discord.Interaction):
    check_new_videos.stop()
    await interaction.response.send_message("Les notifications vidéos sont maintenant suspendus")


@client.tree.command(name="start_notifying")
@commands.has_role("Administrateur Echo[Systèmes]")
async def start_notifying(interaction: discord.Interaction):
    await interaction.response.send_message("Je vais maintenant notifier les nouvelles vidéos mise en ligne")
    check_new_videos.start()

load_dotenv(dotenv_path="config")
client.run(os.getenv("TOKEN"))
