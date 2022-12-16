import os
from uuid import uuid4

import functions_framework as ff
import telegram
import youtube_dl
from flask import Request


def download_video(url: str, filename: str):
    # create the youtube_dl object  with the best quality preset
    ydl = youtube_dl.YoutubeDL({'outtmpl': f'{filename}'}, {'format': 'best'})
    # download the video
    ydl.download([url])


@ff.http
def get_video(request: Request):
    # Get the telegram message from the request
    update = request.get_json()
    print(update)
    if not update:
        return "Handled", 200

    # get api token from environment variable
    API_TOKEN = os.environ['API_TOKEN']
    bot = telegram.Bot(token=API_TOKEN)

    if 'message' not in update:
        return "Handled", 200

    message = update['message']

    # Restrict the function to only work for me
    if message['from']['id'] != int(os.environ['PERSONAL_ID']):
        bot.sendMessage(chat_id=message['chat']['id'], text="You are not allowed to use this bot")
        return "Handled", 200

    if message['text'] == '/start':
        bot.sendMessage(chat_id=message['chat']['id'], text="Welcome to the Reddit Video Downloader Bot")
        return "Handled", 200

    if not message['text'].startswith('https://www.reddit.com'):
        bot.sendMessage(chat_id=message['chat']['id'], text="Please send a reddit post url")
        return "Handled", 200

    # generate random video name with uuid
    video_name = f'/tmp/video{str(uuid4())}.mp4'
    download_video(message['text'], video_name)

    # check if the video is more than 50MB
    if os.path.getsize(video_name) > 52428800:
        bot.sendMessage(chat_id=message['chat']['id'], text="The video is too big")
        # delete the video
        os.remove(video_name)
        return "Handled", 200

    # send the video to the chat
    bot.send_video(chat_id=message['chat']['id'], video=open(video_name, 'rb'))
    # delete the video
    os.remove(video_name)
    return "Handled", 200
