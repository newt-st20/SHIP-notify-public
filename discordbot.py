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


@tasks.loop(seconds=60)
async def loop():
    await client.wait_until_ready()
    channel = client.get_channel(814451345267621888)
    await channel.send('時間だよ')
    now = datetime.now().strftime('%H:%M')
    if now == '06:00':
        channel = client.get_channel(814451345267621888)
        await channel.send('おはよう')
loop.start()


client.run(TOKEN)
