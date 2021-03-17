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

import shipcheck
import shnews
import search

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN']


intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.wait_until_ready()
    wakeLogChannel = client.get_channel(817389202161270794)
    await wakeLogChannel.send('起動しました')
    game = discord.Game("prefix: [sh!]")
    await client.change_presence(activity=game)


@client.event
async def on_member_join(member):
    guild = member.guild
    unauthenticatedRole = guild.get_role(813015195881570334)
    await member.add_roles(unauthenticatedRole)


async def on_member_remove(member):
    await client.wait_until_ready()
    joinLeaveLogChannel = client.get_channel(810813680618831906)
    await joinLeaveLogChannel.send(member.name+"("+member.id+") が退出しました")


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
        elif 'search' in message.content:
            word = message.content.split()[1]
            data = search.main(word)
            if len(data) == 0 or len(data[0][4]) == 0:
                body = "指定されたidに該当するファイルがデータベースに見つかりませんでした"
            else:
                if len(data[0][4]) == 1:
                    body = data[0][4][0]
                else:
                    body = ""
                    for file in data[0][4]:
                        body += file + "\n"
            await message.channel.send(body)
        # メッセージリンク返信
        elif 'sm' in message.content:
            messages = await message.channel.history().flatten()
            for msg in messages:
                if word in msg.content:
                    await message.channel.send(msg.jump_url)
        # Wikipedia検索
        elif 'wiki' in message.content:
            word = message.content.split()[1]
            await message.channel.send('Wikipediaで`'+word+'`を検索...')
            wikipedia.set_lang("ja")
            response = wikipedia.search(word)
            if not response:
                await message.channel.send('Wikipediaで`'+word+'`に関連するページが見つかりませんでした')
            try:
                page = wikipedia.page(response[0])
                content = page.content.splitlines()[0]
                if len(content) > 1000:
                    content = content[0:1000] + "..."
                embed = discord.Embed(title=word)
                embed.add_field(name="wikipediaで検索した結果",
                                value=content.splitlines()[0], inline=False)
                embed.add_field(name="▶リンク",
                                value='['+page.url+']('+page.url+')', inline=False)
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send("エラー:"+str(e))
        elif 'neko' in message.content:
            def check(msg):
                return msg.author == message.author
            await message.channel.send('にゃーん')
            wait_message = await client.wait_for("message", check=check)
            await message.channel.send(wait_message.content)
        else:
            await message.channel.send('このコマンドは用意されていません')
    # 管理者用コマンド
    elif 'sa!' in message.content and message.author.guild_permissions.administrator:
        if 'get' in message.content:
            await message.channel.send('データの取得を開始します')
            try:
                await getData()
            except Exception as e:
                await message.channel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif 'shnews' in message.content:
            await message.channel.send('データの取得を開始します')
            try:
                await getNewsData()
                await getLogChannel.send('処理が完了しました')
            except Exception as e:
                await message.channel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif 'count' in message.content:
            guild = message.guild
            member_count = guild.member_count
            user_count = sum(1 for member in guild.members if not member.bot)
            bot_count = sum(1 for member in guild.members if member.bot)
            await message.channel.send(f'メンバー数：{member_count}\nユーザ数：{user_count}\nBOT数：{bot_count}')
    if isinstance(message.channel, discord.DMChannel):
        user = client.get_user(message.author.id)
        embed = discord.Embed(title="DMを受信しました")
        embed.add_field(name="ユーザー名",
                        value=message.author.mention+str(message.author.id), inline=False)
        embed.add_field(name="本文",
                        value=message.content, inline=False)
        embed.add_field(name="チャンネルID",
                        value=str(message.channel.id), inline=False)
        await dmLogChannel.send(embed=embed)
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


