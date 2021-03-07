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
    dmLogChannel = client.get_channel(817971315138756619)
    if message.author.bot:
        return
    elif 'sh!' in message.content:
        if message.content == 'sh!':
            await message.channel.send('`sh!`はコマンドです。')
        elif 'neko' in message.content:
            await message.channel.send('にゃーん')
        else:
            await message.channel.send('このコマンドは用意されていません')
    if isinstance(message.channel, discord.DMChannel):
        user = client.get_user(message.author.id)
        await dmLogChannel.send("from: "+str(message.author)+" ( "+str(message.author.id)+" ) \nbody: "+str(message.content)+"\nchannel-id: "+str(message.channel.id))
    if message.channel == dmLogChannel and message.author.guild_permissions.administrator and 'reply!' in message.content:
        replyDmChannel = client.get_channel(int(message.content.split('!')[1]))
        sendMessage = str(message.content.split('!')[2])
        await replyDmChannel.send(sendMessage)


@client.event
async def on_raw_reaction_add(payload):
    await client.wait_until_ready()
    entranceMessageId = 817952115095109633
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.add_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.remove_roles(unauthenticatedRole)
        user = client.get_user(payload.user_id)
        await roleLogChannel.send(user.mention+'に'+authenticatedRole.mention+'ロールを付与し、'+unauthenticatedRole.mention+'ロールを剥奪しました。')


@client.event
async def on_raw_reaction_remove(payload):
    await client.wait_until_ready()
    entranceMessageId = 817952115095109633
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        authenticatedRole = guild.get_role(813014134001500170)
        await member.remove_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.add_roles(unauthenticatedRole)
        user = client.get_user(payload.user_id)
        await roleLogChannel.send(user.mention+'から'+authenticatedRole.mention+'ロールを剥奪し、'+unauthenticatedRole.mention+'ロールを付与しました。')


@tasks.loop(seconds=600)
async def loop():
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    getLogChannel = client.get_channel(817400535639916544)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    nowMinute = int(datetime.datetime.now().strftime("%M"))
    print(nowMinute)
    if nowHour % 6 == 0 and nowMinute < 10:
        result = sqlpush.main()
        if len(result[0]) != 0:
            for conData in result[0]:
                embed = discord.Embed(
                    title="連絡事項更新通知", description="取得:"+result[2], color=discord.Colour.from_rgb(52, 235, 79))
                embed.add_field(name="date", value=conData[0], inline=False)
                embed.add_field(name="path", value=conData[1], inline=False)
                embed.add_field(name="title", value=conData[2], inline=False)
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
                    title="学習教材更新通知", description="取得:"+result[2], color=discord.Colour.from_rgb(52, 229, 235))
                embed.add_field(name="date", value=studyData[0], inline=False)
                embed.add_field(name="path", value=studyData[1], inline=False)
                embed.add_field(name="title", value=studyData[2], inline=False)
                await studyJuniorChannel.send(embed=embed)
        else:
            await getLogChannel.send('学習教材に更新はありませんでした')


loop.start()


client.run(TOKEN)
