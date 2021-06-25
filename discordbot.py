import datetime
import json
import os
import random
import time

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

@client.event
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
            content = '`sh!info` idからSHIP上のファイル名や投稿日などを取得。省略形は`-i`'
            content += '\n`sh!file` idからSHIP上のファイルをダウンロードするためのリンクを返す。省略形は`-f`'
            content += '\n`sh!recently` SHIPの最近の更新を一覧表示。省略形は`-r`'
            content += '\n`sh!when` SHIPの更新を取得する日時を表示'
            content += '\n`sh!wiki` Wikipediaを検索'
            content += '\n`sh!nhk` NHKで現在放送している番組を取得'
            content += '\n\n＜「小説家になろう」関連コマンド＞ ※DMチャンネルでのみ利用可能'
            content += '\n`n!when` 更新を取得している日時の取得'
            content += '\n`n!add` 更新を通知する小説の追加'
            content += '\n`n!remove` 更新を通知する小説の削除'
            content += '\n`n!list` 更新を通知している小説一覧を表示'
            embed = discord.Embed(title="コマンド一覧 - lastupdate: 2021/06/19", description=content, color=discord.Colour.from_rgb(190, 252, 3))
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
                    embed = discord.Embed(title="情報取得", description="情報を取得したいファイルのidを入力してください。idは通知チャンネル(" + conHighChannel.mention + ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(190, 252, 3))
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
            if data[0][4] == "高校連絡事項" or data[0][4] == "高校学習教材" or data[0][4] == "高校学校通信":
                linkList = str(data[0][3])[1:-1].split(",")
                body += "`file` "+str(len(linkList))+"\n"
            if data[0][4] == "高校連絡事項" or data[0][4] == "中学連絡事項":
                body += "`link` https://ship.sakae-higashi.jp/sub_window_anke/?obj_id=" + \
                    str(idIntMessage)+"&t=3\n"
            elif data[0][4] == "高校学習教材" or data[0][4] == "中学学習教材":
                body += "`link` https://ship.sakae-higashi.jp/sub_window_study/?obj_id=" + \
                    str(idIntMessage)+"&t=7\n"
            elif data[0][4] == "高校学校通信" or data[0][4] == "中学学校通信":
                body += "`link` https://ship.sakae-higashi.jp/sub_window/?obj_id="+str(idIntMessage)+"&t=7\n"
                body += "`original id` "+ data[0][5] + "\n"
            body += "\n※リンクはSHIPにログインした状態でのみ開けます"
            embed = discord.Embed(
                title=data[0][0], description=body, color=discord.Colour.from_rgb(190, 252, 3))
            await message.channel.send(embed=embed)
        elif 'file' in message.content or '-f' in message.content:
            flag = False
            if len(message.content.split()) == 2:
                if isint(message.content.split()[1]):
                    idIntMessage = int(message.content.split()[1])
                    flag = True
            if flag == False:
                try:
                    idMessage = ""
                    embed = discord.Embed(title="ファイル取得", description="ダウンロードリンクを表示したいもののidを入力してください。idは通知チャンネル(" + conHighChannel.mention + ","+studyHighChannel.mention+")または`sh!recently`コマンドなどから確認できます。", color=discord.Colour.from_rgb(50, 168, 82))
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
            if str(data[0][1]).startswith('{'):
                linkList = str(data[0][1])[1:-1].split(",")
            else:
                linkList = data[0][1]
            await message.channel.send("**"+str(data[0][0]+"** - "+str(data[0][2])))
            for lc, link in enumerate(linkList, 1):
                fileName = link.split(
                    '%2F')[-1].split('.pdf')[0]+"-"+str(lc)+".pdf"
                urllib.request.urlretrieve(link, fileName)
                file = discord.File(fileName, filename=fileName)
                await message.channel.send(file=file)
        elif 'recently' in message.content or 'sh!r' in message.content or '-r' in message.content:
            itemNameList = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))["pageList"]
            flag = False
            if len(message.content.split()) == 3:
                if isint(message.content.split()[1]) and isint(message.content.split()[1]):
                    typeIntMessage = int(message.content.split()[1])
                    howmanyIntMessage = int(message.content.split()[2])
                    flag = True
            if flag == False:
                description = ""
                for i, eachName in enumerate(itemNameList):
                    description += "`" + str(i) + "` " + eachName["name"] + "\n"
                embed = discord.Embed(title="最近の更新の取得", description=description, color=discord.Colour.from_rgb(252, 186, 3))
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
                    return
            mainData = search.recently(typeIntMessage, howmanyIntMessage)
            body = ""
            for lc, eachData in enumerate(mainData, 1):
                try:
                    body += "`" + str(eachData['id']) + "` __**" + eachData['title'] + "**__ - " + str(eachData['date'].strftime('%Y/%m/%d')) + "\n"
                except:
                    body += "`" + str(eachData['id']) + "` __**" + eachData['title'] + "**__ - " + str(eachData['date']) + "\n"
                if howmanyIntMessage == lc or lc == 30:
                    break
            if body == "":
                body = "empty"
            embed = discord.Embed(
                title="最近の"+itemNameList[typeIntMessage]["name"], description=body, color=discord.Colour.from_rgb(252, 186, 3))
            await message.channel.send(embed=embed)
        # Wikipedia検索
        # https://wikipedia.readthedocs.io/en/latest/code.html#module-wikipedia.exceptions
        elif 'wiki' in message.content:
            wikipedia.set_lang("ja")
            flag = False
            if len(message.content.split()) == 2:
                word = message.content.split()[1]
                flag = True
            if flag == True:
                await message.channel.send('🔍Wikipediaで`'+word+'`を検索中...')
                response = wikipedia.search(word)
                if not response:
                    await message.channel.send('❌Wikipediaで`'+word+'`に関連するページが見つかりませんでした')
            else:
                response = wikipedia.random()
            try:
                page = wikipedia.page(response[0])
                content = page.content.splitlines()[0]
                if len(content) > 1000:
                    content = content[0:1000] + "..."
                body = content.splitlines()[0] + "\n\n> リンク\n" + '['+page.url+']('+page.url+')'
                embed = discord.Embed(title=page.title, description=body, color=discord.Colour.from_rgb(255, 255, 255))
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send("❌エラー:"+str(e))
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
                    for c, eachData in enumerate(jsonChannelData, 1):
                        body += '\n`' + str(c+1) + '` **'+i['title']+'**'
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
        elif 'when' in message.content:
            configChannel = client.get_channel(820242721330561044)
            messages = await configChannel.history().flatten()
            for msg in messages:
                if "GET_HOUR=" in msg.content:
                    whenGetConfigMessage = msg.content.lstrip("GET_HOUR=")
                    continue
            hourList = [int(x) for x in whenGetConfigMessage.split()]
            await message.channel.send('現在毎日'+str(hourList)+'時にSHIPデータを取得しています')
        else:
            await message.channel.send('このコマンドは用意されていません')
    if 'sa!' in message.content:
        if message.author.guild_permissions.administrator:
            if message.content == 'sa!get':
                await message.channel.send('SHIPデータの取得を開始します')
                try:
                    start = time.time()
                    await getData()
                    elapsedTime = time.time() - start
                    await message.channel.send('SHIP更新取得処理が完了しました。'+str(elapsedTime)+'[sec]')
                except Exception as e:
                    await message.channel.send(str(type(e)) + str(e))
            elif message.content == 'sa!shnews':
                await message.channel.send('栄東ニュース更新取得処理を開始します')
                try:
                    await getNewsData()
                    await message.channel.send('栄東ニュース更新取得処理が完了しました')
                except Exception as e:
                    await message.channel.send(str(type(e)) + str(e))
            elif message.content == 'sa!narou':
                try:
                    await getNarouData()
                    await message.channel.send('小説家になろう更新取得処理が完了しました')
                except Exception as e:
                    await message.channel.send(str(type(e)) + str(e))
            elif message.content == 'sa!weather':
                try:
                    await getWeather()
                except Exception as e:
                    await message.channel.send(str(type(e)) + str(e))
            elif message.content == 'sa!delete-all-message':
                try:
                    await message.channel.send("このチャンネルのメッセージをすべて削除します。本当によろしいですか？")
                    agreeMessage = await client.wait_for("message", check=check, timeout=10)
                    if agreeMessage.content == "yes" and agreeMessage.author.guild_permissions.administrator:
                        await message.channel.purge(limit=None)
                except:
                    await message.channel.send("操作が中断されました")
        else:
            await message.channel.send('このコマンドは管理者のみ利用可能です')
    if isinstance(message.channel, discord.DMChannel):
        userId = str(message.author.id)
        embed = discord.Embed(title="DMを受信しました", color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
        embed.add_field(name="ユーザー名",
                        value=message.author.mention+" ("+userId+")", inline=False)
        embed.add_field(name="本文",
                        value=message.content, inline=False)
        embed.add_field(name="チャンネルID",
                        value=str(message.channel.id), inline=False)
        await dmLogChannel.send(embed=embed)
        if 'n!when' in message.content:
            configChannel = client.get_channel(820242721330561044)
            messages = await configChannel.history().flatten()
            whenGetNarouConfigMessage = ""
            for msg in messages:
                if "GET_NAROU_HOUR=" in msg.content:
                    whenGetNarouConfigMessage = msg.content.lstrip("GET_NAROU_HOUR=")
                    continue
            hourList = [int(x) for x in whenGetNarouConfigMessage.split()]
            await message.channel.send('現在毎日'+str(hourList)+'時に「小説家になろう」の更新を取得しています。')
        elif 'n!add' in message.content:
            if len(message.content.split()) == 2:
                ncode = message.content.split()[1]
                if len(ncode) == 7 and ncode[0] == 'n':
                    result = narou.add(ncode, message.channel.id)
                    if result == "success":
                        await message.channel.send("このチャンネルで https://ncode.syosetu.com/"+ncode+" の小説の更新を通知します")
                    else:
                        await message.channel.send("https://ncode.syosetu.com/"+ncode+" の小説は存在しません"+result)
                else:
                    await message.channel.send("これはncodeではありません。")
            else:
                await message.channel.send("第2引数にncodeを指定してください。\n例) https://ncode.syosetu.com/n2267be のncode → n2267be")
        elif 'n!remove' in message.content:
            if len(message.content.split()) == 2:
                ncode = message.content.split()[1]
                if len(ncode) == 7 and ncode[0] == 'n':
                    result = narou.remove(ncode, message.channel.id)
                    if result == "success":
                        await message.channel.send("このチャンネルで https://ncode.syosetu.com/"+ncode+" の小説の更新通知を解除します")
                    else:
                        await message.channel.send("この小説はまだフォローされていないか、存在しません"+result)
                else:
                    await message.channel.send("これはncodeではありません。")
            else:
                await message.channel.send("第2引数にncodeを指定してください。\n例) https://ncode.syosetu.com/n2267be のncode → n2267be")
        elif 'n!list' in message.content:
            result = narou.list(message.channel.id)
            body = ""
            for eachData in result:
                body += "`title` "+eachData['title']+" ( https://ncode.syosetu.com/" + eachData['ncode'] + " )\n"
            if body == "":
                await message.channel.send("このチャンネルでフォローされている小説はありません")
            else:
                await message.channel.send(body)
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
            userId = str(oldmessage.author.id)
            if len(oldmessage.attachments) != 0:
                if oldmessage.content == "":
                    body = oldmessage.attachments[0].filename
                else:
                    body = oldmessage.content+"," + \
                        oldmessage.attachments[0].filename
                embed = discord.Embed(timestamp=oldmessage.created_at,description=body,color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
                embed.set_image(url=str(oldmessage.attachments[0].url))
            elif oldmessage.content != "":
                embed = discord.Embed(timestamp=oldmessage.created_at,description=oldmessage.content,color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
            elif oldmessage.embeds:
                embed = discord.Embed(timestamp=oldmessage.created_at,description="リッチメッセージ",color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
            else:
                embed = discord.Embed(timestamp=oldmessage.created_at,description="システムメッセージ",color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
        embed.set_author(name=oldmessage.author.name, icon_url=oldmessage.author.avatar_url)
        embed.set_footer(text=oldchannel.name+"チャンネルでのメッセージ")
        await message.channel.send(embed=embed)


@client.event
async def on_raw_reaction_add(payload):
    await client.wait_until_ready()
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    user = client.get_user(payload.user_id)
    entranceMessageId = 817952115095109633
    roleLogChannel = client.get_channel(817401458244714506)
    if payload.message_id == entranceMessageId:
        authenticatedRole = guild.get_role(813014134001500170)
        await member.add_roles(authenticatedRole)
        unauthenticatedRole = guild.get_role(813015195881570334)
        await member.remove_roles(unauthenticatedRole)
        await roleLogChannel.send(user.mention+'に'+authenticatedRole.mention+'ロールを付与しました。')
        await user.send("「SHIP Info」サーバーへようこそ！このサーバーとbotでは、**SHIPの更新の通知を受け取ったり**、**コマンドからSHIP上のファイルをダウンロード**したりすることができます。何かわからないことがある場合はこのチャットやサーバーのお問い合わせチャンネルでお気軽にお尋ねください。\n\n※__このメッセージはサーバー参加時に全員に送信しています__\n")
        await user.send("botとのDMやコマンドチャンネルなどでは様々なコマンドを使うことができます。**例えばここで`sh!r`と送信すれば最近のSHIPの更新を一覧で確認することができます。**\nなおコマンドの一覧は`sh!help`と送信することで確認できます。ぜひお試しください。")


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
    whenNarouGetConfigMessage = ""
    for msg in messages:
        if "GET_NAROU_HOUR=" in msg.content:
            whenNarouGetConfigMessage = msg.content.lstrip("GET_NAROU_HOUR=")
            continue
    narouHourList = [int(x) for x in whenNarouGetConfigMessage.split()]
    announceMessage = await ruleChannel.fetch_message(821736777391538206)
    if str(hourList) not in str(announceMessage.embeds[0].to_dict()):
        editDatetime = "更新日時: " + str(announceMessage.edited_at.strftime("%Y/%m/%d %H:%M:%S"))
        editedBody = "現在は"+str(hourList) + "時ごろに取得しています。データを取得するタイミングは変更する場合があります。"
        embed = discord.Embed(title="データ取得タイミング", description=editDatetime, color=discord.Colour.from_rgb(245, 236, 66))
        embed.add_field(name="SHIPデータを取得する時間", value=editedBody, inline=False)
        await announceMessage.edit(embed=embed)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    nowMinute = int(datetime.datetime.now().strftime("%M"))
    if nowMinute < 10:
        if nowHour in hourList:
            await getLogChannel.send('SHIPデータの取得を開始します')
            try:
                start = time.time()
                await getData()
                elapsedTime = time.time() - start
                await getLogChannel.send('SHIPデータ取得処理が完了しました。'+str(elapsedTime)+'[sec]')
            except Exception as e:
                await getLogChannel.send('**failedToGetShipUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
            if random.randrange(10) == 0:
                try:
                    await getNewsData()
                    await getLogChannel.send('栄東ニュースの更新取得処理が完了しました')
                except Exception as e:
                    await getLogChannel.send('**failedToGetShnewsUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
        if nowHour in narouHourList:
            try:
                await getNarouData()
                await getLogChannel.send('小説家になろうの更新取得処理が完了しました')
            except Exception as e:
                await getLogChannel.send('**failedToGetNarouUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
        if nowHour == 5:
            try:
                await getWeather()
            except Exception as e:
                await getLogChannel.send('**failedToGetWeather**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))


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
    if len(result['juniorCon']) != 0:
        for conData in result['juniorCon']:
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
                embed.set_footer(text="取得: "+result['getTime'])
                await conJuniorChannel.send(embed=embed)
            except Exception as e:
                await conJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学連絡事項更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log", value='中学連絡事項に更新はありませんでした')
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['juniorStudy']) != 0:
        for studyData in result['juniorStudy']:
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
                embed.set_footer(text="取得: "+result['getTime'])
                await studyJuniorChannel.send(embed=embed)
            except Exception as e:
                await studyJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学学習教材更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学習教材に更新はありませんでした')
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['juniorSchoolNews']) != 0:
        for schoolNewsData in result['juniorSchoolNews']:
            try:
                if schoolNewsData[3] != '':
                    embed = discord.Embed(
                        title=schoolNewsData[3], description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(242, 245, 66))
                else:
                    embed = discord.Embed(
                        title="中学学校通信更新通知", description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(242, 245, 66))
                embed.add_field(name="id", value=schoolNewsData[0])
                if schoolNewsData[2] != '':
                    embed.add_field(name="path", value=schoolNewsData[2])
                embed.set_footer(text="取得: "+result['getTime'])
                await schoolNewsJuniorChannel.send(embed=embed)
            except Exception as e:
                await schoolNewsJuniorChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="中学学校通信更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='中学学校通信に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['highCon']) != 0:
        for conData in result['highCon']:
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
                embed.set_footer(text="取得: "+result['getTime'])
                await conHighChannel.send(embed=embed)
            except Exception as e:
                await conHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校連絡事項更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校連絡事項に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['highStudy']) != 0:
        for studyData in result['highStudy']:
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
                embed.set_footer(text="取得: "+result['getTime'])
                await studyHighChannel.send(embed=embed)
            except Exception as e:
                await studyHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校学習教材更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学習教材に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['highSchoolNews']) != 0:
        for schoolNewsData in result['highSchoolNews']:
            try:
                if schoolNewsData[3] != '':
                    embed = discord.Embed(
                        title=schoolNewsData[3], description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(242, 245, 66))
                else:
                    embed = discord.Embed(
                        title="高校学校通信更新通知", description="投稿: "+schoolNewsData[1], color=discord.Colour.from_rgb(242, 245, 66))
                embed.add_field(name="id", value=schoolNewsData[0])
                if schoolNewsData[2] != '':
                    embed.add_field(name="path", value=schoolNewsData[2])
                embed.set_footer(text="取得: "+result['getTime'])
                await schoolNewsHighChannel.send(embed=embed)
            except Exception as e:
                await schoolNewsHighChannel.send(str(e))
    else:
        embed = discord.Embed(
            title="高校学校通信更新通知", color=discord.Colour.from_rgb(52, 235, 79))
        embed.add_field(name="system-log",
                        value='高校学校通信に更新はありませんでした', inline=False)
        embed.set_footer(text="取得: "+result['getTime'])
        await getLogChannel.send(embed=embed)
    if len(result['highCon']) != 0 or len(result['highStudy']) != 0:
        try:
            log = line.main(result)
            await getLogChannel.send("LINE版処理完了\n" + log)
        except Exception as e:
            await getLogChannel.send("LINE版での不具合:\n" + str(e))


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

async def getNarouData():
    await client.wait_until_ready()
    result = narou.main()
    if len(result) != 0:
        for eachData in result:
            embed = discord.Embed(title=eachData['title'], description="投稿: "+eachData['lastup']+"\nリンク: https://ncode.syosetu.com/"+eachData['ncode']+"/"+str(eachData['count']), color=discord.Colour.from_rgb(256-int(eachData['ncode'][1:2])*2, 256-int(eachData['ncode'][2:3])*2, 256-int(eachData['ncode'][3:4])*2))
            for channel in eachData['channels']:
                sendChannel = client.get_channel(int(channel))
                await sendChannel.send(embed=embed)

async def getWeather():
    await client.wait_until_ready()
    weatherChannel = client.get_channel(855709750704209921)
    url = "https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json"
    response = requests.get(url).json()[0]
    pops = response['timeSeries'][1]['areas'][1]['pops']
    timeDefines = response['timeSeries'][1]['timeDefines']
    title = "埼玉県南部の天気 - " + response['reportDatetime'][8:13].replace("T","日") + "時発表\n"
    day1 = response['timeSeries'][0]['areas'][1]['weathers'][0].replace("晴れ", "🌞晴れ").replace("くもり","☁くもり").replace("雨","☔雨").replace("雷", "⚡雷")
    day2 = response['timeSeries'][0]['areas'][1]['weathers'][1].replace("晴れ", "🌞晴れ").replace("くもり","☁くもり").replace("雨","☔雨").replace("雷", "⚡雷")
    body = "`" + response['timeSeries'][0]['timeDefines'][0][8:10] + "日:` " + day1 + "\n`" + response['timeSeries'][0]['timeDefines'][1][8:10] + "日:` " + day2 + "\n> 降水確率\n"
    for (pop, timeDefine) in zip(pops, timeDefines):
        icon = "🌧"*(int(pop)//10)+"➖"*(10-int(pop)//10)
        body += "`" + timeDefine[8:13].replace("T","日") + "時` " + icon + pop + "%\n"
    response = requests.get("https://www.jma.go.jp/bosai/forecast/data/overview_forecast/110000.json").json()
    if response['headlineText'] != "":
        body += "> 埼玉県の天気概況\n" + response['headlineText'] + "\n"
    embed = discord.Embed(title=title, description=body, color=discord.Colour.from_rgb(163, 212, 255))
    await weatherChannel.send(embed=embed)


loop.start()


client.run(TOKEN)
