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
        elif 'search' in message.content:
            await message.channel.send('検索')
        elif 'count' in message.content:
            guild = message.guild
            member_count = guild.member_count
            user_count = sum(1 for member in guild.members if not member.bot)
            bot_count = sum(1 for member in guild.members if member.bot)
            await message.channel.send(f'メンバー数：{member_count}\nユーザ数：{user_count}\nBOT数：{bot_count}')
        elif 'neko' in message.content:
            await message.channel.send('にゃーん')
        elif 'get' in message.content:
            if message.author.guild_permissions.administrator:
                await message.channel.send('データの取得を開始します')
                try:
                    await getData()
                except Exception as e:
                    await message.channel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
            else:
                await message.channel.send('このコマンドは管理者のみ利用することができます')
        elif 'members' in message.content:
            if message.author.guild_permissions.administrator:
                await message.channel.send(message.guild.members)
            else:
                await message.channel.send('このコマンドは管理者のみ利用することができます')
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
    if nowHour % 6 == 0 and nowMinute < 10:
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
    result = sqlpush.main()
    if len(result[0]) != 0:
        for conData in result[0]:
            embed = discord.Embed(
                title="連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            embed.add_field(name="id", value=conData[0])
            embed.add_field(name="date", value=conData[1])
            if conData[2] != '':
                embed.add_field(name="path", value=conData[2], inline=False)
            else:
                embed.add_field(name="path", value="(トップフォルダ)", inline=False)
            if conData[3] != '':
                embed.add_field(name="title", value=conData[3], inline=False)
            else:
                embed.add_field(name="title", value="(タイトルなし)", inline=False)
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
            embed = discord.Embed(
                title="中学学習教材更新通知", description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            embed.add_field(name="id", value=studyData[0])
            embed.add_field(name="date", value=studyData[1])
            if studyData[2] != '':
                embed.add_field(name="path", value=studyData[2], inline=False)
            else:
                embed.add_field(name="path", value="(トップフォルダ)", inline=False)
            if studyData[3] != '':
                embed.add_field(name="title", value=studyData[3], inline=False)
            else:
                embed.add_field(name="title", value="(タイトルなし)", inline=False)
            await studyJuniorChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="中学学習教材更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学習教材に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)
    if len(result[2]) != 0:
        for conData in result[2]:
            embed = discord.Embed(
                title="高校連絡事項更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
            embed.add_field(name="id", value=conData[0])
            embed.add_field(name="date", value=conData[1])
            if conData[2] != '':
                embed.add_field(name="path", value=conData[2], inline=False)
            if conData[3] != '':
                embed.add_field(name="title", value=conData[3], inline=False)
            else:
                embed.add_field(name="title", value="(タイトルなし)", inline=False)
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
            embed = discord.Embed(
                title="高校学習教材更新通知", description="取得:"+result[4], color=discord.Colour.from_rgb(52, 229, 235))
            embed.add_field(name="id", value=studyData[0])
            embed.add_field(name="date", value=studyData[1])
            if studyData[2] != '':
                embed.add_field(name="path", value=studyData[2], inline=False)
            else:
                embed.add_field(name="path", value="(トップフォルダ)", inline=False)
            if studyData[3] != '':
                embed.add_field(name="title", value=studyData[3], inline=False)
            else:
                embed.add_field(name="title", value="(タイトルなし)", inline=False)
            await studyHighChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="高校学習教材更新通知", description="取得日時:"+result[4], color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学習教材に更新はありませんでした', inline=False)
        await getLogChannel.send(embed=embed)

loop.start()


client.run(TOKEN)
