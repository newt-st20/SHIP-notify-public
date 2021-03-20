import datetime
import json
import os
import random
import re

import discord
import requests
import wikipedia
from bs4 import BeautifulSoup
from discord.ext import tasks
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import search
import shipcheck
import shnews

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.wait_until_ready()
    wakeLogChannel = client.get_channel(817389202161270794)
    wakeMessage = os.environ['STATUS'] + ": 起動しました"
    await wakeLogChannel.send(wakeMessage)
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
    dmLogChannel = client.get_channel(817971315138756619)
    conHighChannel = client.get_channel(818066947463053312)
    studyHighChannel = client.get_channel(818066981982830613)
    if message.author.bot:
        return
    if 'sh!' in message.content:
        if message.content == 'sh!':
            await message.channel.send('`sh!`はコマンドです。')
        elif 'info' in message.content or message.content == 'sh!i':
            def check(msg):
                return msg.author == message.author
            try:
                embed = discord.Embed(title="情報取得", description="情報を取得したいもののidを入力してください。idは通知チャンネル("+conHighChannel.mention +
                                      ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(190, 252, 3))
                await message.channel.send(embed=embed)
                idMessage = await client.wait_for("message", check=check, timeout=60)
                try:
                    idMessageTyped = int(idMessage.content)
                except:
                    await message.channel.send("入力された文字は数字ではありません。最初からやり直してください。")
                    pass
                data = search.info(idMessageTyped)
                if len(data) == 0:
                    embed = discord.Embed(
                        title=idMessage.content, description="指定されたidに該当するファイルがデータベースに見つかりませんでした")
                else:
                    body = "`page` "+data[0][4]+"\n"
                    body += "`id` "+idMessage.content+"\n"
                    body += "`date` "+str(data[0][1]).replace("-", "/")+"\n"
                    body += "`folder` "+data[0][2]+"\n"
                    linkList = str(data[0][3])[1:-1].split(",")
                    body += "`file` "+str(len(linkList))+"\n"
                    if data[0][4] == "高校連絡事項":
                        body += "`link` https://ship.sakae-higashi.jp/sub_window_anke/?obj_id=" + \
                            idMessage.content+"&t=3\n"
                    elif data[0][4] == "高校学習教材":
                        body += "`link` https://ship.sakae-higashi.jp/sub_window_study/?obj_id=" + \
                            idMessage.content+"&t=7\n"
                    body += "※リンクはSHIPにログインした状態でのみ開けます"
                    embed = discord.Embed(
                        title=data[0][0], description=body, color=discord.Colour.from_rgb(190, 252, 3))
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send("セッションがタイムアウトしました:"+str(e))
        elif 'file' in message.content or 'download' in message.content or message.content == 'sh!f' or message.content == 'sh!d':
            def check(msg):
                return msg.author == message.author
            try:
                embed = discord.Embed(title="ファイル取得", description="ダウンロードリンクを表示したいもののidを入力してください。idは通知チャンネル("+conHighChannel.mention +
                                      ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(50, 168, 82))
                await message.channel.send(embed=embed)
                idMessage = await client.wait_for("message", check=check, timeout=60)
                data = search.__file__(int(idMessage.content))
                if len(data) == 0 or str(data[0][1]) == "{}":
                    embed = discord.Embed(
                        description="指定されたidに該当するファイルがデータベースに見つかりませんでした")
                else:
                    linkList = str(data[0][1])[1:-1].split(",")
                    body = ""
                    lc = 1
                    for link in linkList:
                        body += "`" + str(lc) + ".` " + link + "\n"
                        lc += 1
                    embed = discord.Embed(
                        title=data[0][0]+" - "+str(data[0][2]).replace("-", "/"), description=body, color=discord.Colour.from_rgb(50, 168, 82))
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send("セッションがタイムアウトしました:"+str(e))
        elif 'recently' in message.content or message.content == 'sh!r':
            def check(msg):
                return msg.author == message.author
            embed = discord.Embed(title="最近の更新の取得",
                                  description="高校連絡事項→ `1`\n高校学習教材→ `2`", color=discord.Colour.from_rgb(252, 186, 3))
            await message.channel.send(embed=embed)
            try:
                typeMessage = await client.wait_for("message", check=check, timeout=60)
                data = search.count(int(typeMessage.content))
                if data == 0:
                    embed = discord.Embed(
                        description="指定されたtypeに該当するオブジェクトがデータベースに見つかりませんでした")
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(str(data)+"件のデータが見つかりました。何件表示しますか？(最大50件まで)")
                    try:
                        howmany = await client.wait_for("message", check=check, timeout=60)
                        mainData = search.recently(
                            int(typeMessage.content), int(howmany.content))
                        body = ""
                        lc = 1
                        for eachData in mainData:
                            body += "`" + str(eachData[2]) + "` __**" + eachData[0] + "**__ - " + str(
                                eachData[1].strftime('%Y/%m/%d')) + "\n"
                            if int(howmany.content) == lc:
                                break
                            lc += 1
                        if body == "":
                            body = "empty"
                        if int(typeMessage.content) == 1:
                            titlebody = "最近の高校連絡事項"
                        elif int(typeMessage.content) == 2:
                            titlebody = "最近の高校学習教材"
                        embed = discord.Embed(
                            title=titlebody, description=body, color=discord.Colour.from_rgb(252, 186, 3))
                        await message.channel.send(embed=embed)
                    except Exception as e:
                        await message.channel.send("セッションがタイムアウトしました:"+str(e))
            except Exception as e:
                await message.channel.send("セッションがタイムアウトしました:"+str(e))
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
    if 'sa!' in message.content and message.author.guild_permissions.administrator:
        if message.content == 'sa!get':
            await message.channel.send('データの取得を開始します')
            try:
                await getData()
                await message.channel.send('処理が完了しました')
            except Exception as e:
                await message.channel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif message.content == 'sa!shnews':
            await message.channel.send('データの取得を開始します')
            try:
                await getNewsData()
                await message.channel.send('処理が完了しました')
            except Exception as e:
                await message.channel.send('エラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif message.content == 'sa!count':
            guild = message.guild
            member_count = guild.member_count
            user_count = sum(1 for member in guild.members if not member.bot)
            bot_count = sum(1 for member in guild.members if member.bot)
            await message.channel.send(f'メンバー数：{member_count}\nユーザ数：{user_count}\nBOT数：{bot_count}')
    if isinstance(message.channel, discord.DMChannel):
        embed = discord.Embed(title="DMを受信しました")
        embed.add_field(name="ユーザー名",
                        value=message.author.mention+" ("+str(message.author.id)+")", inline=False)
        embed.add_field(name="本文",
                        value=message.content, inline=False)
        embed.add_field(name="チャンネルID",
                        value=str(message.channel.id), inline=False)
        await dmLogChannel.send(embed=embed)
    if message.channel == dmLogChannel and message.author.guild_permissions.administrator and 'reply!' in message.content:
        replyDmChannel = client.get_channel(int(message.content.split('!')[1]))
        sendMessage = str(message.content.split('!')[2])
        await replyDmChannel.send(sendMessage)
    if "https://discord.com/channels/" in message.content:
        messageChannel = message.content.split("/")[-2]
        messageId = message.content.split("/")[-1]
        oldchannel = client.get_channel(int(messageChannel))
        oldmessage = await oldchannel.fetch_message(int(messageId))
        if str(message.type) == "MessageType.default":
            if len(oldmessage.attachments) != 0:
                if oldmessage.content == "":
                    body = oldmessage.attachments[0].filename
                else:
                    body = oldmessage.content+"," + \
                        oldmessage.attachments[0].filename
                embed = discord.Embed(timestamp=oldmessage.created_at,
                                      description=body)
                embed.set_image(url=str(oldmessage.attachments[0].url))
            elif oldmessage.content != "":
                embed = discord.Embed(timestamp=oldmessage.created_at,
                                      description=oldmessage.content)
            elif oldmessage.embeds:
                embed = discord.Embed(timestamp=oldmessage.created_at,
                                      description="リッチメッセージ")
            else:
                embed = discord.Embed(timestamp=oldmessage.created_at,
                                      description="システムメッセージ")
        embed.set_author(name=oldmessage.author.name,
                         icon_url=oldmessage.author.avatar_url)
        embed.set_footer(text=oldchannel.name+"チャンネルでのメッセージ")
        await message.channel.send(embed=embed)


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
    getLogChannel = client.get_channel(817400535639916544)
    configChannel = client.get_channel(820242721330561044)
    ruleChannel = client.get_channel(821735577383731231)
    messages = await configChannel.history().flatten()
    for msg in messages:
        if "GET_HOUR=" in msg.content:
            whenGetConfigMessage = msg.content.lstrip("GET_HOUR=")
            continue
    hourList = [int(x) for x in whenGetConfigMessage.split()]
    announceMessage = await ruleChannel.fetch_message(821736777391538206)
    if str(hourList) not in str(announceMessage.embeds[0].to_dict()):
        editDatetime = "更新日時: " + \
            str(announceMessage.edited_at.strftime("%Y/%m/%d %H:%M:%S"))
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
            await getLogChannel.send('【SHIP】\nエラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        if random.randrange(10) == 0:
            await getLogChannel.send('栄東ニュースの取得を開始します')
            try:
                await getNewsData()
                await getLogChannel.send('栄東ニュースの取得処理が完了しました')
            except Exception as e:
                await getLogChannel.send('【栄東ニュース】\nエラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))


async def getData():
    await client.wait_until_ready()
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    conHighChannel = client.get_channel(818066947463053312)
    studyHighChannel = client.get_channel(818066981982830613)
    getLogChannel = client.get_channel(817400535639916544)
    result = shipcheck.main()
    if len(result[0]) != 0:
        for conData in result[0]:
            try:
                if conData[3] != '':
                    embed = discord.Embed(
                        title=conData[3], description="投稿: "+conData[1], color=discord.Colour.from_rgb(52, 235, 79))
                else:
                    embed = discord.Embed(
                        title="中学連絡事項更新通知", description="投稿: "+conData[1], color=discord.Colour.from_rgb(52, 235, 79))
                embed.add_field(name="id", value=conData[0])
                if conData[2] != '':
                    embed.add_field(name="path", value=conData[2])
                if conData[4] != '':
                    embed.add_field(name="description",
                                    value=conData[4], inline=False)
                embed.set_footer(text="取得: "+result[4])
                await conJuniorChannel.send(embed=embed)
            except Exception as e:
                await conJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学連絡事項更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log", value='中学連絡事項に更新はありませんでした')
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)
    if len(result[1]) != 0:
        for studyData in result[1]:
            try:
                if studyData[3] != '':
                    embed = discord.Embed(
                        title=studyData[3], description="投稿: "+studyData[1], color=discord.Colour.from_rgb(52, 229, 235))
                else:
                    embed = discord.Embed(
                        title="中学学習教材更新通知", description="投稿: "+studyData[1], color=discord.Colour.from_rgb(52, 229, 235))
                embed.add_field(name="id", value=studyData[0])
                if studyData[2] != '':
                    embed.add_field(name="path", value=studyData[2])
                embed.set_footer(text="取得: "+result[4])
                await studyJuniorChannel.send(embed=embed)
            except Exception as e:
                await studyJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学学習教材更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学習教材に更新はありませんでした')
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)
    if len(result[2]) != 0:
        for conData in result[2]:
            try:
                if conData[3] != '':
                    embed = discord.Embed(
                        title=conData[3], description="投稿: "+conData[1], color=discord.Colour.from_rgb(52, 235, 79))
                else:
                    embed = discord.Embed(
                        title="高校連絡事項更新通知", description="投稿: "+conData[1], color=discord.Colour.from_rgb(52, 235, 79))
                embed.add_field(name="id", value=conData[0])
                if conData[2] != '':
                    embed.add_field(name="path", value=conData[2])
                if conData[4] != '':
                    embed.add_field(name="description",
                                    value=conData[4], inline=False)
                embed.set_footer(text="取得: "+result[4])
                await conHighChannel.send(embed=embed)
            except Exception as e:
                await conHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校連絡事項更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校連絡事項に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)
    if len(result[3]) != 0:
        for studyData in result[3]:
            try:
                if studyData[3] != '':
                    embed = discord.Embed(
                        title=studyData[3], description="投稿: "+studyData[1], color=discord.Colour.from_rgb(52, 229, 235))
                else:
                    embed = discord.Embed(
                        title="高校学習教材更新通知", description="投稿: "+studyData[1], color=discord.Colour.from_rgb(52, 229, 235))
                embed.add_field(name="id", value=studyData[0])
                if studyData[2] != '':
                    embed.add_field(name="path", value=studyData[2])
                embed.set_footer(text="取得: "+result[4])
                await studyHighChannel.send(embed=embed)
            except Exception as e:
                await studyHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校学習教材更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学習教材に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)


async def getNewsData():
    await client.wait_until_ready()
    shnewsChannel = client.get_channel(818480374334226443)
    getLogChannel = client.get_channel(817400535639916544)
    result = shnews.main()
    if len(result[0]) != 0:
        for conData in result[0]:
            embed = discord.Embed(
                title=conData[0], description="投稿日時: "+conData[1], color=discord.Colour.from_rgb(230, 32, 226))
            embed.add_field(name="category", value=conData[4])
            embed.add_field(name="body", value=conData[2], inline=False)
            if len(conData[5]) != 0:
                embed.set_image(url=conData[5][0])
            embed.add_field(name="link", value=conData[3], inline=False)
            embed.set_footer(text="取得: "+result[1])
            await shnewsChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="栄東ニュース更新通知", color=discord.Colour.from_rgb(230, 32, 226))
        embed.add_field(name="system-log",
                        value='栄東ニュースに更新はありませんでした')
        embed.set_footer(text="取得: "+result[1])
        await getLogChannel.send(embed=embed)


loop.start()


client.run(TOKEN)
