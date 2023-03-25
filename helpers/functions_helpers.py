import json
import os
import functools
import typing
import asyncio
import logging

import google.auth
from googleapiclient.discovery import build

logging.basicConfig(level = logging.INFO)


def open_json():
    with open("youtube_data.json", 'r') as file:
        data = json.load(file)
    return data


def save_json(data):
    with open("youtube_data.json", "w") as file:
        json.dump(data, file)
    return data


def get_last_video_id_from_channel(youtube_channel):    
    # Set up the API client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/jisu-calenrondo-a823d04b62e8.json"
    credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/youtube.readonly"])
    youtube = build("youtube", "v3", credentials=credentials)

    # Get the channel details
    logging.info("API get channels")
    channel_id = youtube_channel
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    # Extract the ID of the latest uploaded video
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    logging.info("API get last video")
    response = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=1
    ).execute()

    # Get the last video id
    latest_video_id = response["items"][0]["snippet"]["resourceId"]["videoId"]
    return latest_video_id


def build_msg(channel_name, latest_video_url):
    msg = "@everyone Ici Jisu CALENRONDO, en direct du journal de Néomuna !\n"
    msg += f"Une nouvelle vidéo de la chaîne de {channel_name} viens d'être mise en ligne\n{latest_video_url}"
    return msg


async def send_msg_to_discord_channel(client, id_channel, msg):
    discord_channel = client.get_channel(id_channel)
    await discord_channel.send(msg)