@tasks.loop(seconds=600)
async def loop():
    await client.wait_until_ready()
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    getLogChannel = client.get_channel(817400535639916544)
    configChannel = client.get_channel(820242721330561044)
    announceChannel = client.get_channel(810813852140306442)
    messages = await configChannel.history().flatten()
    for msg in messages:
        if "GET_HOUR=" in msg.content:
            whenGetConfigMessage = msg.content.lstrip("GET_HOUR=")
            continue
    hourList = [int(x) for x in whenGetConfigMessage.split()]
    announceMessage = await announceChannel.fetch_message(818636188084076594)
    if str(hourList) not in str(announceMessage.embeds[0].to_dict()):
        editDatetime = "更新日時: " + str(datetime.datetime.now())
        editedBody = "現在は"+str(hourList) + \
            "時ごろに取得しています。データを取得するタイミングは変更する場合があります。"
        embed = discord.Embed(
            title="データ取得タイミング", description=editDatetime, color=discord.Colour.from_rgb(245, 236, 66))
        embed.add_field(name="SHIPデータを取得する時間",
                        value=editedBody, inline=False)
        await announceMessage.edit(embed=embed)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    nowMinute = int(datetime.datetime.now().strftime("%M"))
    if nowHour in hourList and nowMinute < 10:
        await getLogChannel.send('データの取得を開始します')
        try:
            await getData()
            await getLogChannel.send('処理が完了しました')
        except Exception as e:
            await getLogChannel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))


async def getData():
    await client.wait_until_ready()
    testChannel = client.get_channel(814460143001403423)
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    conHighChannel = client.get_channel(818066947463053312)
    studyHighChannel = client.get_channel(818066981982830613)
    getLogChannel = client.get_channel(817400535639916544)
    result = shipcheck.main()
    if len(result[0]) != 0:
        for conData in result[0]:
            if conData[3] != '':
                embed = discord.Embed(
                    title=conData[3], description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            else:
                embed = discord.Embed(
                    title="中学連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            embed.add_field(name="id", value=conData[0])
            embed.add_field(name="date", value=conData[1])
            if conData[2] != '':
                embed.add_field(name="path", value=conData[2], inline=False)
            if conData[4] != '':
                embed.add_field(name="description",
                                value=conData[4], inline=False)
            await conJuniorChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="中学連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学連絡事項に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)
    if len(result[1]) != 0:
        for studyData in result[1]:
            if studyData[3] != '':
                embed = discord.Embed(
                    title=studyData[3], description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            else:
                embed = discord.Embed(
                    title="中学学習教材更新通知", description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            embed.add_field(name="id", value=studyData[0])
            embed.add_field(name="date", value=studyData[1])
            if studyData[2] != '':
                embed.add_field(name="path", value=studyData[2], inline=False)
            await studyJuniorChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="中学学習教材更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学習教材に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)
    if len(result[2]) != 0:
        for conData in result[2]:
            if conData[3] != '':
                embed = discord.Embed(
                    title=conData[3], description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            else:
                embed = discord.Embed(
                    title="高校連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            embed.add_field(name="id", value=conData[0])
            embed.add_field(name="date", value=conData[1])
            if conData[2] != '':
                embed.add_field(name="path", value=conData[2], inline=False)
            if conData[4] != '':
                embed.add_field(name="description",
                                value=conData[4], inline=False)
            await conHighChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="高校連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校連絡事項に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)
    if len(result[3]) != 0:
        for studyData in result[3]:
            if studyData[3] != '':
                embed = discord.Embed(
                    title=result[3], description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            else:
                embed = discord.Embed(
                    title="高校学習教材更新通知", description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            embed.add_field(name="id", value=studyData[0])
            embed.add_field(name="date", value=studyData[1])
            if studyData[2] != '':
                embed.add_field(name="path", value=studyData[2], inline=False)
            await studyHighChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="高校学習教材更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学習教材に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)


async def getNewsData():
    await client.wait_until_ready()
    shnewsChannel = client.get_channel(814460143001403423)
    getLogChannel = client.get_channel(817400535639916544)
    result = shnews.main()
    if len(result[0]) != 0:
        for conData in result[0]:
            embed = discord.Embed(
                title="栄東ニュース更新通知", description="取得日時:"+result[1], color=discord.Colour.from_rgb(52, 235, 79))
            embed.add_field(name="title", value=conData[0], inline=False)
            embed.add_field(name="datetime", value=conData[1])
            embed.add_field(name="category", value=conData[4], inline=False)
            embed.add_field(name="body", value=conData[2], inline=False)
            embed.add_field(name="link", value=conData[3], inline=False)
            await shnewsChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="栄東ニュース更新通知", description="取得日時:"+result[1], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='栄東ニュースに更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)

loop.start()


client.run(TOKEN)
