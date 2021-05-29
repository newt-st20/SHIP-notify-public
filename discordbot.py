import datetime
import json
import os
import random

import discord
import requests
import wikipedia
from discord.ext import tasks
from dotenv import load_dotenv
import urllib.request

import search
import shipcheck
import shnews
import line
import narou

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']


def isint(s):
    try:
        int(s, 10)
    except ValueError:
        return False
    else:
        return True


intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.wait_until_ready()
    wakeLogChannel = client.get_channel(817389202161270794)
    wakeMessage = os.environ['STATUS'] + ": 起動しました"
    await wakeLogChannel.send(wakeMessage)
    game = discord.Game("commands: sh!help")
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
    def check(msg):
        return msg.author == message.author

    await client.wait_until_ready()
    dmLogChannel = client.get_channel(817971315138756619)
    conHighChannel = client.get_channel(818066947463053312)
    studyHighChannel = client.get_channel(818066981982830613)
    if message.author.bot:
        return
    if 'sh!' in message.content or message.content.startswith('-'):
        if message.content == 'sh!':
            await message.channel.send('`sh!`はコマンドです。')
        elif 'help' in message.content:
            content = '※ [S]表記のあるものはDMでは利用不可'
            content += '\n`sh!info` idからSHIP上のファイル名や投稿日などを取得。省略形は`-i`'
            content += '\n`sh!file` idからSHIP上のファイルをダウンロードするためのリンクを返す。省略形は`-f`'
            content += '\n`sh!recently` SHIPの最近の更新を一覧表示。省略形は`-r`'
            content += '\n`sh!wiki` Wikipediaを検索'
            content += '\n`sh!nhk` NHKで現在放送している番組を取得'
            content += '\n`sh!naroulist` なろう通知チャンネルで通知する小説のリスト'
            content += '\n`sh!narouadd` なろう通知チャンネルで通知する小説の追加'
            content += '\n`sh!narouremove` なろう通知チャンネルで通知する小説の削除'
            embed = discord.Embed(title="コマンド一覧 /lastupdate: 2021-04-10",
                                  description=content, color=discord.Colour.from_rgb(190, 252, 3))
            await message.channel.send(embed=embed)
        elif 'info' in message.content or '-i' in message.content:
            flag = False
            if len(message.content.split()) == 2:
                if isint(message.content.split()[1]):
                    idIntMessage = int(message.content.split()[1])
                    flag = True
            if flag == False:
                try:
                    idMessage = ""
                    embed = discord.Embed(title="情報取得", description="情報を取得したいファイルのidを入力してください。idは通知チャンネル("+conHighChannel.mention +
                                          ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(190, 252, 3))
                    await message.channel.send(embed=embed)
                    idMessage = await client.wait_for("message", check=check, timeout=60)
                    if isint(idMessage.content) == False:
                        if 'sh!' in idMessage.content:
                            await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await idMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    idIntMessage = int(idMessage.content)
                except Exception as e:
                    if idMessage == "":
                        await message.reply("セッションがタイムアウトしました"+str(e))
                    return
            data = search.info(idIntMessage)
            if len(data) == 0:
                await message.reply("指定されたidに該当するファイルがデータベースに見つかりませんでした。")
                return
            body = "`page` "+data[0][4]+"\n"
            body += "`id` "+str(idIntMessage)+"\n"
            body += "`date` "+str(data[0][1]).replace("-", "/")+"\n"
            body += "`folder` "+data[0][2]+"\n"
            if data[0][4] == "高校連絡事項" or data[0][4] == "高校学習教材":
                linkList = str(data[0][3])[1:-1].split(",")
                body += "`file` "+str(len(linkList))+"\n"
            if data[0][4] == "高校連絡事項" or data[0][4] == "中学連絡事項":
                body += "`link` https://ship.sakae-higashi.jp/sub_window_anke/?obj_id=" + \
                    str(idIntMessage)+"&t=3\n"
            elif data[0][4] == "高校学習教材" or data[0][4] == "中学学習教材":
                body += "`link` https://ship.sakae-higashi.jp/sub_window_study/?obj_id=" + \
                    str(idIntMessage)+"&t=7\n"
            body += "※リンクはSHIPにログインした状態でのみ開けます"
            embed = discord.Embed(
                title=data[0][0], description=body, color=discord.Colour.from_rgb(190, 252, 3))
            await message.channel.send(embed=embed)
        elif 'file' in message.content or '-f' in message.content or 'download' in message.content or '-d' in message.content:
            flag = False
            if len(message.content.split()) == 2:
                if isint(message.content.split()[1]):
                    idIntMessage = int(message.content.split()[1])
                    flag = True
            if flag == False:
                try:
                    idMessage = ""
                    embed = discord.Embed(title="ファイル取得", description="ダウンロードリンクを表示したいもののidを入力してください。idは通知チャンネル("+conHighChannel.mention +
                                          ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(50, 168, 82))
                    await message.channel.send(embed=embed)
                    idMessage = await client.wait_for("message", check=check, timeout=60)
                    if isint(idMessage.content) == False:
                        if 'sh!' in idMessage.content:
                            await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await idMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    idIntMessage = int(idMessage.content)
                except Exception as e:
                    if idMessage == "":
                        await message.reply("セッションがタイムアウトしました"+str(e))
                    return
            data = search.file(idIntMessage)
            if len(data) == 0 or str(data[0][1]) == "{}":
                await message.reply("指定されたidに該当するファイルがデータベースに見つかりませんでした。idが間違っているか、中学ページのファイルの可能性があります。")
                return
            linkList = str(data[0][1])[1:-1].split(",")
            await message.channel.send("**"+str(data[0][0]+"** - "+str(data[0][2])))
            lc = 1
            for link in linkList:
                fileName = link.split(
                    '%2F')[-1].split('.pdf')[0]+"-"+str(lc)+".pdf"
                urllib.request.urlretrieve(link, fileName)
                file = discord.File(fileName, filename=fileName)
                await message.channel.send(file=file)
                lc += 1
        elif 'recently' in message.content or 'sh!r' in message.content or '-r' in message.content:
            flag = False
            if len(message.content.split()) == 3:
                if isint(message.content.split()[1]) and isint(message.content.split()[1]):
                    typeIntMessage = int(message.content.split()[1])
                    howmanyIntMessage = int(message.content.split()[2])
                    flag = True
            if flag == False:
                embed = discord.Embed(title="最近の更新の取得",
                                      description="高校連絡事項→ `1`\n高校学習教材→ `2`\n中学連絡事項→ `3`\n中学学習教材→ `4`", color=discord.Colour.from_rgb(252, 186, 3))
                await message.channel.send(embed=embed)
                try:
                    typeMessage = await client.wait_for("message", check=check, timeout=60)
                    if isint(typeMessage.content) == False:
                        if 'sh!' in typeMessage.content:
                            await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await typeMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    typeIntMessage = int(typeMessage.content)
                    data = search.count(typeIntMessage)
                    if data == 0:
                        await typeMessage.reply("指定されたタイプは存在しません。")
                        return
                    await message.channel.send(str(data)+"件のデータが見つかりました。何件表示しますか？(最大30件まで)")
                    try:
                        howmanyMessage = await client.wait_for("message", check=check, timeout=60)
                        if isint(howmanyMessage.content) == False:
                            if 'sh!' in howmanyMessage.content:
                                await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                            else:
                                await howmanyMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                            return
                        howmanyIntMessage = int(howmanyMessage.content)
                    except Exception as e:
                        await howmanyMessage.reply("セッションがタイムアウトしました"+str(e))
                        return
                except Exception as e:
                    await typeMessage.reply("セッションがタイムアウトしました"+str(e))
            mainData = search.recently(typeIntMessage, howmanyIntMessage)
            body = ""
            lc = 1
            for eachData in mainData:
                body += "`" + str(eachData[2]) + "` __**" + eachData[0] + "**__ - " + str(
                    eachData[1].strftime('%Y/%m/%d')) + "\n"
                if howmanyIntMessage == lc or lc == 30:
                    break
                lc += 1
            if body == "":
                body = "empty"
            if typeIntMessage == 1:
                titlebody = "最近の高校連絡事項"
            elif typeIntMessage == 2:
                titlebody = "最近の高校学習教材"
            elif typeIntMessage == 3:
                titlebody = "最近の中学連絡事項"
            elif typeIntMessage == 4:
                titlebody = "最近の中学学習教材"
            embed = discord.Embed(
                title=titlebody, description=body, color=discord.Colour.from_rgb(252, 186, 3))
            await message.channel.send(embed=embed)
        # Wikipedia検索
        elif 'wiki' in message.content:
            flag = False
            if len(message.content.split()) == 2:
                if isint(message.content.split()[1]):
                    word = int(message.content.split()[1])
                    flag = True
            if flag == False:
                try:
                    wordMessage = ""
                    embed = discord.Embed(
                        title="Wikipedia検索", description="検索したいワードを入力してください。")
                    await message.channel.send(embed=embed)
                    wordMessage = await client.wait_for("message", check=check, timeout=60)
                    if 'sh!' in wordMessage.content:
                        await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                        return
                    word = int(wordMessage.content)
                except Exception as e:
                    if wordMessage == "":
                        await message.reply("セッションがタイムアウトしました"+str(e))
                    return
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
            await message.channel.send('にゃーん')
            wait_message = await client.wait_for("message", check=check)
            await message.channel.send(wait_message.content)
        elif 'nhk' in message.content:
            jsonLoad = json.load(
                open('json/nhk.json', 'r', encoding="utf-8_sig"))
            jsonAreaData = jsonLoad["areas"]
            jsonChannelData = jsonLoad["channels"]
            body = ''
            idList = []
            for i in jsonAreaData:
                body += '\n`' + i['id'] + '` **'+i['title']+'**'
                idList.append(i['id'])
            flag = False
            if len(message.content.split()) == 3:
                if isint(message.content.split()[1]) and isint(message.content.split()[1]):
                    nhkAreaId = message.content.split()[1]
                    nhkChannelId = int(message.content.split()[2]) - 1
                    if nhkAreaId in idList and nhkChannelId < len(jsonChannelData):
                        nhkAreaLen = idList.index(nhkAreaId)
                        flag = True
            if flag == False:
                await message.channel.send('🗾地域を選択してください'+body)
                try:
                    nhkAreaMessage = await client.wait_for("message", check=check, timeout=60)
                    if nhkAreaMessage.content not in idList:
                        if 'sh!' in nhkAreaMessage.content:
                            await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await nhkAreaMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    nhkAreaId = nhkAreaMessage.content
                    nhkAreaLen = idList.index(nhkAreaId)
                    body = ''
                    c = 0
                    for i in jsonChannelData:
                        body += '\n`' + str(c+1) + '` **'+i['title']+'**'
                        c += 1
                    await message.channel.send('📺チャンネルを選択してください'+body)
                    try:
                        nhkChannelMessage = await client.wait_for("message", check=check, timeout=60)
                        if isint(nhkChannelMessage.content) == False:
                            if 'sh!' in nhkChannelMessage.content:
                                await message.reply("別のコマンドが実行されたためこのセッションは終了しました。")
                            else:
                                await nhkChannelMessage.reply("入力された文字は数字ではありません。最初からやり直してください。")
                            return
                        nhkChannelId = int(nhkChannelMessage.content) - 1
                        if nhkChannelId > len(jsonChannelData):
                            await nhkChannelMessage.reply("入力された数字に対応するチャンネルがありません。最初からやり直してください。")
                            return
                    except Exception as e:
                        await message.reply("セッションがタイムアウトしました"+str(e))
                except Exception as e:
                    await message.reply("セッションがタイムアウトしました"+str(e))
            response = requests.get(
                "https://api.nhk.or.jp/v2/pg/now/"+nhkAreaId+"/"+jsonChannelData[nhkChannelId]['id']+'.json?key='+os.environ['NHK_ACCESS_KEY'])
            responseJson = response.json()
            try:
                responseDataPresent = responseJson['nowonair_list'][jsonChannelData[nhkChannelId]['id']]['present']
                responseDataFollowing = responseJson['nowonair_list'][
                    jsonChannelData[nhkChannelId]['id']]['following']
                present = '`title` **'+responseDataPresent['title']+'**\n`subtitle` '+responseDataPresent['subtitle'] + \
                    '\n`start` ' + \
                    responseDataPresent['start_time']+'\n`end` ' + \
                    responseDataPresent['end_time']+'\n'
                following = '`title` **'+responseDataFollowing['title']+'**\n`subtitle` '+responseDataFollowing['subtitle'] + \
                    '\n`start` '+responseDataFollowing['start_time'] + \
                    '\n`end` '+responseDataFollowing['end_time']+'\n'
                embed = discord.Embed(title='📺'+jsonChannelData[nhkChannelId]['title'] +
                                      '('+jsonAreaData[nhkAreaLen]['title']+')', color=discord.Colour.from_rgb(50, 168, 82))
                embed.add_field(name="▶現在放送中", value=present, inline=False)
                embed.add_field(name="▶▶次に放送予定", value=following, inline=False)
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.reply("エラー"+str(e))
        elif 'naroucheck' in message.content:
            try:
                await getNarou()
                await message.channel.send('なろうの更新取得処理が完了しました')
            except Exception as e:
                await message.channel.send('【なろう】\nエラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif 'narouadd' in message.content:
            if len(message.content.split()) != 2:
                await message.channel.send('第2引数に小説のURLの末尾にあるncodeを入れてください。')
                return
            ncode = message.content.split()[1]
            resMessage = narou.add(ncode)
            if resMessage[0] == "success":
                await message.channel.send('更新通知リストに**'+resMessage[1]+'** ( '+resMessage[2] + ' ) を追加しました。')
            else:
                await message.channel.send('エラー: '+resMessage[1])
        elif 'narouremove' in message.content:
            if len(message.content.split()) != 2:
                await message.channel.send('第2引数に小説のURLの末尾にあるncodeを入れてください。')
                return
            ncode = message.content.split()[1]
            resMessage = narou.remove(ncode)
            if resMessage[0] == "success":
                await message.channel.send('更新通知リストから '+resMessage[1] + ' ) を削除しました。')
            else:
                await message.channel.send('エラー: '+resMessage[1])
        elif 'naroulist' in message.content:
            try:
                data = narou.list()
                for i in data:
                    body = ""
                    body += "**title** " + \
                        i[1]+" ( https://ncode.syosetu.com/"+i[0]+" )\n"
                    await message.channel.send(body)
            except Exception as e:
                await message.channel.send('【なろう】\nエラータイプ:' + str(type(e))+'\nエラーメッセージ:' + str(e))
        elif 'anime' in message.content:
            return
        else:
            await message.channel.send('このコマンドは用意されていません')
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
        user_count = sum(
            1 for member in guild.members if not member.bot)
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
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    user = client.get_user(payload.user_id)
    entranceMessageId = 817952115095109633
    narouRoleMessageId = 827415329223213066
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        authenticatedRole = guild.get_role(813014134001500170)
        await member.add_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.remove_roles(unauthenticatedRole)
        await roleLogChannel.send(user.mention+'に'+authenticatedRole.mention+'ロールを付与し、'+unauthenticatedRole.mention+'ロールを剥奪しました。')
        await user.send("「SHIP Info」サーバーへようこそ！このサーバーとbotでは、**SHIPの更新の通知を受け取ったり**、**コマンドからSHIP上のファイルをダウンロード**したりすることができます。何かわからないことがある場合はこのチャットやサーバーのお問い合わせチャンネルでお気軽にお尋ねください。\n\n※__このメッセージはサーバー参加時に全員に送信しています__")
        await user.send("botとのDMやコマンドチャンネルなどでは様々なコマンドを使うことができます。**例えばここで`sh!r`と送信すれば最近のSHIPの更新を一覧で確認することができます。**\nなおコマンドの一覧は`sh!help`と送信することで確認できます。ぜひお試しください。")
    elif payload.message_id == narouRoleMessageId:
        if payload.emoji.name == '1️⃣':
            narouRole = guild.get_role(827413046968320040)
            await member.add_roles(narouRole)
            await roleLogChannel.send(user.mention+'に'+narouRole.mention+'ロールを付与しました。')


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
    for msg in messages:
        if "NAROU_GET_HOUR=" in msg.content:
            whenNarouGetConfigMessage = msg.content.lstrip("NAROU_GET_HOUR=")
            continue
    narouHourList = [int(x) for x in whenNarouGetConfigMessage.split()]
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
    if nowMinute < 10:
        if nowHour in hourList:
            await getLogChannel.send('データの取得を開始します')
            try:
                await getData()
                await getLogChannel.send('処理が完了しました')
            except Exception as e:
                await getLogChannel.send('**failedToGetShipUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
            if random.randrange(10) == 0:
                try:
                    await getNewsData()
                    await getLogChannel.send('栄東ニュースの取得処理が完了しました')
                except Exception as e:
                    await getLogChannel.send('**failedToGetShnewsUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
        if nowHour in narouHourList:
            try:
                await getNarou()
                await getLogChannel.send('小説家になろうの更新取得処理が完了しました')
            except Exception as e:
                await getLogChannel.send('**failedToGetNarouUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))


async def getData():
    await client.wait_until_ready()
    conJuniorChannel = client.get_channel(812592878194262026)
    studyJuniorChannel = client.get_channel(814791146966220841)
    schoolNewsJuniorChannel = client.get_channel(841936448878018560)
    conHighChannel = client.get_channel(818066947463053312)
    studyHighChannel = client.get_channel(818066981982830613)
    schoolNewsHighChannel = client.get_channel(841936546772156426)
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
    if len(result[5]) != 0:
        for schoolNewsData in result[5]:
            try:
                if schoolNewsData[3] != '':
                    embed = discord.Embed(
                        title=schoolNewsData[3], description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(52, 229, 235))
                else:
                    embed = discord.Embed(
                        title="高校学校通信更新通知", description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(52, 229, 235))
                embed.add_field(name="id", value=schoolNewsData[0])
                if schoolNewsData[2] != '':
                    embed.add_field(name="path", value=schoolNewsData[2])
                embed.set_footer(text="取得: "+result[4])
                await schoolNewsHighChannel.send(embed=embed)
            except Exception as e:
                await schoolNewsHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校学校通信更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学校通信に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)
    if len(result[6]) != 0:
        for schoolNewsData in result[5]:
            try:
                if schoolNewsData[3] != '':
                    embed = discord.Embed(
                        title=schoolNewsData[3], description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(52, 229, 235))
                else:
                    embed = discord.Embed(
                        title="中学学校通信更新通知", description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(52, 229, 235))
                embed.add_field(name="id", value=schoolNewsData[0])
                if schoolNewsData[2] != '':
                    embed.add_field(name="path", value=schoolNewsData[2])
                embed.set_footer(text="取得: "+result[4])
                await schoolNewsJuniorChannel.send(embed=embed)
            except Exception as e:
                await schoolNewsJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学学校通信更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学校通信に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result[4])
        await getLogChannel.send(embed=embed)
    if len(result[2]) != 0 or len(result[3]) != 0:
        try:
            log = line.main(result)
            await getLogChannel.send("LINE版処理完了" + log)
        except Exception as e:
            await getLogChannel.send("LINE版での不具合:"+str(e))


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


async def getNarou():
    await client.wait_until_ready()
    narouChannel = client.get_channel(826094369467138108)
    getLogChannel = client.get_channel(817400535639916544)
    try:
        result = narou.main()
        for item in result:
            embed = discord.Embed(
                title=str(item[3]), description="更新日時:"+str(item[1])+"\n最新ページURL: https://ncode.syosetu.com/"+str(item[0])+"/"+str(item[2]), color=discord.Colour.from_rgb(66, 135, 245))
            await narouChannel.send(embed=embed)
    except Exception as e:
        await getLogChannel.send("なろう取得不具合:"+str(e))


loop.start()


client.run(TOKEN)
