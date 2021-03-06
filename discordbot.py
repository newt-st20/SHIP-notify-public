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
    getLogChannel = client.get_channel(814791146966220841)
    if message.author.bot:
        return
    if 'sh!' in message.content:
        if message.content == 'sh!':
            await message.channel.send('`sh!`はコマンドです。')
        elif 'neko' in message.content:
            await message.channel.send('にゃーん')
        else:
            await message.channel.send('このコマンドは用意されていません')


@client.event
async def on_raw_reaction_add(payload):
    await client.wait_until_ready()
    entranceMessageId = 814804313535807508
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.add_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.remove_roles(unauthenticatedRole)
        print("complete")
        user = client.get_user(payload.user_id)
        print(user.name, user.discriminator, str(user))
        await roleLogChannel.send(user.mention+'に`authenticated`ロールを付与し、`unauthenticated`ロールを剥奪しました。')


@client.event
async def on_raw_reaction_remove(payload):
    await client.wait_until_ready()
    entranceMessageId = 814804313535807508
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.remove_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.add_roles(unauthenticatedRole)
        print("complete")
        user = client.get_user(payload.user_id)
        print(user.name, user.discriminator, str(user))
        await roleLogChannel.send(user.mention+'から`authenticated`ロールを剥奪し、`unauthenticated`ロールを付与しました。')


@tasks.loop(seconds=1200)
async def loop():
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    getLogChannel = client.get_channel(817400535639916544)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    print(nowHour)
    if nowHour % 6 == 0:
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
        else:
            await getLogChannel.send('連絡事項に更新はありませんでした')
        if len(result[1]) != 0:
            for studyData in result[1]:
                embed = discord.Embed(
                    title="学習教材更新通知", description="取得:"+result[2])
                embed.add_field(name="date", value=studyData[0])
                embed.add_field(name="path", value=studyData[1])
                embed.add_field(name="title", value=studyData[2])
                await studyJuniorChannel.send(embed=embed)
        else:
            await getLogChannel.send('学習教材に更新はありませんでした')


loop.start()


client.run(TOKEN)
