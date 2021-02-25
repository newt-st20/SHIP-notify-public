import discord
from discord.ext import tasks
import datetime
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import re
import random

import sqlpush

TOKEN = os.environ['DISCORD_TOKEN']

client = discord.Client()


@client.event
async def on_ready():
    print('ログインしました')


@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    if message.content == '/run':
        result = sqlpush.main()
        await channel.send(result)


@tasks.loop(seconds=3000)
async def loop():
    await client.wait_until_ready()
    channel = client.get_channel(814460143001403423)
    await channel.send('時間だよ')
    date = datetime.datetime.now().strftime("%H")
    print(date)
    if date == "21":
        result = sqlpush.main()
        await channel.send(result)

loop.start()


client.run(TOKEN)
