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

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.wait_until_ready()
    wakeLogChannel = client.get_channel(817389202161270794)
    await wakeLogChannel.send('起動しました')


@client.event
async def on_member_join(member):
    guild = member.guild
    unauthenticatedRole = guild.get_role(813015195881570334)
    await member.add_roles(unauthenticatedRole)


@client.event
async def on_message(message):
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    if message.author.bot:
        return
    if 'sh!' in message.content:
        if 'neko' in message.content:
            await message.channel.send('にゃーん')
        elif 'run' in message.content:
            result = sqlpush.main()
            if len(result[0]) != 0:
                for conData in result[0]:
                    embed = discord.Embed(
                        title="連絡事項更新通知", description="取得:"+result[2])
                    embed.add_field(name="date", value=conData[0])
                    embed.add_field(name="path", value=conData[1])
                    embed.add_field(name="title", value=conData[2])
                    try:
                        embed.add_field(name="description", value=conData[3])
                    except:
                        print("no data")
                    await conJuniorChannel.send(embed=embed)
            if len(result[1]) != 0:
                for studyData in result[1]:
                    embed = discord.Embed(
                        title="学習教材更新通知", description="取得:"+result[2])
                    embed.add_field(name="date", value=studyData[0])
                    embed.add_field(name="path", value=studyData[1])
                    embed.add_field(name="title", value=studyData[2])
                    await studyJuniorChannel.send(embed=embed)
        else:
            await message.channel.send('このコマンドは用意されていません')


@client.event
async def on_raw_reaction_add(payload):
    await client.wait_until_ready()
    entranceMessageId = 814804313535807508
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.add_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.remove_roles(unauthenticatedRole)
        print("complete")


@client.event
async def on_raw_reaction_remove(payload):
    await client.wait_until_ready()
    entranceMessageId = 814804313535807508
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.remove_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.add_roles(unauthenticatedRole)
        print("complete")


@tasks.loop(seconds=1200)
async def loop():
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    print(nowHour)
    if nowHour % 2 == 0:
        result = sqlpush.main()
        if len(result[0]) != 0:
            for conData in result[0]:
                embed = discord.Embed(
                    title="連絡事項更新通知", description="取得:"+result[2])
                embed.add_field(name="date", value=conData[0])
                embed.add_field(name="path", value=conData[1])
                embed.add_field(name="title", value=conData[2])
                try:
                    embed.add_field(name="description", value=conData[3])
                except:
                    print("no data")
                await conJuniorChannel.send(embed=embed)
        if len(result[1]) != 0:
            for studyData in result[1]:
                embed = discord.Embed(
                    title="学習教材更新通知", description="取得:"+result[2])
                embed.add_field(name="date", value=studyData[0])
                embed.add_field(name="path", value=studyData[1])
                embed.add_field(name="title", value=studyData[2])
                await studyJuniorChannel.send(embed=embed)

loop.start()


client.run(TOKEN)
