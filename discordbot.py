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
    print('ログインしました')


@client.event
async def on_member_join(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name="beta_welcome")
    embed = discord.Embed(
        title=f"{member.author.name}さんが参加しました", url="https://bit.ly/2JahfiF", color=0x00ffff)
    embed.set_thumbnail(
        url="https://nureyon.com/sample/84/check_mark-2-p53.svg?2020-09-09")
    embed.add_field(name="参加者", value="f{member.author.mention}", inline=False)
    embed.set_footer(text="サーバー参加を検知しました")
    await channel.send(f'{member.author.mention}', embed=embed)


@client.event
async def on_message(message):
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    if message.author.bot:
        return
    if message.content == '/neko':
        await message.channel.send('にゃーん')
    if message.content == '/run':
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


@tasks.loop(seconds=3000)
async def loop():
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    await testChannel.send('時間だよ')
    date = datetime.datetime.now().strftime("%H")
    print(date)
    if date == "21":
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
