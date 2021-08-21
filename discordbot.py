import datetime
import json
import os
import time
import urllib.request

import discord
import requests
import wikipedia
from discord.ext import tasks
from dotenv import load_dotenv

import line
import twitter
import narou
import search
import shipcheck
import shnews

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
    await member.send("「SHIP Info」サーバーへようこそ！このサーバーでは、SHIPの更新情報をはじめとして様々な情報を確認することができます。何かわからないことがある場合はこのチャットなどで気軽にお尋ねください。\
    \nbotとのDMやサーバー内では様々なコマンドを使うことができます。利用可能なコマンドはここで`sh!help`と送信することで確認できます。\n\n__**※このメッセージはサーバー参加時に全員に送信しています**__")


@client.event
async def on_member_remove(member):
    await client.wait_until_ready()
    joinLeaveLogChannel = client.get_channel(810813680618831906)
    await joinLeaveLogChannel.send(str(member.name)+" ( "+str(member.id)+" ) が脱退しました")


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
            content += '\n`sh!wiki` Wikipediaを検索'
            content += '\n\n> 「小説家になろう」関連コマンド'
            content += '\n`n!when` 更新を取得している日時の取得'
            content += '\n`n!add` 更新を通知する小説の追加'
            content += '\n`n!remove` 更新を通知する小説の削除'
            content += '\n`n!list` 更新を通知している小説一覧を表示'
            embed = discord.Embed(title="コマンド一覧 - lastupdate: 2021/08/16", description=content, color=discord.Colour.from_rgb(190, 252, 3))
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
                            await message.reply("❌別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await idMessage.reply("❌入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    idIntMessage = int(idMessage.content)
                except Exception as e:
                    if idMessage == "":
                        await message.reply("⏱セッションがタイムアウトしました"+str(e))
                    return
            data = search.Search().info(idIntMessage)
            if len(data) == 0:
                await message.reply("❌指定されたidに該当するファイルがデータベースに見つかりませんでした。")
                return
            body = "`page` "+data[0][4]+"\n"
            body += "`id` "+str(idIntMessage)+"\n"
            body += "`date` "+str(data[0][1]).replace("-", "/")+"\n"
            body += "`folder` "+data[0][2]+"\n"
            if "高校" in data[0][4]:
                linkList = str(data[0][3])[1:-1].split(",")
                body += "`file` "+str(len(linkList))+"\n"
            body += "`link` https://ship-assistant.web.app/post/" + str(idIntMessage)
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
                            await message.reply("❌別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await idMessage.reply("❌入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    idIntMessage = int(idMessage.content)
                except Exception as e:
                    if idMessage == "":
                        await message.reply("⏱セッションがタイムアウトしました"+str(e))
                    return
            data = search.Search().file(idIntMessage)
            if len(data) == 0:
                await message.reply("❌指定されたidに該当するファイルがデータベースに見つかりませんでした。idが間違っているか、中学ページのファイルの可能性があります。")
                return
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
                            await message.reply("❌別のコマンドが実行されたためこのセッションは終了しました。")
                        else:
                            await typeMessage.reply("❌入力された文字は数字ではありません。最初からやり直してください。")
                        return
                    typeIntMessage = int(typeMessage.content)
                    data = search.Search().count(typeIntMessage)
                    if data == 0:
                        await typeMessage.reply("❌指定されたタイプは存在しません。")
                        return
                    await message.channel.send(str(data)+"件のデータが見つかりました。何件表示しますか？(最大30件まで)")
                    try:
                        howmanyMessage = await client.wait_for("message", check=check, timeout=60)
                        if isint(howmanyMessage.content) == False:
                            if 'sh!' in howmanyMessage.content:
                                await message.reply("❌別のコマンドが実行されたためこのセッションは終了しました。")
                            else:
                                await howmanyMessage.reply("❌入力された文字は数字ではありません。最初からやり直してください。")
                            return
                        howmanyIntMessage = int(howmanyMessage.content)
                    except Exception as e:
                        await howmanyMessage.reply("⏱セッションがタイムアウトしました"+str(e))
                        return
                except Exception as e:
                    await typeMessage.reply("⏱セッションがタイムアウトしました"+str(e))
                    return
            mainData = search.Search().recently(typeIntMessage, howmanyIntMessage)
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
        elif 'role' in message.content:
            await message.channel.send('Now prepairing. Please wait...')
        # Wikipedia検索
        # https://wikipedia.readthedocs.io/en/latest/code.html#module-wikipedia.exceptions
        elif 'wiki' in message.content:
            wikipedia.set_lang("ja")
            if len(message.content.split()) == 2:
                word = message.content.split()[1]
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
        else:
            await message.channel.send('❌このコマンドは用意されていません')
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
                    start = time.time()
                    await getNewsData()
                    elapsedTime = time.time() - start
                    await message.channel.send('栄東ニュースの更新取得処理が完了しました'+str(elapsedTime)+'[sec]')
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
                    await message.channel.send("⚠️このチャンネルのメッセージをすべて削除します。本当によろしいですか？")
                    agreeMessage = await client.wait_for("message", check=check, timeout=10)
                    if agreeMessage.content == "yes" and agreeMessage.author.guild_permissions.administrator:
                        await agreeMessage.channel.purge(limit=None)
                        await agreeMessage.channel.send("削除が完了しました。")
                except:
                    await message.channel.send("操作が中断されました")
            elif 'sa!delete-some-message' in message.content:
                if len(message.content.split()) == 2:
                    if isint(message.content.split()[1]):
                        try:
                            await message.reply("⚠️これより"+str(int(message.content.split()[1]))+"件前までのメッセージを削除します。よろしいですか？")
                            agreeMessage = await client.wait_for("message", check=check, timeout=10)
                            if agreeMessage.content == "yes" and agreeMessage.author.guild_permissions.administrator:
                                await agreeMessage.channel.purge(limit=int(message.content.split()[1])+3)
                                await agreeMessage.channel.send(str(message.content.split()[1])+"件のメッセージの削除が完了しました。")
                        except:
                            await message.reply("操作が中断されました")
        else:
            await message.channel.send('⚠️このコマンドは管理者のみ利用可能です')
    if 'n!' in message.content:
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
        if 'n!add' in message.content:
            if len(message.content.split()) == 2:
                ncode = message.content.split()[1]
                if len(ncode) == 7 and ncode[0] == 'n':
                    result = narou.add(ncode)
                    if result == "add":
                        await message.channel.send("このチャンネルで https://ncode.syosetu.com/"+ncode+" の小説の更新を通知します")
                    elif result == "already":
                        await message.channel.send("https://ncode.syosetu.com/"+ncode+" の小説はすでにフォローされています")
                    else:
                        await message.channel.send(result)
                else:
                    await message.channel.send("これはncodeではありません。最初からやり直してください")
            else:
                await message.channel.send("第2引数にncodeを指定してください。\n例) https://ncode.syosetu.com/n2267be のncode → n2267be")
        elif 'n!remove' in message.content:
            if len(message.content.split()) == 2:
                ncode = message.content.split()[1]
                if len(ncode) == 7 and ncode[0] == 'n':
                    result = narou.remove(ncode)
                    if result == "remove":
                        await message.channel.send("このチャンネルで https://ncode.syosetu.com/"+ncode+" の小説の更新通知を解除します")
                    else:
                        await message.channel.send("この小説はまだフォローされていないか、存在しません"+result)
                else:
                    await message.channel.send("これはncodeではありません。最初からやり直してください")
            else:
                await message.channel.send("第2引数にncodeを指定してください。\n例) https://ncode.syosetu.com/n2267be のncode → n2267be")
        elif 'n!list' in message.content:
            result = narou.list()
            body = ""
            for eachData in result:
                body += "`title` "+eachData['title']+" ( https://ncode.syosetu.com/" + eachData['ncode'] + " )\n"
            if body == "":
                await message.channel.send("このチャンネルでフォローされている小説はありません")
            else:
                await message.channel.send(body)
    if isinstance(message.channel, discord.DMChannel):
        userId = str(message.author.id)
        embed = discord.Embed(title="DMを受信しました", color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
        embed.add_field(name="user",
                        value=message.author.mention+" ("+userId+")", inline=False)
        embed.add_field(name="body",
                        value=message.content, inline=False)
        embed.add_field(name="channelId",
                        value=str(message.channel.id), inline=False)
        await dmLogChannel.send(embed=embed)
    if message.channel == dmLogChannel and message.author.guild_permissions.administrator and 'sa!reply' in message.content:
        replyDmChannel = client.get_channel(int(message.content.split()[1]))
        sendMessage = str(message.content.split()[2])
        await replyDmChannel.send(sendMessage)
    if "https://discord.com/channels/" in message.content:
        messageChannel = message.content.split("/")[-2]
        messageId = message.content.split("/")[-1]
        oldchannel = client.get_channel(int(messageChannel))
        oldmessage = await oldchannel.fetch_message(int(messageId))
        userId = str(oldmessage.author.id)
        if oldmessage.content != "":
            embed = discord.Embed(timestamp=oldmessage.created_at,description=oldmessage.content,color=discord.Colour.from_rgb(256-int(userId[0:1])*2, 256-int(userId[2:4])*2, 256-int(userId[5:6])*2))
            embed.set_author(name=oldmessage.author.name, icon_url=oldmessage.author.avatar_url)
            embed.set_footer(text=oldchannel.name+"チャンネルでのメッセージ")
            await message.channel.send(embed=embed)
        elif oldmessage.embeds:
            await message.channel.send(content=str(oldmessage.created_at)[:19]+"に"+oldchannel.name+"チャンネルで"+oldmessage.author.mention+"が送信したEmbedメッセージ", embed=oldmessage.embeds[0])

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
        body = "現在は毎日"+str(hourList) + "時ごろに取得しています。データを取得するタイミングは変更する場合があります。"
        embed = discord.Embed(title="SHIPデータを取得するタイミング", description=body, color=discord.Colour.from_rgb(245, 236, 66))
        embed.set_footer(text="更新日時: " + str(announceMessage.edited_at.strftime("%Y/%m/%d %H:%M:%S")))
        await announceMessage.edit(embed=embed)
    nowHour = int(datetime.datetime.now().strftime("%H"))
    nowMinute = int(datetime.datetime.now().strftime("%M"))
    if nowMinute < 10:
        if nowHour in hourList:
            game = discord.Game("Getting SHIP data...")
            await client.change_presence(status=discord.Status.dnd, activity=game)
            await getLogChannel.send('SHIPデータの取得を開始します')
            try:
                start = time.time()
                await getData()
                elapsedTime = time.time() - start
                await getLogChannel.send('SHIPデータ取得処理が完了しました。'+str(elapsedTime)+'[sec]')
            except Exception as e:
                await getLogChannel.send('**failedToGetShipUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
            try:
                start = time.time()
                await getNewsData()
                elapsedTime = time.time() - start
                await getLogChannel.send('栄東ニュースの更新取得処理が完了しました。'+str(elapsedTime)+'[sec]')
            except Exception as e:
                await getLogChannel.send('**failedToGetShnewsUpdate**\n[errorType]' + str(type(e))+'\n[errorMessage]' + str(e))
            game = discord.Game("commands: sh!help")
            await client.change_presence(status=discord.Status.online, activity=game)
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
    getLogChannel = client.get_channel(817400535639916544)
    configChannel = client.get_channel(820242721330561044)
    messages = await configChannel.history().flatten()
    for msg in messages:
        if "DISCORD_NOTIFY=" in msg.content:
            discordNotifyBool = msg.content.lstrip("DISCORD_NOTIFY=")
            continue
    result = shipcheck.main()
    itemNameList = json.load(open('json/ship.json', 'r', encoding="utf-8_sig"))["pageList"]
    noneUpdateChannelList = []
    updateList = []
    for eachName in itemNameList:
        if len(result[eachName["collectionName"]]) != 0:
            if discordNotifyBool == "true":
                sendChannel = client.get_channel(eachName["channelId"])
                c = eachName["color"]
                for conData in result[eachName["collectionName"]]:
                    try:
                        if conData['title'] != '':
                            embed = discord.Embed(
                                title=conData['title'], description="投稿: "+conData['date'], color=discord.Colour.from_rgb(c[0], c[1], c[2]))
                        else:
                            embed = discord.Embed(
                                title=eachName["name"]+"更新通知", description="投稿: "+conData['date'], color=discord.Colour.from_rgb(c[0], c[1], c[2]))
                        embed.add_field(name="id", value=conData['id'][0])
                        if conData['folder'] != '':
                            embed.add_field(name="path", value=conData['folder'])
                        if "description" in eachName["props"]:
                            if conData['description'] != '':
                                embed.add_field(name="description",
                                                value=conData['description'], inline=False)
                        embed.set_footer(text="取得: "+result['getTime'])
                        await sendChannel.send(embed=embed)
                    except Exception as e:
                        await sendChannel.send(str(e))
            else:
                await getLogChannel.send(eachName["collectionName"]+"に更新がありましたが、discordNotifyBoolの設定によりLINE版には更新が通知されませんでした")
            updateList.append(eachName["name"])
        else:
            noneUpdateChannelList.append(eachName["name"])
    if len(noneUpdateChannelList) != 0:
        body = result['getTime'] + "の取得で以下のチャンネルに更新がありませんでした。\n" + str(noneUpdateChannelList)
        embed = discord.Embed(
            title="未更新チャンネル", description=body, color=discord.Colour.from_rgb(52, 235, 79))
        await getLogChannel.send(embed=embed)
    if len(result['highCon']) != 0 or len(result['highStudy']) != 0:
        messages = await configChannel.history().flatten()
        for msg in messages:
            if "LINE_NOTIFY=" in msg.content:
                lineNotifyBool = msg.content.lstrip("LINE_NOTIFY=")
                continue
        if lineNotifyBool == "true":
            try:
                log = line.main(result)
                await getLogChannel.send("LINE版処理完了\n" + log)
            except Exception as e:
                await getLogChannel.send("LINE版での不具合:\n" + str(e))
        else:
            await getLogChannel.send("highCon,highStudyのいずれかに更新がありましたが、lineNotifyBoolの設定によりLINE版には更新が通知されませんでした")
    if result["logId"] != "":
        try:
            tweetUrl = twitter.main(result['logId'], updateList)
            await getLogChannel.send("twitter版処理完了\n" + tweetUrl)
        except Exception as e:
            await getLogChannel.send("twitter版不具合:\n" + str(e))


async def getNewsData():
    await client.wait_until_ready()
    shnewsChannel = client.get_channel(818480374334226443)
    getLogChannel = client.get_channel(817400535639916544)
    result = shnews.main()
    if len(result["newsData"]) != 0:
        for conData in result["newsData"]:
            embed = discord.Embed(
                title=conData["title"], description="投稿日時: "+conData["postDateTime"], color=discord.Colour.from_rgb(230, 32, 226))
            embed.add_field(name="category", value=conData["category"])
            embed.add_field(name="body", value=conData["body"], inline=False)
            if len(conData["images"]) != 0:
                embed.set_image(url=conData["images"][0])
            embed.add_field(name="link", value=conData["link"], inline=False)
            embed.set_footer(text="取得: "+result["getTime"])
            await shnewsChannel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="栄東ニュース更新通知", color=discord.Colour.from_rgb(230, 32, 226))
        embed.add_field(name="system-log",
                        value='栄東ニュースに更新はありませんでした')
        embed.set_footer(text="取得: "+result["getTime"])
        await getLogChannel.send(embed=embed)

async def getNarouData():
    await client.wait_until_ready()
    sendChannel = client.get_channel(826094369467138108)
    result = narou.main()
    if len(result) != 0:
        for eachData in result:
            embed = discord.Embed(title=eachData['title'], description="投稿: "+eachData['lastup']+"\nリンク: https://ncode.syosetu.com/"+eachData['ncode']+"/"+str(eachData['count']), color=discord.Colour.from_rgb(256-int(eachData['ncode'][1:2])*2, 256-int(eachData['ncode'][2:3])*2, 256-int(eachData['ncode'][3:4])*2))
            await sendChannel.send(embed=embed)

async def getWeather():
    await client.wait_until_ready()
    weatherChannel = client.get_channel(855709750704209921)
    response = requests.get("https://www.jma.go.jp/bosai/forecast/data/forecast/110000.json").json()[0]
    pops = response['timeSeries'][1]['areas'][1]['pops']
    timeDefines = response['timeSeries'][1]['timeDefines']
    title = "埼玉県南部の天気 - " + response['reportDatetime'][8:13].replace("T","日") + "時発表\n"
    day1 = response['timeSeries'][0]['areas'][1]['weathers'][0].replace("晴れ", "🌞晴れ").replace("くもり","☁くもり").replace("雨","☔雨").replace("雷", "⚡雷")
    day2 = response['timeSeries'][0]['areas'][1]['weathers'][1].replace("晴れ", "🌞晴れ").replace("くもり","☁くもり").replace("雨","☔雨").replace("雷", "⚡雷")
    body = "`" + response['timeSeries'][0]['timeDefines'][0][8:10] + "日:` `" + day1 + "`\n`" + response['timeSeries'][0]['timeDefines'][1][8:10] + "日:` `" + day2 + "`\n> 降水確率\n"
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
