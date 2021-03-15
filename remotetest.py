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
import wikipedia
from dotenv import load_dotenv
try:
    load_dotenv()
except:
    print("remote")

TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.wait_until_ready()
    wakeLogChannel = client.get_channel(817389202161270794)
    await wakeLogChannel.send('remototest.py 成功')
    game = discord.Game("prefix: [sh!]")
    await client.change_presence(activity=game)
